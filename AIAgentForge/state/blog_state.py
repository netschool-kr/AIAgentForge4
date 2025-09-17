# blog_state.py
import os
import re
import reflex as rx
from uuid import uuid4

# LangChain 관련 라이브러리 임포트
from langchain_community.tools import TavilySearchResults
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig, chain
from langchain_openai import ChatOpenAI

# --- 중요 ---
# 이 애플리케이션을 실행하기 전에 터미널에서 아래 환경 변수를 설정해야 합니다.
# export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
# export TAVILY_API_KEY="YOUR_TAVILY_API_KEY"
# export LANGCHAIN_API_KEY="YOUR_LANGCHAIN_API_KEY"

def setup_langchain_environment():
    """LangChain 추적 환경을 설정합니다."""
    unique_id = uuid4().hex[0:8]
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = f"Reflex Blog Post Generator - {unique_id}"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

class BlogState(rx.State):
    """애플리케이션의 상태와 이벤트 핸들러를 정의합니다."""

    # --- 상태 변수 (State Vars) ---
    product_keyword: str = ""
    title_candidates: list[str] = []
    selected_title: str = ""
    generated_outline: str = ""
    final_posting: str = ""
    
    # UI 제어를 위한 상태 변수
    is_generating_titles: bool = False
    is_generating_outline: bool = False
    is_generating_posting: bool = False
    is_finished: bool = False

    def set_product_keyword(self, value: str):
        self.product_keyword = value
        
    # --- 이벤트 핸들러 (Event Handlers) ---
    def init_state(self):
        """페이지 로드 시 상태를 초기화하고 환경을 설정합니다."""
        self.reset_all()
        setup_langchain_environment()

    def reset_all(self):
        """모든 상태를 초기값으로 리셋합니다."""
        self.product_keyword = ""
        self.title_candidates = []
        self.selected_title = ""
        self.generated_outline = ""
        self.final_posting = ""
        self.is_generating_titles = False
        self.is_generating_outline = False
        self.is_generating_posting = False
        self.is_finished = False

    async def generate_titles(self):
        """제품 키워드를 기반으로 블로그 제목 후보를 생성합니다."""
        if not self.product_keyword.strip():
            return
        
        self.is_generating_titles = True
        self.title_candidates = []
        self.selected_title = ""
        self.generated_outline = ""
        self.final_posting = ""
        self.is_finished = False
        yield

        try:
            llm = ChatOpenAI(model="gpt-4o", temperature=0)
            prompt = ChatPromptTemplate.from_messages([
                ("system", "너는 다음 키워드를 기반으로 제품 사용후기 네이버 블로그 제목을 추천해주는 전문가야. 다음 키워드를 기반으로 3개의 네이버 블로그 제목을 추천해줘."),
                MessagesPlaceholder(variable_name="messages"),
            ])
            title_chain = prompt | llm

            response = await title_chain.ainvoke({"messages": [HumanMessage(content=self.product_keyword)]})
            
            # 번호와 따옴표 제거
            cleaned_titles = []
            for line in response.content.strip().split("\n"):
                match = re.match(r'\d+\.\s*"?(.+?)"?$', line.strip())
                cleaned_title = match.group(1).strip() if match else line.strip()
                cleaned_titles.append(cleaned_title)

            self.title_candidates = cleaned_titles
        finally:
            self.is_generating_titles = False
            yield

    async def select_title_and_generate_outline(self, title: str):
        """제목을 선택하고 바로 목차 생성을 시작합니다."""
        self.selected_title = title
        self.is_generating_outline = True
        yield

        try:
            llm = ChatOpenAI(model="gpt-4o", temperature=0)
            prompt = ChatPromptTemplate.from_messages([
                ("system", """다음 제목을 기반으로 네이버 블로그에 최적화된 제품 사용후기 포스팅 목차를 작성해줘.
부제목만 생성하고 소제목은 생성하지마. 부제목 앞에 숫자를 포함시키지마.
인터넷 검색을 통해 인터넷에 있는 자료를 같이 참조해서 결과를 생성해줘.
요청 조건: 4~6개의 목차로 간결하게 구성"""),
                ("human", "{user_input}"),
                MessagesPlaceholder(variable_name="messages"),
            ])
            tool = TavilySearchResults(max_results=3)
            llm_with_tools = llm.bind_tools([tool])
            outline_chain = prompt | llm_with_tools

            @chain
            async def tool_chain(user_input: str, config: RunnableConfig):
                input_ = {"user_input": user_input, "messages": []}
                ai_msg = await outline_chain.ainvoke(input_, config=config)
                tool_msgs = await tool.abatch(ai_msg.tool_calls, config=config)
                return await outline_chain.ainvoke({**input_, "messages": [ai_msg, *tool_msgs]}, config=config)

            response = await tool_chain.ainvoke(self.selected_title)
            self.generated_outline = response.content
        finally:
            self.is_generating_outline = False
            yield

    async def generate_final_posting(self):
        """제목과 목차를 기반으로 최종 포스팅을 생성합니다."""
        self.is_generating_posting = True
        yield

        try:
            llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
            prompt = ChatPromptTemplate.from_messages([
                ("system", """너는 네이버 블로그 전문 작가야.
다음 아웃라인을 기반으로 제품 사용후기 블로그 포스팅을 작성해줘.
부제목은 그대로 사용하고 각 부제목마다 자연스러운 3문장 내외로 작성해줘.
자연스럽고 친근한 말투로 작성하고, 너무 광고처럼 보이지 않게 솔직한 후기로 써줘.
아웃라인과 별도로 앞에 머릿말과 끝에 맺음말도 작성해줘.

제목: {title}
아웃라인:
{outline}"""),
            ])
            posting_chain = prompt | llm
            response = await posting_chain.ainvoke({
                "title": self.selected_title,
                "outline": self.generated_outline
            })
            self.final_posting = response.content
            self.is_finished = True
        finally:
            self.is_generating_posting = False
            yield

    async def handle_key_down(self, key: str):
        """Handle key down events for the input field."""
        if key == "Enter":
            self.generate_titles()