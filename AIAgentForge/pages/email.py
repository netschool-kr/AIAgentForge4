# AIAgentForge/pages/email.py
import reflex as rx
from ..state.email_state import EmailState

def email_page():
    return rx.vstack(
        rx.heading("회원 이메일 전송 시스템", size="7"),
        rx.button("회원 이메일 목록 불러오기",
            on_click=EmailState.fetch_emails,
            is_loading=EmailState.is_loading
        ),
        rx.text(f"대상: {rx.cond(EmailState.emails, EmailState.emails.length().to_string() + '명', '0명')}"),
        rx.form.root(
            rx.vstack(
                rx.input(placeholder="이메일 제목", name="subject", required=True, width="100%"),
                rx.text_area(placeholder="이메일 내용 (HTML 형식)", name="html_content", required=True, width="100%", height="200px"),
                rx.form.submit(
                    rx.button("모든 회원에게 전송", type="submit", is_loading=EmailState.is_loading),
                    as_child=True,
                ),
                width="100%"
            ),
            on_submit=EmailState.send_emails,
            width="100%",
            padding_x="4em",
        ),
        rx.cond(EmailState.message, rx.callout(EmailState.message)),
        spacing="5",
        align="center",
        padding_top="5em",
    )

