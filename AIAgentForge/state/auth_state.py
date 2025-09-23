# AIAgentForge/state/auth_state.py
import reflex as rx
from .base import BaseState
import os
import urllib
import re

class AuthState(BaseState):
    """
    Handles all authentication logic including login, logout, signup,
    and checking the authentication status on page loads.
    """

    # IMPORTANT: Ensure these environment variables are set in your .env file.
    # .env 파일에 아래 환경 변수들을 반드시 설정해야 합니다.
    # SUPABASE_URL="https://your-project-ref.supabase.co"
    # SUPABASE_KEY="your-anon-public-key"
    # SITE_URL="http://localhost:3000" (or your production domain)
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SITE_URL = os.getenv("SITE_URL")          # 배포 도메인
    REDIRECT_URI = f"{SITE_URL}/auth/callback"  # Supabase 대시보드와 동일해야 함

    # JWT tokens stored in browser cookies for session persistence.
    access_token: str = rx.Cookie("")
    refresh_token: str = rx.Cookie("")
    
    # State for UI feedback during auth operations.
    error_message: str = ""
    success_message: str = ""
    is_loading: bool = False

    username_input: str = ""
    username_checking: bool = False
    username_available: bool | None = None
    username_message: str = ""

    @rx.event
    def oauth_start(self, provider: str):
        """Supabase OAuth 시작: Google 등."""
        if not self.SUPABASE_URL or not self.SITE_URL:
            self.error_message = "환경변수 누락: SUPABASE_URL, SITE_URL"
            yield
            return
        redirect_to = f"{self.SITE_URL}/auth/callback"
        qs = {
            "provider": provider,
            "redirect_to": redirect_to,
            # 필요 시 scope, prompt 등 추가 가능
            # "scopes": "email profile",
            # "prompt": "consent",
        }
        url = (
            f"{self.SUPABASE_URL}/auth/v1/authorize?"
            + urllib.parse.urlencode(qs, safe="/:")
        )
        # 외부 URL 이동
        yield rx.redirect(url, external=True)
            
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
        # 패턴 검사(서버측과 동일)
        import re
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
            # 대소문자 무시 비교를 위해 서버는 소문자 인덱스로 보장. 여기선 eq로 충분.
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
        """Returns the user's email if they are logged in, otherwise an empty string."""
        return self.user.email if self.user else ""

    @rx.var
    def role(self) -> str:
        """
        인증된 사용자의 역할을 반환하는 계산 변수입니다.
        역할이 없거나 비로그인 상태일 경우 'guest'를 반환합니다.
        """
        if self.is_authenticated and self.user and self.user.app_metadata:
            return self.user.app_metadata.get("role", "user")
        return "guest"
    
    async def check_auth(self):
        """
        Verifies authentication on page load for protected routes.
        This is the single source of truth for auth status.
        It runs every time a protected page is loaded.
        """
        # If there is no access token in the cookie, the user is not logged in.
        if not self.access_token:
            # If server state is out of sync, reset it.
            if self.is_authenticated:
                self.is_authenticated = False
                self.user = None
            yield rx.redirect("/login")
            return

        try:
            # The token exists. Verify its validity by fetching the user from Supabase.
            response = self.supabase_client.auth.get_user(self.access_token)
            if response and response.user:
                self.user = response.user
                self.is_authenticated = True
                yield
            else:
                # get_user가 user를 반환하지 않는 예외적인 경우
                raise Exception("User not found with the given token.")

        except Exception:
            # 3. get_user 실패: access_token이 만료되었거나 유효하지 않다는 의미입니다.
            # 이제 refresh_token으로 세션 갱신을 시도합니다.
            if not self.refresh_token:
                # 갱신 토큰조차 없으면 완전히 로그아웃 처리합니다.
                self._reset_auth_state()
                yield rx.redirect("/login")

            try:
                # 4. refresh_token으로 새로운 세션(access_token + refresh_token)을 요청합니다.
                response = await self.supabase_client.auth.refresh_session(self.refresh_token)

                # 5. 세션 갱신 성공: 새로운 토큰들로 상태를 업데이트합니다 (토큰 로테이션).
                if response.session:
                    self.access_token = response.session.access_token
                    self.refresh_token = response.session.refresh_token
                    self.user = response.user
                    self.is_authenticated = True
                    yield
                else:
                    raise Exception("Session refresh did not return a session.")

            except Exception:
                # 6. 세션 갱신 실패: refresh_token도 만료되었거나 유효하지 않습니다.
                # 모든 인증 정보를 지우고 로그인 페이지로 보냅니다.
                self._reset_auth_state()
                yield rx.redirect("/login")
                
    async def check_admin(self):
        """관리자 페이지 접근을 위한 인증 및 권한을 확인합니다."""
        # 1단계: 사용자가 로그인했는지 먼저 확인합니다.
        # check_auth의 이벤트를 체이닝하여 yield합니다. (리디렉션이 발생하면 여기서 중단됨)
        async for event in self.check_auth():
            yield event

        # 2단계: 로그인한 사용자의 역할이 'admin'이 아닌 경우, 메인 페이지로 리디렉션합니다.
        if self.role != "admin":
            yield rx.redirect("/")
        return  # 리디렉션 후 불필요한 실행 방지
            
    def _reset_auth_state(self):
        """인증 관련 모든 상태를 깨끗하게 초기화하는 헬퍼 메서드."""
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
        """Logs the user out, clears all state, and redirects."""
        self.access_token = ""
        self.refresh_token = ""
        self.is_authenticated = False
        self.user = None
        # Inform Supabase to invalidate the token on the server.
        self.supabase_client.auth.sign_out()
        yield rx.redirect("/login")




    async def handle_signup(self, form_data: dict):
        """회원가입 처리.
        - 비번 확인
        - username 정규식 검사(옵션)
        - supabase.auth.sign_up
        - 세션 있으면 JWT로 profiles upsert (RLS 통과)
        - 세션 없으면 이메일 인증 안내 (profiles는 DB 트리거가 생성)
        """
        # UI 상태 초기화
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

            # 기본 유효성
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

            # 회원가입
            resp = self.supabase_client.auth.sign_up({"email": email, "password": password})

            # supabase-py v2/구버전 호환 처리
            user = getattr(resp, "user", None) or (resp.get("user") if isinstance(resp, dict) else None)
            session = getattr(resp, "session", None) or (resp.get("session") if isinstance(resp, dict) else None)

            if not user:
                self.error_message = "회원가입에 실패했습니다."
                self.is_loading = False
                yield
                return

            # 세션이 있으면 JWT로 RLS 통과 후 profiles upsert
            if session and getattr(session, "access_token", None) or (isinstance(session, dict) and session.get("access_token")):
                access_token = getattr(session, "access_token", None) or session["access_token"]
                refresh_token = getattr(session, "refresh_token", None) or session.get("refresh_token")

                # PostgREST에 JWT 주입
                try:
                    # supabase-py v2
                    if hasattr(self.supabase_client, "postgrest"):
                        self.supabase_client.postgrest.auth(access_token)
                    # 일부 구버전 호환
                    if hasattr(self.supabase_client, "auth") and hasattr(self.supabase_client.auth, "set_session") and refresh_token:
                        self.supabase_client.auth.set_session({
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                        })
                except Exception:
                    # 주입 실패해도 아래 upsert가 실패하면 예외로 처리
                    pass

                # profiles upsert (username 유니크는 DB 인덱스가 보장)
                row = {"id": getattr(user, "id", None) or user.get("id")}
                if username:
                    row["username"] = username

                try:
                    self.supabase_client.table("profiles").upsert(row).execute()
                except Exception as e:
                    # 유니크 위반 등 처리
                    msg = str(e).lower()
                    if "unique" in msg or "duplicate" in msg or "23505" in msg:
                        self.error_message = "이미 사용 중인 사용자명입니다."
                    else:
                        self.error_message = f"프로필 저장 실패: {str(e)}"
                    self.is_loading = False
                    yield
                    return

                # 바로 로그인 흐름 유지
                # (이미 세션이 있더라도 기존 로직을 재사용하려면 호출)
                try:
                    async for _ in self.handle_login({"email": email, "password": password}):
                        yield _
                    return
                except Exception:
                    # 로그인 재호출 실패 시에도 가입은 완료
                    self.success_message = "회원가입 완료. 대시보드로 이동을 시도했으나 세션 동기화가 필요합니다."
                    print("회원가입 완료. 대시보드로 이동을 시도했으나 세션 동기화가 필요합니다.")
                    self.is_loading = False
                    yield
                    return

            # 세션이 없는 경우: 이메일 인증 후 첫 로그인 때 사용
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

    async def oauth_start(self, provider: str):
        from urllib.parse import urlencode
        # Supabase 대시보드에서 Google OAuth를 활성화하고,
        # 클라이언트 ID와 시크릿을 추가해야 합니다.
        # 또한, `REDIRECT_URI`를 `your-project-ref.supabase.co/auth/v1/callback`에 추가해야 합니다.
        if not self.SUPABASE_URL or not self.REDIRECT_URI:
            self.error_message = "OAuth 설정 오류(SUPABASE_URL / SITE_URL)."
            yield
            return
        qs = urlencode({
            "provider": provider,
            "redirect_to": self.REDIRECT_URI,
            "scopes": "openid profile email",
        })
        yield rx.redirect(f"{self.SUPABASE_URL}/auth/v1/authorize?{qs}")
        
    async def oauth_callback(self, code: str):
        # PKCE 코드 -> 세션 교환
        resp = self.supabase_client.auth.exchange_code_for_session({"auth_code": code})
        if resp.session:
            self.access_token  = resp.session.access_token
            self.refresh_token = resp.session.refresh_token
            self.user = resp.user
            self.is_authenticated = True
            yield rx.redirect("/")
        else:
            self.error_message = "소셜 로그인에 실패했습니다."
            yield rx.redirect("/login")
