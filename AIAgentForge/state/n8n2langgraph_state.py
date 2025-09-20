import reflex as rx
from AIAgentForge.state.base import BaseState
import json, re, os, textwrap
from typing import Any, List, Tuple


class N8nConvertState(BaseState):
    # 입력/상태
    json_text: str = ""
    converted_code: str = ""
    uploaded_filename: str = ""
    env_hints: dict[str, list[str]] = {}
    error: str = ""

    # UI용 파생값: dict Var → 리스트
    @rx.var
    def env_hints_list(self) -> list[tuple[str, list[str]]]:
        return list(self.env_hints.items())

    # -------- 입력 핸들러 --------
    def set_json_text(self, v: str):
        self.json_text = v

    @rx.event
    async def handle_upload(self, files: Any):
        # files는 단일/다중 둘 다 들어올 수 있음 → 리스트로 정규화
        file_list = files if isinstance(files, list) else [files]
        if not file_list:
            return
        f = file_list[0]
        self.uploaded_filename = getattr(f, "name", "uploaded.json")
        try:
            b = await f.read()
            self.json_text = b.decode("utf-8")
        except Exception as e:
            self.error = f"파일 읽기 실패: {e}"
        yield

    # -------- 변환기 --------
    @staticmethod
    def _sanitize_name(name: str) -> str:
        return re.sub(r"[^A-Za-z0-9_]", "_", name.strip()).lower() or "tool"

    @staticmethod
    def _strip_n8n_expr(v):
        if isinstance(v, str):
            return re.sub(r"\{\{.*?\}\}", "", v).strip()
        return v

    def _convert(self, wf: dict) -> tuple[str, dict]:
        nodes = wf.get("nodes", [])

        # 1) 모델 추출
        model = "gpt-4.1-mini"
        for n in nodes:
            t = n.get("type", "")
            if t.endswith(".lmChatOpenAi"):
                mv = n.get("parameters", {}).get("model", {})
                model = mv.get("value") or mv.get("model") or model
                break

        # 2) HTTP 툴 수집
        tools = []
        env_hints: dict[str, list[str]] = {}
        for n in nodes:
            if n.get("type") == "n8n-nodes-base.httpRequestTool":
                name = n.get("name") or n.get("id") or "http_tool"
                func = self._sanitize_name(name)
                desc = n.get("parameters", {}).get("toolDescription") or "HTTP request tool"
                url = n.get("parameters", {}).get("url") or ""
                method = (n.get("parameters", {}).get("options", {}) or {}).get("method", "GET")
                qp = (n.get("parameters", {}).get("queryParameters", {}) or {}).get("parameters", []) or []

                fixed = {}
                query_param = None
                env_keys = []
                for p in qp:
                    k = p.get("name")
                    v = self._strip_n8n_expr(p.get("value"))
                    if not k:
                        continue
                    if k.lower() in {"q", "query"}:
                        query_param = k
                        continue
                    if any(tk in k.lower() for tk in ["key", "token", "secret", "apikey", "api_key"]):
                        env_name = f"{func.upper()}_{k.upper()}"
                        env_keys.append((k, env_name))
                    else:
                        fixed[k] = v

                if env_keys:
                    env_hints[func] = [env for _, env in env_keys]

                tools.append({
                    "func": func, "desc": desc, "url": url, "method": method,
                    "fixed": fixed, "query_param": query_param, "env_keys": env_keys
                })

        # 3) 코드 생성 (모든 템플릿은 일반 문자열 + .format 사용. 중괄호는 {{ }}로 이스케이프)
        header_tmpl = textwrap.dedent("""
            # Auto-generated from n8n workflow
            # requirements: langgraph>=0.2 langchain>=0.2 langchain-openai>=0.2 requests>=2
            import os, requests
            from typing import Dict, Any, List
            from langchain.tools import tool
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
            from langgraph.prebuilt import create_react_agent

            llm = ChatOpenAI(model="{model}")
        """)
        header = header_tmpl.format(model=model)

        tool_defs: list[str] = []
        tool_names: list[str] = []

        for t in tools:
            func = t["func"]; desc = t["desc"]; url = t["url"]; method = t["method"].upper()
            fixed = t["fixed"]; qname = t["query_param"]; env_keys = t["env_keys"]

            if fixed:
                fixed_src = "{" + ", ".join([f'"{k}": "{(v or "")}"' for k, v in fixed.items()]) + "}"
            else:
                fixed_src = "{}"

            # ENV 주입 블록
            env_block_lines = []
            for k, env in env_keys:
                env_block_lines.append(f'    v_{k} = os.getenv("{env}")')
                env_block_lines.append(f'    if not v_{k}:')
                env_block_lines.append(f'        return "Missing env: {env}"')
            env_block = "\n".join(env_block_lines) if env_block_lines else ""

            env_assign_lines = [f'    params["{k}"] = v_{k}' for k, _ in env_keys]
            env_assign_block = "\n".join(env_assign_lines) if env_assign_lines else ""

            query_block = ""
            if qname:
                query_block = (
                    '    if query is not None:\n'
                    f'        params["{qname}"] = query'
                )

            tool_src_tmpl = textwrap.dedent("""
                @tool("{func}", return_direct=False)
                def {func}(query: str) -> str:
                    \"\"\"{desc}\"\"\"
                    url = "{url}"
                    method = "{method}"
                    params = {fixed_src}.copy()
                {query_block}
                {env_block}
                {env_assign_block}
                    try:
                        r = requests.request(method, url, params=params, timeout=30)
                        if r.headers.get("content-type","").startswith("application/json"):
                            data = r.json()
                        else:
                            data = r.text
                    except Exception as e:
                        return f"HTTP error: {{e}}"

                    if isinstance(data, dict) and "items" in data:
                        items = data.get("items") or []
                        top = [f"- {{i.get('title')}}\\n  {{i.get('link')}}" for i in items[:5] if isinstance(i, dict)]
                        return "Top results:\\n" + ("\\n".join(top) if top else "No results")
                    return str(data)[:4000]
            """)
            tool_src = tool_src_tmpl.format(
                func=func,
                desc=desc.replace('"', '\\"'),
                url=url.replace('"', '\\"'),
                method=method,
                fixed_src=fixed_src,
                query_block=query_block,
                env_block=env_block,
                env_assign_block=env_assign_block,
            )
            tool_defs.append(tool_src)
            tool_names.append(func)

        tools_block = f"tools = [{', '.join(tool_names)}]" if tool_names else "tools = []"

        tail_tmpl = textwrap.dedent("""
            {tools_block}
            app = create_react_agent(llm, tools)

            def invoke_chat(user_text: str, system_prompt: str | None = None) -> dict:
                msgs = []
                if system_prompt:
                    msgs.append(SystemMessage(system_prompt))
                msgs.append(HumanMessage(user_text))
                result = app.invoke({{"messages": msgs}})
                ai_msgs = [m for m in result["messages"] if isinstance(m, AIMessage)]
                return {{"reply": ai_msgs[-1].content if ai_msgs else "", "trace": result["messages"]}}

            if __name__ == "__main__":
                print(invoke_chat("LangGraph 개요를 찾아 요약해줘.")["reply"])
        """)
        tail = tail_tmpl.format(tools_block=tools_block)

        code = header + "\n".join(tool_defs) + "\n" + tail
        return code, env_hints

    @rx.event
    def convert(self):
        self.error = ""
        self.converted_code = ""
        self.env_hints = {}
        try:
            wf = json.loads(self.json_text)
        except Exception as e:
            self.error = f"JSON 파싱 실패: {e}"
            return
        try:
            code, hints = self._convert(wf)
            self.converted_code = code
            self.env_hints = hints
        except Exception as e:
            self.error = f"변환 실패: {e}"

    @rx.event
    def download_py(self):
        if not self.converted_code:
            return
        return rx.download(data=self.converted_code, filename="langgraph_app.py")
