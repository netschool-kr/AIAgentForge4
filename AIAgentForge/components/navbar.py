# AIAgentForge/components/navbar.py

import reflex as rx
from AIAgentForge.state.auth_state import AuthState
from AIAgentForge.state.language_state import LanguageState


class NavBarState(rx.State):
    mobile_open: bool = False

    def toggle(self):
        self.mobile_open = not self.mobile_open

    def close(self):
        self.mobile_open = False


def _authed_link_items() -> list[tuple[str, str]]:
    return [
        (LanguageState.t["nav_dashboard"], "/"),
        (LanguageState.t["nav_boards"], "/boards"),
        (LanguageState.t["nav_collections"], "/collections"),
        (LanguageState.t["nav_chat"], "/chat"),
        (LanguageState.t["nav_youtube"], "/youtube"),
        (LanguageState.t["nav_blog"], "/blog"),
        (LanguageState.t["nav_research"], "/research"),
    ]


def _desktop_links() -> rx.Component:
    return rx.hstack(
        *[rx.link(text, href=href) for text, href in _authed_link_items()],
        rx.cond(
            AuthState.role == "admin",
            rx.link(LanguageState.t["nav_admin_panel"], href="/admin"),
        ),
        rx.spacer(),
        rx.text(AuthState.user.email),
        rx.button(LanguageState.t["logout_button"], on_click=AuthState.handle_logout),
        spacing="4",
        align="center",
    )


def _desktop_guest_links() -> rx.Component:
    return rx.hstack(
        rx.link(LanguageState.t["login_link"], href="/login"),
        rx.link(LanguageState.t["signup_link"], href="/signup"),
        spacing="4",
        align="center",
    )


def _mobile_menu() -> rx.Component:
    return rx.cond(
        NavBarState.mobile_open,
        rx.box(
            rx.vstack(
                rx.cond(
                    AuthState.is_authenticated,
                    rx.vstack(
                        *[
                            rx.link(text, href=href, on_click=NavBarState.close)
                            for text, href in _authed_link_items()
                        ],
                        rx.cond(
                            AuthState.role == "admin",
                            rx.link(LanguageState.t["nav_admin_panel"], href="/admin", on_click=NavBarState.close),
                        ),
                        rx.text(AuthState.user.email),
                        rx.button(
                            LanguageState.t["logout_button"],
                            on_click=[AuthState.handle_logout, NavBarState.close],
                        ),
                        align_items="start",
                        spacing="3",
                    ),
                    rx.vstack(
                        rx.link(LanguageState.t["login_link"], href="/login", on_click=NavBarState.close),
                        rx.link(LanguageState.t["signup_link"], href="/signup", on_click=NavBarState.close),
                        align_items="start",
                        spacing="3",
                    ),
                ),
                padding="0.75em",
                width="100%",
            ),
            background_color="white",
            border=f"1px solid {rx.color('gray', 4)}",
            border_radius="md",
            width="100%",
        ),
    )


def navbar() -> rx.Component:
    return rx.vstack(
        # 상단 바
        rx.hstack(
            rx.link("AIAgentForge", href="/", font_weight="bold"),
            rx.spacer(),
            # 데스크톱: 전체 링크 노출
            rx.desktop_only(
                rx.cond(
                    AuthState.is_authenticated,
                    _desktop_links(),
                    _desktop_guest_links(),
                )
            ),
            # 모바일: 메뉴 버튼만 노출
            rx.mobile_only(
                rx.button(LanguageState.t["nav_menu"], on_click=NavBarState.toggle)
            ),
            position="sticky",
            top="0",
            padding="1em",
            width="100%",
            z_index="10",
            background_color=rx.color("gray", 2),
            align="center",
        ),
        # 모바일 드롭다운 메뉴
        rx.mobile_only(_mobile_menu()),
        width="100%",
        background_color=rx.color("gray", 2),
    )
