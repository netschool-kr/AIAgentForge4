# AIAgentForge/pages/admin_page.py
import reflex as rx
from AIAgentForge.state.admin_state import AdminState
from .email import email_page
from AIAgentForge.components.navbar import navbar
from AIAgentForge.state.language_state import LanguageState  # i18n

def board_management_content() -> rx.Component:
    """게시판 관리 탭 콘텐츠."""
    return rx.vstack(
        # --- 1) 새 게시판 생성 폼 ---
        rx.card(
            rx.form(
                rx.vstack(
                    rx.heading(LanguageState.t["new_board_heading"], size="5"),
                    rx.input(name="name", placeholder=LanguageState.t["input_board_name_placeholder"], required=True),
                    rx.input(name="description", placeholder=LanguageState.t["input_board_desc_placeholder"]),
                    rx.hstack(
                        rx.text(LanguageState.t["label_read_permission"]),
                        rx.select(["guest", "user", "admin"], name="read_permission", default_value="user"),
                        rx.text(LanguageState.t["label_write_permission"]),
                        rx.select(["user", "admin"], name="write_permission", default_value="user"),
                        spacing="3",
                        align="center",
                    ),
                    rx.button(LanguageState.t["btn_create"], type="submit"),
                    spacing="4",
                ),
                on_submit=AdminState.create_board,
                reset_on_submit=True,
            ),
            width="100%",
        ),

        rx.divider(margin_y="2em"),

        # --- 2) 게시판 목록 및 관리 ---
        rx.heading(LanguageState.t["boards_list_heading"], size="5", margin_bottom="1em"),
        rx.cond(
            AdminState.is_loading_boards,
            rx.center(rx.spinner()),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell(LanguageState.t["table_name_header"]),
                        rx.table.column_header_cell(LanguageState.t["table_desc_header"]),
                        rx.table.column_header_cell(LanguageState.t["table_read_perm_header"]),
                        rx.table.column_header_cell(LanguageState.t["table_write_perm_header"]),
                        rx.table.column_header_cell(LanguageState.t["table_actions_header"]),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        AdminState.boards,
                        lambda board: rx.table.row(
                            rx.table.cell(board["name"]),
                            rx.table.cell(board["description"]),
                            rx.table.cell(board["read_permission"]),
                            rx.table.cell(board["write_permission"]),
                            rx.table.cell(
                                rx.button(
                                    LanguageState.t["btn_delete"],
                                    on_click=lambda: AdminState.delete_board(board["id"]),
                                    color_scheme="red",
                                    size="1",
                                )
                            ),
                        )
                    )
                ),
                variant="surface",
                width="100%",
            ),
        ),
        spacing="5",
        width="100%",
        padding_x="2em",
        padding_y="2em",
    )

@rx.page(route="/admin", on_load=AdminState.load_all_boards)
def admin_page() -> rx.Component:
    """관리자 전용 대시보드 UI."""
    return rx.box(
        navbar(),
        rx.box(
            rx.heading(LanguageState.t["admin_dashboard_title"], size="8", margin_bottom="1em"),
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger(LanguageState.t["tab_main"], value="main"),
                    rx.tabs.trigger(LanguageState.t["tab_board_management"], value="board_management"),
                    rx.tabs.trigger(LanguageState.t["tab_email"], value="email"),
                    width="100%",
                ),
                # --- 메인 탭 ---
                rx.tabs.content(
                    rx.vstack(
                        rx.text(LanguageState.t["admin_only_notice"]),
                        width="100%",
                        padding_x="4em",
                        padding_y="4em",
                    ),
                    value="main",
                    width="100%",
                ),
                # --- 게시판 관리 탭 ---
                rx.tabs.content(
                    board_management_content(),
                    value="board_management",
                    width="100%",
                ),
                # --- 이메일 전송 탭 ---
                rx.tabs.content(
                    email_page(),
                    value="email",
                    width="100%",
                ),
                defaultValue="main",
                width="100%",
            ),
            padding_x="2em",
            padding_y="2em",
        ),
        width="100%",
    )
