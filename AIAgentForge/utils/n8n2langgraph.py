# requirements: langgraph>=0.2, langchain>=0.2, langchain-openai>=0.2, requests>=2
import os, re, json, hashlib, requests
from typing import Any, Dict, List, Callable
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# ---------- 유틸 ----------
def snake_env(name: str) -> str:
    base = re.sub(r"[^A-Za-z0-9]+", "_", name).upper().strip("_")
    return base or "HTTP_TOOL"

def strip_n8n_expr(v: str) -> str:
    if not isinstance(v, str):
        return v
    # {{$fromAI(...)}}, {{ ... }} 등 제거
    v = re.sub(r"\{\{.*?\}\}", "", v).strip()
    return v

# ---------- httpRequestTool → LangChain Tool 팩토리 ----------
def build_http_tool(node: Dict[str, Any]) -> Callable:
    name = node.get("name") or f"http_tool_{node.get('id')[:6]}"
    desc = node.get("parameters", {}).get("toolDescription") or "HTTP request tool"
    url = node.get("parameters", {}).get("url")
    method = node.get("parameters", {}).get("options", {}).get("method", "GET")
    qp = node.get("parameters", {}).get("queryParameters", {}).get("parameters", []) or []

    # n8n 쿼리 파라미터를 고정값/비밀값/질의어로 구분
    fixed_params: Dict[str, str] = {}
    key_env_map: Dict[str, str] = {}
    q_param_name = None
    for p in qp:
        k = p.get("name")
        val = strip_n8n_expr(p.get("value"))
        if k is None:
            continue
        if k.lower() in {"q", "query"}:
            q_param_name = k
            continue
        # 키나 토큰이면 ENV로 치환
        if any(t in k.lower() for t in ["key", "token", "secret", "apikey", "api_key"]):
            env = f"{snake_env(name)}_{k.upper()}"
            key_env_map[k] = env
        else:
            fixed_params[k] = val

    # LangChain @tool 생성
    tool_name = re.sub(r"[^A-Za-z0-9_]", "_", name.strip()).lower() or "http_tool"

    @tool(tool_name, return_direct=False)
    def _tool(query: str) -> str:
        """{}""".format(desc)
        if not url:
            return "No URL configured."
        params = dict(fixed_params)
        if q_param_name:
            params[q_param_name] = query
        # ENV 치환
        for k, env in key_env_map.items():
            v = os.getenv(env)
            if not v:
                return f"Missing env: {env}"
            params[k] = v
        try:
            r = requests.request(method.upper(), url, params=params, timeout=30)
            data = r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text
        except Exception as e:
            return f"HTTP error: {e}"
        # 간단 요약
        if isinstance(data, dict) and "items" in data:
            items = data.get("items") or []
            top = [f"- {i.get('title')}\n  {i.get('link')}" for i in items[:5] if isinstance(i, dict)]
            return "Top results:\n" + ("\n".join(top) if top else "No results")
        return str(data)[:4000]
    _tool.__doc__ = desc
    return _tool

# ---------- OpenAI LLM 노드 파싱 ----------
def build_llm(model_node: Dict[str, Any]) -> ChatOpenAI:
    model_cfg = model_node.get("parameters", {}).get("model", {})
    model = model_cfg.get("value") or model_cfg.get("model") or "gpt-4.1-mini"
    # 온도 등 옵션 확장 여지
    return ChatOpenAI(model=model)

# ---------- 그래프 빌더 ----------
def build_langgraph_from_n8n(workflow: Dict[str, Any]):
    nodes = workflow.get("nodes", [])
    conns = workflow.get("connections", {})

    # 노드 인덱스
    by_name = {n.get("name"): n for n in nodes}
    by_id = {n.get("id"): n for n in nodes}

    # 모델 노드
    llm_node = next((n for n in nodes if n.get("type", "").endswith(".lmChatOpenAi")), None)
    if not llm_node:
        raise ValueError("OpenAI Chat Model 노드를 찾지 못함 (@n8n/n8n-nodes-langchain.lmChatOpenAi).")
    llm = build_llm(llm_node)

    # HTTP 툴들
    tools: List[Callable] = []
    for n in nodes:
        if n.get("type") == "n8n-nodes-base.httpRequestTool":
            tools.append(build_http_tool(n))

    # 에이전트 존재 검사
    agent_node = next((n for n in nodes if n.get("type", "").endswith(".agent")), None)
    if not agent_node:
        # 에이전트 노드가 없으면 기본 ReAct로 구성
        app = create_react_agent(llm, tools)
    else:
        app = create_react_agent(llm, tools)

    # 트리거 후보
    trigger = next((n for n in nodes if "chatTrigger" in n.get("type", "")), None)
    trigger_name = trigger.get("name") if trigger else "When chat message received"

    def invoke_chat(user_text: str, system_prompt: str = None) -> Dict[str, Any]:
        msgs = []
        if system_prompt:
            msgs.append(SystemMessage(system_prompt))
        msgs.append(HumanMessage(user_text))
        result = app.invoke({"messages": msgs})
        ai_msgs = [m for m in result["messages"] if isinstance(m, AIMessage)]
        return {
            "reply": ai_msgs[-1].content if ai_msgs else "",
            "trace": result["messages"],
            "trigger": trigger_name,
        }

    return app, invoke_chat

# ---------- 사용 예 ----------
if __name__ == "__main__":
    # 예) 파일로부터 로드
    with open("workflow.json", "r", encoding="utf-8") as f:
        wf = json.load(f)

    app, invoke_chat = build_langgraph_from_n8n(wf)

    # ENV 예시: 구글 CSE 키/엔진이 있는 httpRequestTool이 있을 때
    # export GOOGLE_SEARCH_KEY=...  등으로 직접 세팅하지 않고
    # 본 스크립트는 각 툴 노드 이름 기반으로 환경변수를 만듭니다.
    # 예: 노드 이름 "구글검색", 파라미터 "key" → ENV: GOOGLESEARCH_KEY
    # 필요 시 print로 확인 가능.

    out = invoke_chat("LangGraph 개요를 찾아 요약해줘.")
    print(out["reply"])
