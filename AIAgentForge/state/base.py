# AIAgentForge/state/base.py
import os
import reflex as rx
from supabase import create_client, Client
from gotrue.types import User
from typing import ClassVar
from dotenv import load_dotenv
from postgrest import SyncPostgrestClient
# --- [삭제된 부분] ---
# 순환 참조를 유발하는 최상위 import를 제거합니다.
# from .auth_state import AuthState

class BaseState(rx.State):
    """
    앱의 기본 상태입니다.
    공유 변수와 Supabase 클라이언트를 포함합니다.
    모든 다른 상태는 이 상태를 상속해야 합니다.
    """
    is_authenticated: bool = False
    user: User | None = None
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    load_dotenv()

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

    supabase_client: ClassVar[Client] = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )

    # Supabase의 데이터베이스(Postgres) 부분만을 다루는 클라이언트
    async def _get_authenticated_client(self) -> SyncPostgrestClient:
        """인증된 Postgrest 클라이언트를 반환합니다."""
        # 함수 내에서 AuthState를 import하여 순환 참조를 방지합니다.
        from .auth_state import AuthState
        
        auth_state = await self.get_state(AuthState)
        if not auth_state.is_authenticated:
            raise Exception("사용자가 인증되지 않았습니다.")
        return SyncPostgrestClient(
            f"{self.SUPABASE_URL}/rest/v1",
            headers={
                "apikey": self.SUPABASE_KEY,
                "Authorization": f"Bearer {auth_state.access_token}",
            }
        )

    #전체 Client 인스턴스(Supabase Python SDK의 supabase-py 라이브러리에서 제공). 
    # 이는 데이터베이스(Postgrest)뿐만 아니라 인증(auth), 실시간(realtime), 스토리지(storage) 등 
    # Supabase의 모든 기능을 포함합니다
    async def _get_supabase_client(self) -> Client:
        """인증된 Supabase 클라이언트를 반환합니다."""
        # 함수 내에서 AuthState를 import하여 순환 참조를 방지합니다.
        from .auth_state import AuthState

        auth_state = await self.get_state(AuthState)
        if not auth_state.is_authenticated:
            raise Exception("사용자가 인증되지 않았습니다.")
        client: Client = create_client(self.SUPABASE_URL, self.SUPABASE_KEY)
        client.auth.set_session(auth_state.access_token, '')
        return client
    
    #@classmethod
    async def admin_client(slef) -> Client:
        if not self.SUPABASE_URL or not self.SUPABASE_SERVICE_KEY:
            raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY")
        return create_client(self.SUPABASE_URL, self.SUPABASE_SERVICE_KEY)
    
    async def _get_service_client(self) -> Client:
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not key:
            raise Exception("Missing SUPABASE_SERVICE_KEY")
        client: Client = create_client(self.SUPABASE_URL, key)
        return client
    