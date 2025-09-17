# AIAgentForge/AIAgentForge/pages/dashboard.py
import reflex as rx
from AIAgentForge.state.dashboard_state import DashboardState
from AIAgentForge.state.language_state import LanguageState
from AIAgentForge.components.navbar import navbar

def mobile_user_card(user: dict) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text(f"{LanguageState.t['name']}: {user['name']}", font_weight="bold"),
            rx.text(f"{LanguageState.t['age']}: {user['age']}"),
            rx.text(f"{LanguageState.t['role']}: {user['role']}"),
            align_items="start",
            spacing="2"
        ),
        width="100%"
    )

def dashboard_page() -> rx.Component:
    return rx.vstack(
        navbar(),
        rx.heading(LanguageState.t["dashboard_title"], size="8"),
        rx.text(f"{LanguageState.t['total_users']}: {DashboardState.total_users}", size="6"),

        # 모바일용 카드 UI
        rx.mobile_only(
            rx.vstack(
                rx.foreach(DashboardState.users, mobile_user_card),
                width="100%", spacing="4"
            ),
        ),

        # 데스크톱용 테이블 UI
        rx.desktop_only(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell(LanguageState.t["name"]),
                        rx.table.column_header_cell(LanguageState.t["age"]),
                        rx.table.column_header_cell(LanguageState.t["role"]),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        DashboardState.users,
                        lambda user: rx.table.row(
                            rx.table.cell(user["name"]),
                            rx.table.cell(user["age"]),
                            rx.table.cell(user["role"]),
                        ),
                    )
                ),
            ),
        ),

        rx.divider(),
        # 사용자 추가 폼
        rx.form(
            rx.hstack(
                rx.input(placeholder=LanguageState.t["name"], name="name", required=True),
                rx.input(placeholder=LanguageState.t["age"], name="age", type="number", required=True),
                rx.button(LanguageState.t["add_user"], type="submit"),
                justify="center",
            ),
            on_submit=DashboardState.add_user,
            reset_on_submit=True,
        ),

        # 언어 전환 버튼
        rx.hstack(
            rx.button("한국어", on_click=lambda: LanguageState.set_locale("ko")),
            rx.button("English", on_click=lambda: LanguageState.set_locale("en")),
            rx.button("日本語", on_click=lambda: LanguageState.set_locale("ja")),
            spacing="4"
        ),
        spacing="5",
        align="center",
        padding_y="2em",
    )
