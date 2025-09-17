# AIAgentForge/state/auth_state.py
import reflex as rx
from .base import BaseState
from dotenv import load_dotenv
import urllib

class AuthState(BaseState):
    """
    Handles all authentication logic including login, logout, signup,
    and checking the authentication status on page loads.
    """

    SITE_URL = load_dotenv("SITE_URL")          # 배포 도메인
    REDIRECT_URI = f"{SITE_URL}/auth/callback"  # Supabase 대시보드와 동일해야 함
    # JWT tokens stored in browser cookies for session persistence.
    access_token: str = rx.Cookie("")
    refresh_token: str = rx.Cookie("")
    
    # State for UI feedback during auth operations.
    error_message: str = ""
    is_loading: bool = False

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
        """Handles the login form submission."""
        self.is_loading = True
        self.error_message = ""
        yield

        try:
            response = self.supabase_client.auth.sign_in_with_password(
                {"email": form_data["email"], "password": form_data["password"]}
            )
            if response.session:
                # Success! Set cookies and server state.
                self.access_token = response.session.access_token
                self.refresh_token = response.session.refresh_token
                self.is_authenticated = True
                self.user = response.user
                self.is_loading = False
                # Yield the redirect event instead of returning it.
                yield rx.redirect("/")
                # Use a bare return to exit the generator.
                return
        except Exception:
            self.error_message = "이메일 또는 비밀번호가 잘못되었습니다."
        
        # This part only runs if login fails.
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
        """Handles the signup form submission."""
        self.is_loading = True
        self.error_message = ""
        yield

        try:
            response = self.supabase_client.auth.sign_up(
                {"email": form_data["email"], "password": form_data["password"]}
            )
            if response.user:
                # Depending on your Supabase settings, a session might be returned directly.
                if response.session:
                    # Delegate event handling to handle_login.
                    # We must iterate over the async generator and yield its events.
                    async for event in self.handle_login(form_data):
                        yield event
                    return
                else:
                    self.error_message = "회원가입 성공! 확인 이메일을 확인해주세요."
            else:
                self.error_message = "회원가입에 실패했습니다."
        except Exception as e:
            self.error_message = f"오류 발생: {getattr(e, 'message', str(e))}"
        
        self.is_loading = False
        yield

    async def oauth_start(self, provider_label: str):
        SUPPORTED = {"google": "google", "kakao": "kakao"}  # 오타 방지 매핑
        provider = SUPPORTED.get(provider_label.lower())
        if not provider:
            self.error_message = "지원하지 않는 소셜 로그인입니다."
            return
        qs = urllib.parse.urlencode({
            "provider": provider,
            "redirect_to": REDIRECT_URI,          # 예: https://<도메인>/auth/callback
            "scopes": "openid profile email",
        })
        yield rx.redirect(f"{SUPABASE_URL}/auth/v1/authorize?{qs}")
    
    async def oauth_start(self, provider: str):
        # 권장: provider별 authorize URL로 리디렉트 (scopes에 openid 포함)
        from urllib.parse import urlencode, quote
        qs = urlencode({
            "provider": provider,
            "redirect_to": self.REDIRECT_URI,
            "scopes": "openid profile email",
        })
        authorize_url = f"{self.SUPABASE_URL}/auth/v1/authorize?{qs}"
        yield rx.redirect(authorize_url)

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