# AIAgentForge/agents/lresearcher.py

import os
# 최신 라이브러리 임포트
from langchain_ollama import ChatOllama
from langchain_tavily import TavilySearch
from langchain.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# .env 파일에서 환경 변수 로드
load_dotenv()

# Tavily API 키 설정 확인
if os.getenv("TAVILY_API_KEY") is None:
    raise ValueError("TAVILY_API_KEY 환경 변수가 설정되지 않았습니다.")

# --- 모델 및 도구 설정 ---
# 로컬 LLM (Llama 3) 초기화 (최신 클래스 사용)
local_llm = ChatOllama(model="llama3", temperature=0)

# 웹 검색 도구 초기화 (최신 클래스 사용)
# 클래스 이름이 TavilySearchResults -> TavilySearch 로 변경되었습니다.
search_tool = TavilySearch(max_results=3)

# --- LangGraph 상태 정의 ---
class AgentState(TypedDict):
    """
    그래프의 상태를 정의하는 TypedDict.
    - query: 사용자의 초기 질문
    - plan: 리서치 계획
    - drafts: 각 하위 질문에 대한 리서치 결과 초안 리스트
    - critques: 초안에 대한 비평
    - report: 최종 보고서
    """
    query: str
    plan: str
    drafts: List[str]
    critiques: List[str]
    report: str

# --- 프롬프트 템플릿 정의 ---

# 1. 계획 생성 프롬프트
planner_prompt = ChatPromptTemplate.from_template(
    """당신은 전문적인 리서처입니다. 사용자의 질문에 대해 심층적인 답변을 제공하기 위한 리서치 계획을 단계별로 작성해주세요.
각 단계는 명확하고 실행 가능해야 합니다.

사용자 질문: {query}

리서치 계획:"""
)

# 2. 리서치 초안 작성 프롬프트
draft_prompt = ChatPromptTemplate.from_template(
    """당신은 리서치 어시스턴트입니다. 다음 질문에 대해 제공된 컨텍스트 정보를 바탕으로 상세한 답변 초안을 작성해주세요.
답변은 포괄적이고 잘 구성되어야 합니다.

질문: {query}
컨텍스트: {context}

답변 초안:"""
)

# 3. 최종 보고서 작성 프롬프트
report_prompt = ChatPromptTemplate.from_template(
    """당신은 수석 편집자입니다. 다음 리서치 초안들을 종합하여 하나의 일관되고 상세한 최종 보고서를 작성해주세요.
보고서는 서론, 본론, 결론의 구조를 갖추어야 하며, 모든 정보가 정확하게 통합되어야 합니다.

리서치 초안들:
{drafts}

최종 보고서:"""
)

# 4. 비평 및 개선 방향 제시 프롬프트
critique_prompt = ChatPromptTemplate.from_template(
    """당신은 비평가입니다. 다음 리서치 초안을 검토하고, 보고서의 품질을 향상시키기 위한 구체적인 개선 방안을 제시해주세요.
사실 확인, 깊이, 명확성 측면에서 부족한 점을 지적해주세요.

리서치 초안:
{draft}

비평 및 개선 제안:"""
)


# --- LangGraph 노드(Node) 함수 정의 (비동기로 수정) ---

async def plan_step(state: AgentState):
    """리서치 계획을 생성하는 비동기 노드"""
    logging.info("--- 리서치 계획 생성 중 ---")
    planner = planner_prompt | local_llm | StrOutputParser()
    plan = await planner.ainvoke({"query": state["query"]})
    return {"plan": plan}

async def research_step(state: AgentState):
    """계획에 따라 웹 검색을 수행하고 초안을 작성하는 비동기 노드"""
    logging.info("--- 웹 검색 및 초안 작성 중 ---")
    plan_steps = state["plan"].strip().split("\n")
    drafts = []
    for step in plan_steps:
        if not step:
            continue
        logging.info(f"  - 검색 주제: {step}")
        # 웹 검색 비동기 수행
        search_results = await search_tool.ainvoke(step)
        # TavilySearch의 결과는 딕셔너리 리스트가 아닌 문자열 리스트일 수 있습니다.
        # 따라서 결과 형식을 확인하고 적절히 처리해야 합니다.
        # 여기서는 결과가 문자열 리스트라고 가정합니다.
        context = "\n".join(search_results) if isinstance(search_results, list) else search_results
        
        # 초안 비동기 생성
        draft_generator = draft_prompt | local_llm | StrOutputParser()
        draft = await draft_generator.ainvoke({"query": step, "context": context})
        drafts.append(draft)
        logging.info(f"  - 초안 생성 완료")
    return {"drafts": drafts}

async def report_step(state: AgentState):
    """초안들을 종합하여 최종 보고서를 생성하는 비동기 노드"""
    logging.info("--- 최종 보고서 생성 중 ---")
    drafts_text = "\n\n---\n\n".join(state["drafts"])
    report_generator = report_prompt | local_llm | StrOutputParser()
    report = await report_generator.ainvoke({"drafts": drafts_text})
    return {"report": report}

# --- 그래프 구성 ---
def build_agent_graph():
    """
    LangGraph를 사용하여 리서치 에이전트의 워크플로우를 구성합니다.
    StateGraph 실행을 State에서 관리하므로, 이 함수는 그래프 객체만 반환합니다.
    """
    workflow = StateGraph(AgentState)

    # 노드 추가 (비동기 함수 등록)
    workflow.add_node("planner", plan_step)
    workflow.add_node("researcher", research_step)
    workflow.add_node("reporter", report_step)

    # 엣지(Edge) 추가 (노드 간의 연결)
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "reporter")
    workflow.add_edge("reporter", END)

    # 그래프 컴파일
    return workflow.compile()
