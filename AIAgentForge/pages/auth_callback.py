# AIAgentForge/pages/auth_callback.py
import reflex as rx

def auth_callback_page() -> rx.Component:
    return rx.fragment(
        rx.text("소셜 로그인 처리 중..."),
        rx.text(rx.heading("잘못된 URL로 접근했습니다."),
                rx.link("로그인 페이지로 돌아가기", href="/login")),
    )