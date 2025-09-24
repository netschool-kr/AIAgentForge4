# AIAgentForge/state/auth_state.py
import reflex as rx
from .base import BaseState
import os
from urllib.parse import urlencode
import re
import urllib.parse

class AuthState(BaseState):
    """
    Handles all authentication logic including login, logout, signup,
    and checking the authentication status on page loads.
    """

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SITE_URL = os.getenv("SITE_URL")          
    REDIRECT_URI = f"{SITE_URL}/auth/callback"  

    access_token: str = rx.Cookie("")
    refresh_token: str = rx.Cookie("")
    
    error_message: str = ""
    success_message: str = ""
    is_loading: bool = False

    username_input: str = ""
    username_checking: bool = False
    username_available: bool | None = None
    username_message: str = ""

    @rx.event
    async def oauth_start(self, provider: str):
        """Supabase OAuth 시작: Google 등."""
        if not self.SUPABASE_URL or not self.REDIRECT_URI:
            self.error_message = "OAuth 설정 오류(SUPABASE_URL / SITE_URL)."
            yield
            return
        qs = urlencode({
            "provider": provider,
            "redirect_to": self.REDIRECT_URI,
            "scopes": "openid profile email",
        })
        # external=True 인자를 제거합니다.
        yield rx.redirect(f"{self.SUPABASE_URL}/auth/v1/authorize?{qs}")
        
    @rx.event
    async def oauth_callback(self, code: str = "", **kwargs):
        """
        URL 파라미터에서 세션 정보를 처리하는 콜백 핸들러.
        Supabase OAuth 인증 후 리디렉션될 때 호출됩니다.
        """
        self.is_loading = True
        yield

        # URL 파라미터에서 access_token, refresh_token을 추출
        parsed_url = urllib.parse.urlparse(self.router.as_page_name)
        if parsed_url.fragment:
            fragment_params = urllib.parse.parse_qs(parsed_url.fragment)
            access_token = fragment_params.get("access_token", [None])[0]
            refresh_token = fragment_params.get("refresh_token", [None])[0]
        else:
            access_token = None
            refresh_token = None
            
        # URL 파라미터에서 토큰을 직접 받는 경우 (implicit flow)
        if access_token and refresh_token:
            try:
                # 받은 토큰으로 세션 정보 설정
                session_data = {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
                
                # 받은 세션으로 사용자 정보 설정
                self.supabase_client.auth.set_session(session_data)
                self.user = self.supabase_client.auth.get_user().user
                self.is_authenticated = True
                self.is_loading = False
                yield rx.redirect("/")
                return
            except Exception as e:
                self.error_message = f"세션 처리 실패: {e}"
                self.is_loading = False
                yield rx.redirect("/login")
                return

        # URL 파라미터에서 code를 받아 세션을 교환하는 경우 (PKCE flow)
        if code:
            try:
                resp = self.supabase_client.auth.exchange_code_for_session({"auth_code": code})
                if resp.session:
                    self.access_token  = resp.session.access_token
                    self.refresh_token = resp.session.refresh_token
                    self.user = resp.user
                    self.is_authenticated = True
                    self.is_loading = False
                    yield rx.redirect("/")
                    return
            except Exception as e:
                self.error_message = f"세션 교환 실패: {e}"
                self.is_loading = False
                yield rx.redirect("/login")
                return
        
        # 어떤 토큰도 받지 못한 경우
        self.error_message = "소셜 로그인에 실패했습니다. 유효한 토큰 또는 코드가 없습니다."
        self.is_loading = False
        yield rx.redirect("/login")
        
    def set_username_input(self, v: str):
        v = (v or "").strip().lower()
        self.username_input = v
        self.username_available = None
        self.username_message = ""

    async def check_username_unique(self, v: str | None = None):
        uname = (v or self.username_input or "").strip().lower()
        if not uname:
            self.username_message = "사용자명을 입력하세요."
            self.username_available = None
            yield
            return
        if not re.fullmatch(r"[a-z0-9_]{3,20}", uname):
            self.username_message = "3~20자 영문소문자/숫자/_ 만 허용."
            self.username_available = None
            yield
            return

        self.username_checking = True
        self.username_message = ""
        self.username_available = None
        yield
        try:
            resp = self.supabase_client.table("profiles") \
                .select("id") \
                .eq("username", uname) \
                .limit(1) \
                .execute()
            taken = bool(resp.data)
            self.username_available = not taken
            self.username_message = "사용 가능" if not taken else "이미 사용 중"
        except Exception as e:
            self.username_available = None
            self.username_message = f"확인 실패: {e}"
        finally:
            self.username_checking = False
            yield
            
    @rx.var
    def user_email(self) -> str:
        return self.user.email if self.user else ""

    @rx.var
    def role(self) -> str:
        if self.is_authenticated and self.user and self.user.app_metadata:
            return self.user.app_metadata.get("role", "user")
        return "guest"
    
    async def check_auth(self):
        if not self.access_token:
            if self.is_authenticated:
                self.is_authenticated = False
                self.user = None
            yield rx.redirect("/login")
            return

        try:
            response = self.supabase_client.auth.get_user(self.access_token)
            if response and response.user:
                self.user = response.user
                self.is_authenticated = True
                yield
            else:
                raise Exception("User not found with the given token.")

        except Exception:
            if not self.refresh_token:
                self._reset_auth_state()
                yield rx.redirect("/login")

            try:
                response = await self.supabase_client.auth.refresh_session(self.refresh_token)

                if response.session:
                    self.access_token = response.session.access_token
                    self.refresh_token = response.session.refresh_token
                    self.user = response.user
                    self.is_authenticated = True
                    yield
                else:
                    raise Exception("Session refresh did not return a session.")

            except Exception:
                self._reset_auth_state()
                yield rx.redirect("/login")
                
    async def check_admin(self):
        async for event in self.check_auth():
            yield event

        if self.role != "admin":
            yield rx.redirect("/")
        return
            
    def _reset_auth_state(self):
        self.access_token = ""
        self.refresh_token = ""
        self.is_authenticated = False
        self.user = None
        
    async def handle_login(self, form_data: dict):
        self.is_loading = True
        self.error_message = ""
        yield
        try:
            response = self.supabase_client.auth.sign_in_with_password(
                {"email": form_data["email"], "password": form_data["password"]}
            )
            if response.session:
                self.access_token = response.session.access_token
                self.refresh_token = response.session.refresh_token
                self.is_authenticated = True
                self.user = response.user
                self.is_loading = False
                yield rx.redirect("/")
                return
        except Exception as e:
            msg = getattr(e, "message", None) or str(e)
            if "Email not confirmed" in msg or "email not confirmed" in msg:
                self.error_message = "이메일 인증 후 로그인하세요."
            elif "Invalid login credentials" in msg or "invalid login credentials" in msg:
                self.error_message = "이메일 또는 비밀번호가 잘못되었습니다."
            else:
                self.error_message = f"로그인 실패: {msg}"
        self.is_loading = False
        yield
        
    async def handle_logout(self):
        self.access_token = ""
        self.refresh_token = ""
        self.is_authenticated = False
        self.user = None
        self.supabase_client.auth.sign_out()
        yield rx.redirect("/login")

    async def handle_signup(self, form_data: dict):
        """회원가입 처리."""
        self.is_loading = True
        self.error_message = ""
        self.success_message = ""
        USERNAME_RE = re.compile(r"^[a-z0-9_]{3,20}$")
        
        yield

        try:
            email = (form_data.get("email") or "").strip()
            password = form_data.get("password") or ""
            password_confirm = form_data.get("password_confirm") or ""
            raw_username = (form_data.get("username") or "").strip()
            username = raw_username.lower() if raw_username else None

            if not email or not password:
                self.error_message = "이메일과 비밀번호를 입력하세요."
                self.is_loading = False
                yield
                return
            if password != password_confirm:
                self.error_message = "비밀번호 확인이 일치하지 않습니다."
                self.is_loading = False
                yield
                return
            if username and not USERNAME_RE.fullmatch(username):
                self.error_message = "사용자명 형식 오류: 3~20자 영문소문자/숫자/_"
                self.is_loading = False
                yield
                return

            resp = self.supabase_client.auth.sign_up({"email": email, "password": password})
            user = getattr(resp, "user", None) or (resp.get("user") if isinstance(resp, dict) else None)
            session = getattr(resp, "session", None) or (resp.get("session") if isinstance(resp, dict) else None)

            if not user:
                self.error_message = "회원가입에 실패했습니다."
                self.is_loading = False
                yield
                return

            if session and getattr(session, "access_token", None) or (isinstance(session, dict) and session.get("access_token")):
                access_token = getattr(session, "access_token", None) or session["access_token"]
                refresh_token = getattr(session, "refresh_token", None) or session.get("refresh_token")

                try:
                    if hasattr(self.supabase_client, "postgrest"):
                        self.supabase_client.postgrest.auth(access_token)
                    if hasattr(self.supabase_client, "auth") and hasattr(self.supabase_client.auth, "set_session") and refresh_token:
                        self.supabase_client.auth.set_session({
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                        })
                except Exception:
                    pass

                row = {"id": getattr(user, "id", None) or user.get("id")}
                if username:
                    row["username"] = username
                bio = (form_data.get("bio") or "").strip()
                if bio:
                    row["bio"] = bio

                try:
                    self.supabase_client.table("profiles").upsert(row).execute()
                except Exception as e:
                    msg = str(e).lower()
                    if "unique" in msg or "duplicate" in msg or "23505" in msg:
                        self.error_message = "이미 사용 중인 사용자명입니다."
                    else:
                        self.error_message = f"프로필 저장 실패: {str(e)}"
                    self.is_loading = False
                    yield
                    return

                try:
                    async for _ in self.handle_login({"email": email, "password": password}):
                        yield _
                    return
                except Exception:
                    self.success_message = "회원가입 완료. 대시보드로 이동을 시도했으나 세션 동기화가 필요합니다."
                    print("회원가입 완료. 대시보드로 이동을 시도했으나 세션 동기화가 필요합니다.")
                    self.is_loading = False
                    yield
                    return

            self.success_message = "회원가입 성공. 이메일 인증을 완료하세요."
            print("회원가입 성공. 이메일 인증을 완료하세요.")
            self.is_loading = False
            yield rx.redirect("/login?verify=email")
            return

        except Exception as e:
            code = getattr(e, "status", None) or getattr(e, "code", None)
            self.error_message = f"회원가입 실패[{code}]: {str(e)}"
            self.is_loading = False
            yield
            return
