# AIAgentForge/state/post_state.py
import reflex as rx
from .base import BaseState
from .auth_state import AuthState
from typing import Optional, Dict, Any
from postgrest import SyncPostgrestClient

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
import datetime

class PostState(BaseState):
    """게시판별 게시글 관리(CRUD, 검색)를 위한 상태"""

    curr_board_id: Optional[str] = None

    # 현재 게시판 정보
    board_name: str = ""
    board_description: str = ""

    # 게시글 목록
    posts: list[dict] = []

    # UI 상태
    is_loading: bool = False
    search_query: str | None
    title: str | None
    content: str | None

    def set_search_query(self, value: str):
        self.search_query = value

    def set_title(self, new_title: str):
        self.title = new_title

    def set_content(self, new_content: str):
        self.content = new_content
        
    def go_to_post(self, post_id: str):
        """게시물 상세 페이지로 리디렉션하는 이벤트 핸들러."""
        return rx.redirect(f"/posts/{post_id}")
    
    # async def _get_authenticated_client(self) -> SyncPostgrestClient:
    #     auth_state = await self.get_state(AuthState)
    #     if not auth_state.is_authenticated:
    #         # 인증이 필요없는 읽기 작업 등을 위해 익명 클라이언트를 반환할 수도 있습니다.
    #         # 여기서는 RLS 정책상 인증이 필요하다고 가정합니다.
    #         logging.warning("User is not authenticated. Returning anonymous client.")
    #         return self.supabase_client # 익명 클라이언트 반환
            
    #     return SyncPostgrestClient(
    #         f"{self.SUPABASE_URL}/rest/v1",
    #         headers={
    #             "apikey": self.SUPABASE_KEY,
    #             "Authorization": f"Bearer {auth_state.access_token}",
    #         }
    #     )
                
    async def load_board_details(self):
        """'새 글 작성' 페이지 로드 시 게시판 정보만 불러옵니다."""
        # 이전에 입력했을 수 있는 내용 초기화
        self.title = ""
        self.content = ""
        
        # URL에서 board_id를 가져옵니다. new_post/[board_id] 라우트를 사용합니다.
        self.curr_board_id = self.router.page.params.get("board_id")
        logging.info(f"load_board_details for board_id: {self.curr_board_id}")
        
        if not self.curr_board_id:
            logging.warning("Board ID not found for loading details.")
            return

        try:
            # 게시판 정보는 보통 공개되어 있으므로 익명 클라이언트를 사용해도 괜찮습니다.
            board_res = self.supabase_client.from_("boards").select("name").eq("id", self.curr_board_id).single().execute()
            if board_res.data:
                self.board_name = board_res.data.get("name", "알 수 없는 게시판")
            else:
                self.board_name = "게시판을 찾을 수 없습니다."
        except Exception as e:
            logging.error(f"Error loading board details: {e}")
        yield
        
    async def load_board_and_posts(self):
        """페이지 로드 시 게시판 정보와 게시글 목록을 함께 불러옵니다."""
        self.curr_board_id = self.router.page.params.get("board_id")
        logging.info(f"Loading board with ID: {self.curr_board_id}")
        self.is_loading = True
        yield

        if not self.curr_board_id:
            self.is_loading = False
            logging.info("Board ID not found in URL.")
            yield
            return

        try:
            # --- [수정된 부분] ---
            # RLS 정책을 통과하기 위해 인증된 클라이언트를 가져옵니다.
            db_client = await self._get_authenticated_client()

            # 게시판 정보 조회 (인증된 클라이언트 사용)
            board_res = db_client.from_("boards").select("*").eq("id", self.curr_board_id).single().execute()
            self.board_name = board_res.data.get("name", "알 수 없는 게시판")
            self.board_description = board_res.data.get("description", "")

            # 게시글 목록 조회 (인증된 클라이언트 사용)
            posts_res = db_client.from_("posts").select("*").eq("board_id", self.curr_board_id).order("created_at", desc=True).execute()
            self.posts = posts_res.data
            logging.info(f"Loaded {len(self.posts)} posts.") # 로드된 게시글 수 로그 추가

        except Exception as e:
            logging.info(f"Error loading board and posts: {e}")
        finally:
            self.is_loading = False
            yield

    async def handle_search(self):
        """현재 게시판 내에서 게시글을 검색합니다."""
        if not self.search_query.strip():
            yield PostState.load_board_and_posts
            return

        self.is_loading = True
        yield
        try:
            # --- [수정된 부분] ---
            # 검색 시에도 인증된 클라이언트를 사용합니다.
            db_client = await self._get_authenticated_client()
            response = db_client.from_("posts").select("*") \
                .eq("board_id", self.curr_board_id) \
                .or_(f"title.ilike.%{self.search_query}%,content.ilike.%{self.search_query}%") \
                .order("created_at", desc=True).execute()
            self.posts = response.data
        except Exception as e:
            logging.info(f"Error searching posts: {e}")
        finally:
            self.is_loading = False
            yield

    async def create_post(self):
        """새로운 게시글을 생성합니다."""
        try:
            auth_state = await self.get_state(AuthState)
            if not auth_state.is_authenticated or not auth_state.user:
                logging.warning("User is not authenticated. Cannot create post.")
                return

            user_id = auth_state.user.id
            
            db_client = await self._get_authenticated_client()
            db_client.from_("posts").insert({
                "title": self.title,
                "content": self.content,
                "board_id": self.curr_board_id,
                "user_id": user_id,
            }).execute()
            
            self.title = ""
            self.content = ""

            return rx.redirect(f"/boards/{self.curr_board_id}")

        except Exception as e:
            logging.error(f"Error creating post: {e}")
            
class PostDetailState(BaseState):
    """게시물 상세 페이지의 상태를 관리합니다."""
    current_post_id: Optional[str] = None
    post: dict = {}
    is_loading: bool = True
    is_editing: bool = False

    comments: list[dict] = []
    new_comment_content: str = ""

    def set_new_comment_content(self, value: str):
        self.new_comment_content = value

    @rx.var
    def no_comments(self) -> bool:
        """댓글이 없는지 확인하는 계산된 변수."""
        return len(self.comments) == 0

    @rx.var
    def formatted_created_at(self) -> str:
        """게시물 작성 시간을 보기 좋은 형식으로 변환합니다."""
        created_at_str = self.post.get("created_at")
        if created_at_str:
            if created_at_str.endswith('Z'):
                created_at_str = created_at_str[:-1] + '+00:00'
            if '.' in created_at_str:
                # 타임존 정보가 있는 경우 분리 후 재조합
                if '+' in created_at_str:
                    dt_part, tz_part = created_at_str.split('+')
                    dt_part = dt_part.split('.')[0]
                    created_at_str = f"{dt_part}+{tz_part}"
                else: # 타임존 정보가 없는 경우
                    created_at_str = created_at_str.split('.')[0]
                
            try:
                dt_object =  datetime.datetime.fromisoformat(created_at_str)
                return dt_object.strftime("%Y년 %m월 %d일 %H:%M")
            except ValueError as e:
                print(f"Date format error: {e}, original string: {self.post.get('created_at')}")
                return "날짜 형식 오류"
        return ""

    @rx.var
    def is_author(self) -> bool:
        """현재 로그인한 사용자가 게시글 작성자인지 확인합니다."""
        if not self.is_authenticated or not self.user or not self.post:
            return False
        return self.user.id == self.post.get("user_id")


    async def load_comments(self, db_client):
        """게시물에 달린 댓글 목록을 불러오고 날짜를 포맷팅합니다."""
        logging.info("Entering load_comments")
        try:
            comments_res = db_client.from_("comments").select("*").eq("post_id", self.current_post_id).order("created_at", desc=True).execute()
            
            formatted_comments = []
            for comment in comments_res.data:
                created_at_str = comment.get("created_at")
                if created_at_str:
                    if created_at_str.endswith('Z'):
                        created_at_str = created_at_str[:-1] + '+00:00'
                    if '.' in created_at_str:
                        if '+' in created_at_str:
                            dt_part, tz_part = created_at_str.split('+')
                            dt_part = dt_part.split('.')[0]
                            created_at_str = f"{dt_part}+{tz_part}"
                        else:
                            created_at_str = created_at_str.split('.')[0]

                    try:
                        dt_object = datetime.datetime.fromisoformat(created_at_str)
                        comment["formatted_created_at"] = dt_object.strftime("%Y-%m-%d %H:%M")
                    except ValueError:
                        comment["formatted_created_at"] = "날짜 형식 오류"
                else:
                    comment["formatted_created_at"] = ""
                formatted_comments.append(comment)
            
            self.comments = formatted_comments
        except Exception as e:
            print(f"Error loading comments: {e}")

    async def load_post(self):
        """ID를 기반으로 특정 게시글의 상세 정보를 불러옵니다."""
        self.current_post_id = self.router.page.params.get("post_id")
        self.is_loading = True
        yield

        if not self.current_post_id:
            self.is_loading = False
            logging.info("Post ID not found in URL.")
            return

        try:
            # --- [수정된 부분] ---
            # 상세 정보 조회 시에도 인증된 클라이언트를 사용합니다.
            db_client = await self._get_authenticated_client()
            response = db_client.from_("posts").select("*").eq("id", self.current_post_id).single().execute()
            if response.data:
                self.post = response.data
                logging.info("Calling load_comments")
                await self.load_comments(db_client)
            else :
                self.post = {}
        except Exception as e:
            logging.info(f"Error loading post detail: {e}")
        finally:
            self.is_loading = False
            yield
            
    async def delete_post(self):
        """게시글을 삭제하고 게시판 목록 페이지로 리디렉션합니다."""
        if not self.is_author:
            logging.info("Permission denied for deletion.")
            return

        board_id = self.post.get("board_id")

        try:
            client = await self._get_authenticated_client()
            client.from_("posts").delete().eq("id", self.current_post_id).execute()
            
            if board_id:
                return rx.redirect(f"/boards/{board_id}")
            else:
                return rx.redirect("/dashboard")
        except Exception as e:
            print(f"Error deleting post: {e}")

    def toggle_edit(self):
        """수정 모드를 토글합니다."""
        self.is_editing = not self.is_editing

    async def update_post(self, form_data: dict):
        """게시글 내용을 수정합니다."""
        if not self.is_author:
            logging.info("Permission denied for update.")
            return

        try:
            client = await self._get_authenticated_client()
            client.from_("posts").update({
                "title": form_data["title"],
                "content": form_data["content"],
            }).eq("id", self.current_post_id).execute()
            
            self.is_editing = False
            return PostDetailState.load_post
        except Exception as e:
            print(f"Error updating post: {e}")

    async def create_comment(self, form_data: dict):
        """새로운 댓글을 작성합니다."""
        content = form_data.get("comment_content")
        if not self.user or not content:
            return
        
        try:
            auth_state = await self.get_state(AuthState)
            if not auth_state.is_authenticated or not auth_state.user:
                logging.warning("User is not authenticated. Cannot create post.")
                return

            db_client = await self._get_authenticated_client()
                        
            db_client.from_("comments").insert({
                "content": content,
                "post_id": self.current_post_id,
                "user_id": auth_state.user.id,
                "author_email": self.user.email
            }).execute()
            
            self.new_comment_content = ""
            
            PostState.go_to_post(self.current_post_id)
        except Exception as e:
            print(f"Error creating comment: {e}")
        yield

    async def delete_comment(self, comment_id: str):
        """댓글을 삭제합니다."""
        try:
            db_client = await self._get_authenticated_client()

            db_client.from_("comments").delete().eq("id", comment_id).execute()
            logging.info("Calling load_comments")
            await self.load_comments(db_client)
        except Exception as e:
            print(f"Error deleting comment: {e}")
        yield
