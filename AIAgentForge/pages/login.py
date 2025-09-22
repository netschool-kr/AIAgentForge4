# AIAgentForge/pages/login.py
import reflex as rx
from AIAgentForge.state.auth_state import AuthState
from AIAgentForge.state.language_state import LanguageState

def _login_form() -> rx.Component:
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
            rx.button(
                LanguageState.t["login_button"],
                type="submit",
                is_loading=AuthState.is_loading,
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        on_submit=AuthState.handle_login,
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
            LanguageState.t["no_account_yet"],
            rx.link(LanguageState.t["signup_link"], href="/signup"),
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

def _mobile_login() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading(LanguageState.t["login"], size="6"),
            rx.card(
                rx.vstack(
                    _login_form(),
                    _auth_footer(),
                    spacing="3",
                    width="100%",
                ),
                width="100%",
            ),
            padding_x="1em",
            width="100%",
            max_width="26em",
            spacing="4",
            align="center",
        ),
        height="70vh",
    )

def _desktop_login() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading(LanguageState.t["login"], size="5"),
            _login_form(),
            _auth_footer(),
            spacing="5",
            align="center",
            width="25em",
        ),
        height="50vh",
    )

def login_page() -> rx.Component:
    return rx.fragment(
        rx.mobile_only(_mobile_login()),
        rx.desktop_only(_desktop_login()),
    )
