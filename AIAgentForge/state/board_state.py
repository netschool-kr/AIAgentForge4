# AIAgentForge/AIAgentForge/state/dashboard_state.py:
import reflex as rx
from .base import BaseState
from .auth_state import AuthState

class BoardState(BaseState):
    """
    대시보드 페이지의 상태를 관리하는 클래스입니다.
    """
    
    # --- [접근 가능한 게시판 목록 기능] ---
    visible_boards: list[dict] = []
    is_loading_boards: bool = False

    async def load_visible_boards(self):
        """사용자가 접근 권한을 가진 게시판 목록만 불러옵니다."""
        self.is_loading_boards = True
        yield
        try:
            # RLS 정책이 자동으로 필터링해주므로, select만 호출하면
            # Supabase가 현재 사용자의 권한에 맞는 데이터만 반환합니다.
            response = self.supabase_client.from_("boards").select("*").order("name").execute()
            self.visible_boards = response.data
        except Exception as e:
            print(f"Error loading visible boards: {e}")
        finally:
            self.is_loading_boards = False
            yield
