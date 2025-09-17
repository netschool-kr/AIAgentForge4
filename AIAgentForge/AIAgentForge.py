# AIAgentForge/AIAgentForge.py
import os
from dotenv import load_dotenv
load_dotenv()  # .env 파일에서 환경 변수를 로드합니다.

import reflex as rx
from AIAgentForge.pages.dashboard import dashboard_page
from AIAgentForge.pages.chat import chat_page  # 새로 만든 chat_page를 가져옵니다.
from AIAgentForge.pages.login import login_page      # 로그인 페이지 import
from AIAgentForge.pages.signup import signup_page    # 회원가입 페이지 import
from AIAgentForge.state.auth_state import AuthState  # 변경: AuthState import 추가 (BaseState 대신 사용)
from AIAgentForge.pages.collections import collections_page # 새로 만든 페이지 import
# from AIAgentForge.state.collection_state import CollectionState  # CollectionState import 추가
from AIAgentForge.pages.collection_detail.collection_detail import collection_detail_page # 상세 페이지 import
from AIAgentForge.pages.search import search_page 
from AIAgentForge.pages.admin_page import admin_page
from AIAgentForge.pages.youtube import youtube_page
from AIAgentForge.pages.blog import blog_page
from AIAgentForge.pages.research import research_page
#from AIAgentForge.pages.lresearch import lresearch_page
from AIAgentForge.pages.email import email_page
from AIAgentForge.pages.boards import boards_page
from AIAgentForge.pages.board_detail.board_detail import board_detail_page # 상세 페이지 import
from AIAgentForge.pages.new_post.new_post import new_post_page # 상세 페이지 import
from AIAgentForge.pages.post_detail.post_detail import post_detail_page
#from AIAgentForge.state.post_state import PostDetailState, PostState
from AIAgentForge.state.board_state import BoardState

from fastapi import FastAPI
from AIAgentForge.utils.v1_router import api_v1_router
from uuid import uuid4


def setup_langchain_tracing():
    """LangSmith 추적을 위한 환경 변수를 설정합니다."""
    if os.environ.get("LANGCHAIN_API_KEY"):
        unique_id = uuid4().hex[0:8]
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = f"Reflex YouTube Translator - {unique_id}"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        print("✅ LangSmith 추적이 활성화되었습니다.")
    else:
        print("ℹ️ LangSmith 추적을 사용하려면 LANGCHAIN_API_KEY를 설정하세요.")

# 1. 확장할 FastAPI 앱 인스턴스를 생성합니다.
fastapi_app = FastAPI(title="AIAgentForge API")
fastapi_app.include_router(api_v1_router)
setup_langchain_tracing()

# 애플리케이션 인스턴스를 생성합니다.
app = rx.App(
    api_transformer=fastapi_app,
)
#app = rx.App(backend_only=bool(os.environ.get('REFLEX_BACKEND_ONLY')))
# 보호된 라우트
app.add_page(
    dashboard_page, 
    route="/", 
    on_load=[AuthState.check_auth, BoardState.load_visible_boards]
)
app.add_page(chat_page, route="/chat", on_load=AuthState.check_auth)  
app.add_page(
    collection_detail_page,
    route="/collections/[collection_id]",
    on_load=AuthState.check_auth
)

app.add_page(
    board_detail_page,
    route="/boards/[board_id]",
    on_load=AuthState.check_auth
)

app.add_page(
    new_post_page,
    route="/new_post/[board_id]",
    on_load=AuthState.check_auth
)

app.add_page(
    post_detail_page,
    route="/posts/[post_id]",
    on_load=AuthState.check_auth
)

# 공개 라우트
app.add_page(login_page, route="/login")
app.add_page(signup_page, route="/signup")
app.add_page(search_page, route="/search")
app.add_page(collections_page, route="/collections")
app.add_page(youtube_page, route="/youtube")
app.add_page(blog_page, route="/blog")
app.add_page(research_page, route="/research", title="AI Deep Research Agent")
#app.add_page(lresearch_page, route="/lresearch", title="Local AI Deep Research Agent")
app.add_page(email_page, route="/email", title="Send Email To Users")

# --- [게시판 관련 페이지 라우팅 추가] ---
app.add_page(boards_page, route="/boards", on_load=AuthState.check_auth)
# app.add_page(board_page, route="/boards/[board_id]", on_load=[AuthState.check_auth, PostState.load_board_and_posts])
#app.add_page(post_page, route="/posts/[post_id]", on_load=[AuthState.check_auth, PostDetailState.load_post])
# app.add_page(post_form_page, route="/new-post/[board_id]", on_load=AuthState.check_auth) # 새 글 작성
# app.add_page(post_form_page, route="/edit-post/[post_id]", on_load=AuthState.check_auth) # 글 수정


app.add_page(admin_page, route="/admin", on_load=AuthState.check_admin)




