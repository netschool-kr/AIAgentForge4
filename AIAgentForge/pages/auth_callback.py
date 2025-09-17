# pages/auth_callback.py
import reflex as rx
from AIAgentForge.state.auth_state import AuthState

def auth_callback_page() -> rx.Component:
    # 페이지 로드시 code 파라미터를 읽어 처리
    return rx.fragment(
        rx.script("""
        (function(){
          const u = new URL(window.location.href);
          const code = u.searchParams.get('code');
          if (code) {
            window.pywebview.api.call_event("AuthState.oauth_callback", {code: code});
          } else {
            window.location.href = "/login";
          }
        })();
        """)
    )
