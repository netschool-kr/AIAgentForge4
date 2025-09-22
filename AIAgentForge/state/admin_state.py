# AIAgentForge/state/admin_state.py
import os
from .base import BaseState
from .auth_state import AuthState
import reflex as rx
from supabase import create_client, Client


class AdminState(BaseState):
    # 사용자 목록
    all_users: list[dict] = []
    is_loading_users: bool = False

    # 편집 상태
    editor_open: bool = False
    edit_user_id: str = ""
    edit_email: str = ""
    edit_username: str = ""
    edit_full_name: str = ""
    edit_avatar_url: str = ""

    # 게시판
    boards: list[dict] = []
    is_loading_boards: bool = False

    async def _get_service_client(self) -> Client:
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not key:
            raise Exception("Missing SUPABASE_SERVICE_KEY")
        client: Client = create_client(self.SUPABASE_URL, key)
        return client
    

    async def _require_admin(self) -> bool:
        auth = await self.get_state(AuthState)
        if not auth.is_authenticated or not getattr(auth, "user", None):
            print("Admin check failed: unauthenticated.")
            return False
        allow = {e.strip().lower() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()}
        if not allow:
            return True
        email = (auth.user.get("email") if isinstance(auth.user, dict) else getattr(auth.user, "email", "")) or ""
        ok = email.lower() in allow
        if not ok:
            print(f"Admin check failed: {email} not in ADMIN_EMAILS.")
        return ok

    # ---------- 초기 로드 ----------
    async def on_load_admin(self):
        if not await self._require_admin():
            yield rx.redirect("/")
            return
        yield AdminState.load_all_boards
        yield AdminState.load_all_users

    # ---------- 사용자 관리 ----------
    async def load_all_users(self):
        """관리자: 모든 사용자 로드"""
        try:
            svc = await self._get_service_client()  # 서비스 롤 키 기반 클라이언트 (BaseState에 구현)
            resp = svc.auth.admin.list_users(page=1, per_page=100)

            # resp가 리스트이든 AdminUserList이든 처리
            users = getattr(resp, "users", resp)

            norm = []
            for u in users:
                if hasattr(u, "model_dump"):
                    norm.append(u.model_dump())
                else:
                    norm.append({
                        "id": getattr(u, "id", None),
                        "email": getattr(u, "email", None),
                        "created_at": getattr(u, "created_at", None),
                        "last_sign_in_at": getattr(u, "last_sign_in_at", None),
                        "app_metadata": getattr(u, "app_metadata", None),
                        "user_metadata": getattr(u, "user_metadata", None),
                        "is_anonymous": getattr(u, "is_anonymous", False),
                    })
            self.all_users = norm
            yield
        except Exception as e:
            print(f"Error loading users: {e}")
        
    async def open_user_editor(self, user_id: str):
        if not await self._require_admin():
            return
        tgt = next((u for u in self.all_users if u.get("id") == user_id), None)
        if not tgt:
            print("User not found for edit.")
            return
        meta = {}
        try:
            svc = self.admin_client() or self.supabase_client
            prof = (
                svc.from_("profiles")
                .select("username, full_name, avatar_url")
                .eq("id", user_id)
                .maybe_single()
                .execute()
            )
            meta = prof.data or {}
        except Exception as e:
            print(f"Error loading profile: {e}")
        self.edit_user_id = user_id
        self.edit_email = (tgt.get("email") or "")
        self.edit_username = (meta.get("username") or "")
        self.edit_full_name = (meta.get("full_name") or "")
        self.edit_avatar_url = (meta.get("avatar_url") or "")
        self.editor_open = True
        yield

    async def cancel_user_editor(self):
        self.editor_open = False
        yield

    async def save_user(self):
        if not await self._require_admin():
            return
        if not self.edit_user_id:
            return
        uid = self.edit_user_id
        try:
            svc = self.admin_client()
            if not svc:
                return
            if self.edit_email:
                svc.auth.admin.update_user_by_id(uid, {"email": self.edit_email})
            svc.from_("profiles").upsert(
                {
                    "id": uid,
                    "username": (self.edit_username or None),
                    "full_name": (self.edit_full_name or None),
                    "avatar_url": (self.edit_avatar_url or None),
                },
                on_conflict="id",
            ).execute()
        except Exception as e:
            print(f"Error saving user: {e}")
        finally:
            self.editor_open = False
            yield AdminState.load_all_users

    async def delete_user(self, user_id: str):
        if not await self._require_admin():
            return
        try:
            svc = await self._get_service_client()
            if not svc:
                return
            svc.auth.admin.delete_user(user_id)
            yield AdminState.load_all_users
        except Exception as e:
            print(f"Error deleting user: {e}")

    # ---------- 게시판 관리(컴파일 에러 방지 포함) ----------
    async def load_all_boards(self):
        self.is_loading_boards = True
        yield
        try:
            authed = await self._get_service_client()
            if not authed:
                self.boards = []
                return
            resp = authed.from_("boards").select("*").order("created_at", desc=True).execute()
            self.boards = resp.data or []
        except Exception as e:
            print(f"Error loading boards: {e}")
        finally:
            self.is_loading_boards = False
            yield

    async def create_board(self, form_data: dict):
        if not await self._require_admin():
            return
        try:
            svc = self.admin_client() or self.supabase_client
            payload = {
                "name": form_data.get("name") or "",
                "description": form_data.get("description") or "",
                "read_permission": form_data.get("read_permission") or "user",
                "write_permission": form_data.get("write_permission") or "user",
            }
            svc.from_("boards").insert(payload).execute()
            yield AdminState.load_all_boards
        except Exception as e:
            print(f"Error creating board: {e}")

    async def delete_board(self, board_id: str):
        if not await self._require_admin():
            return
        try:
            svc = self.admin_client() or self.supabase_client
            svc.from_("boards").delete().eq("id", board_id).execute()
            yield AdminState.load_all_boards
        except Exception as e:
            print(f"Error deleting board: {e}")

    async def set_editor_open(self, v: bool):
        self.editor_open = bool(v)
        yield

    async def set_edit_email(self, v: str):
        self.edit_email = v or ""
        yield

    async def set_edit_username(self, v: str):
        self.edit_username = v or ""
        yield

    async def set_edit_full_name(self, v: str):
        self.edit_full_name = v or ""
        yield

    async def set_edit_avatar_url(self, v: str):
        self.edit_avatar_url = v or ""
        yield
