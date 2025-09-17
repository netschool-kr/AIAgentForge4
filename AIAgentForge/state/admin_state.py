# AIAgentForge/state/admin_state.py 
import reflex as rx
from .base import BaseState
from .auth_state import AuthState
from supabase import create_client, Client
import os

class AdminState(BaseState):
    """관리자 패널의 상태와 로직을 관리합니다."""
    all_users: list[dict] = []
    
    # --- [게시판 관리 기능] ---
    boards: list[dict] = []
    is_loading_boards: bool = False

    async def _get_authed_client(self) -> Client | None:
        """현재 사용자의 인증 토큰으로 초기화된 Supabase 클라이언트를 반환합니다."""
        auth_state = await self.get_state(AuthState)
        if not auth_state.is_authenticated or not auth_state.access_token:
            print("Authentication error: User is not logged in or token is missing.")
            return None
        
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_ANON_KEY")
        
        authed_client: Client = create_client(url, key)
        authed_client.auth.set_session(auth_state.access_token, auth_state.refresh_token)
        return authed_client

    async def load_all_users(self):
        pass

    async def load_all_boards(self):
        """관리자가 모든 게시판 목록을 불러옵니다."""
        self.is_loading_boards = True
        yield
        try:
            response = self.supabase_client.from_("boards").select("*").order("created_at", desc=True).execute()
            self.boards = response.data
        except Exception as e:
            print(f"Error loading boards: {e}")
        finally:
            self.is_loading_boards = False
            yield

    async def create_board(self, form_data: dict):
        """새로운 게시판을 생성합니다. (인증된 클라이언트로 RPC 호출)"""
        try:
            if not form_data.get("name"):
                print("Board name is required.")
                return

            # [FIXED] 사용자의 JWT로 인증된 클라이언트를 가져옵니다.
            authed_client = await self._get_authed_client()
            if not authed_client:
                return

            # 인증된 클라이언트로 RPC 함수를 호출합니다.
            authed_client.rpc(
                "create_new_board",
                {
                    "board_name": form_data["name"],
                    "board_description": form_data.get("description", ""),
                    "read_perm": form_data.get("read_permission", "user"),
                    "write_perm": form_data.get("write_permission", "user"),
                }
            ).execute()
            
            yield AdminState.load_all_boards
        except Exception as e:
            print(f"Error creating board: {e}")

    async def update_board_permissions(self, board_id: str, permissions: dict):
        """게시판의 권한을 수정합니다."""
        try:
            authed_client = await self._get_authed_client()
            if not authed_client:
                return
                
            authed_client.from_("boards").update(permissions).eq("id", board_id).execute()
            yield AdminState.load_all_boards
        except Exception as e:
            print(f"Error updating board permissions: {e}")

    async def delete_board(self, board_id: str):
        """게시판을 삭제합니다."""
        try:
            authed_client = await self._get_authed_client()
            if not authed_client:
                return

            authed_client.from_("boards").delete().eq("id", board_id).execute()
            yield AdminState.load_all_boards
        except Exception as e:
            print(f"Error deleting board: {e}")
