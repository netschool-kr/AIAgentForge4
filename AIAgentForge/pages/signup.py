# AIAgentForge/pages/signup.py
import reflex as rx
from AIAgentForge.state.auth_state import AuthState
from AIAgentForge.state.language_state import LanguageState

def _signup_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input(
                placeholder=LanguageState.t["email_placeholder"],
                name="email",
                type="email",
                required=True,
                width="100%",
            ),
            rx.input(
                placeholder=LanguageState.t["password_placeholder"],
                name="password",
                type="password",
                required=True,
                width="100%",
            ),
            rx.input(
                placeholder=LanguageState.t["password_confirm_placeholder"],
                name="password_confirm",
                type="password",
                required=True,
                width="100%",
            ),
            rx.button(
                LanguageState.t["signup_button"],
                type="submit",
                is_loading=AuthState.is_loading,
                width="100%",
            ),
            rx.button("Google로 계속", on_click=lambda: AuthState.oauth_start("google")),
            rx.button("Kakao로 계속", on_click=lambda: AuthState.oauth_start("kakao"), width="100%"),
            spacing="4",
            width="100%",
        ),
        on_submit=AuthState.handle_signup,
    )

def _auth_footer() -> rx.Component:
    return rx.vstack(
        rx.cond(
            AuthState.error_message != "",
            rx.callout(
                AuthState.error_message,
                icon="triangle_alert",
                color_scheme="red",
                width="100%",
                margin_top="1em",
            ),
        ),
        rx.text(
            LanguageState.t["already_have_account"],
            rx.link(LanguageState.t["login_link"], href="/login"),
            LanguageState.t["question_mark"],
            margin_top="1em",
        ),
        rx.hstack(
            rx.button("한국어", on_click=lambda: LanguageState.set_locale("ko")),
            rx.button("English", on_click=lambda: LanguageState.set_locale("en")),
            rx.button("日本語", on_click=lambda: LanguageState.set_locale("ja")),
            spacing="4",
        ),
        width="100%",
        spacing="4",
        align="center",
    )

def _mobile_signup() -> rx.Component:
    return rx.flex(
        rx.vstack(
            rx.heading(LanguageState.t["signup"], size="7"),
            rx.card(
                rx.vstack(
                    _signup_form(),
                    _auth_footer(),
                    spacing="3",
                    width="100%",
                ),
                width="100%",
            ),
            width="100%",
            max_width="26em",
            spacing="4",
            align="center",
        ),
        direction="column",
        align="center",     # 가로 가운데
        justify="start",    # 세로 상단 정렬
        min_height="100vh",
        padding_x="1em",
        padding_top="0.75em",
    )

def _desktop_signup() -> rx.Component:
    return rx.flex(
        rx.vstack(
            rx.heading(LanguageState.t["signup"], size="8"),
            _signup_form(),
            _auth_footer(),
            spacing="4",
            align="center",
            width="25em",
        ),
        direction="column",
        align="center",
        justify="start",
        min_height="100vh",
        padding_top="1.5em",
    )

def signup_page() -> rx.Component:
    return rx.fragment(
        rx.mobile_only(_mobile_signup()),
        rx.desktop_only(_desktop_signup()),
    )
