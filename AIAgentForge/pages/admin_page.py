# AIAgentForge/pages/admin_page.py
import reflex as rx
from AIAgentForge.state.admin_state import AdminState
from AIAgentForge.state.language_state import LanguageState
from AIAgentForge.components.navbar import navbar
from .email import email_page


def board_management_content() -> rx.Component:
    return rx.vstack(
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
                        lambda b: rx.table.row(
                            rx.table.cell(b.get("name", "")),
                            rx.table.cell(b.get("description", "")),
                            rx.table.cell(b.get("read_permission", "")),
                            rx.table.cell(b.get("write_permission", "")),
                            rx.table.cell(
                                rx.button(
                                    LanguageState.t["btn_delete"],
                                    on_click=lambda: AdminState.delete_board(b["id"]),
                                    color_scheme="red",
                                    size="1",
                                )
                            ),
                        ),
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

def user_management_content() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("사용자 관리", size="5"),
            rx.spacer(),
            rx.button("새로고침", on_click=lambda: AdminState.load_all_users(), size="1"),
            align="center",
            width="100%",
        ),
        rx.cond(
            AdminState.is_loading_users,
            rx.center(rx.spinner()),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("이메일"),
                        rx.table.column_header_cell("생성일"),
                        rx.table.column_header_cell("최근 로그인"),
                        rx.table.column_header_cell("작업"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        AdminState.all_users,
                        lambda u: rx.table.row(
                            rx.table.cell(u.get("email", "")),
                            rx.table.cell(u.get("created_at", "")),
                            rx.table.cell(u.get("last_sign_in_at", "")),
                            rx.table.cell(
                                rx.hstack(
                                    rx.button(
                                        "수정",
                                        on_click=lambda _: AdminState.open_user_editor(u["id"]),   # 렌더 타임 실행 방지
                                        size="1",
                                    ),

                                    rx.button(
                                        "삭제",
                                        color_scheme="red",
                                        on_click=lambda _: AdminState.delete_user(u["id"]),        # 이벤트 인자 무시
                                        size="1",
                                    ),
                                    spacing="2",
                                )
                            ),
                        )
                    )
                ),
                variant="surface",
                width="100%",
            ),
        ),
        rx.dialog.root(
            rx.dialog.content(
                rx.vstack(
                    rx.heading("사용자 정보 수정", size="4"),
                    rx.vstack(
                        rx.input(
                            name="email",
                            placeholder="이메일",
                            value=AdminState.edit_email,
                            on_change=AdminState.set_edit_email,
                        ),
                        rx.input(
                            name="username",
                            placeholder="username",
                            value=AdminState.edit_username,
                            on_change=AdminState.set_edit_username,
                        ),
                        rx.input(
                            name="full_name",
                            placeholder="full_name",
                            value=AdminState.edit_full_name,
                            on_change=AdminState.set_edit_full_name,
                        ),
                        rx.input(
                            name="avatar_url",
                            placeholder="avatar_url",
                            value=AdminState.edit_avatar_url,
                            on_change=AdminState.set_edit_avatar_url,
                        ),
                        rx.hstack(
                            rx.button("취소", variant="soft", on_click=AdminState.cancel_user_editor),
                            rx.button("저장", on_click=AdminState.save_user),
                            spacing="3",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    spacing="4",
                    width="28rem",
                )
            ),
            open=AdminState.editor_open,
            on_open_change=AdminState.set_editor_open,
        ),
        spacing="5",
        width="100%",
        padding_x="2em",
        padding_y="2em",
    )


@rx.page(route="/admin", on_load=AdminState.on_load_admin)
def admin_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            rx.heading(LanguageState.t["admin_dashboard_title"], size="8", margin_bottom="1em"),
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger(LanguageState.t["tab_main"], value="main"),
                    rx.tabs.trigger(LanguageState.t["tab_board_management"], value="board_management"),
                    rx.tabs.trigger("사용자 관리", value="user_management"),
                    rx.tabs.trigger(LanguageState.t["tab_email"], value="email"),
                    width="100%",
                ),
                rx.tabs.content(
                    rx.vstack(rx.text(LanguageState.t["admin_only_notice"]), width="100%", padding_x="4em", padding_y="4em"),
                    value="main",
                    width="100%",
                ),
                rx.tabs.content(board_management_content(), value="board_management", width="100%"),
                rx.tabs.content(user_management_content(), value="user_management", width="100%"),
                rx.tabs.content(email_page(), value="email", width="100%"),
                defaultValue="main",
                width="100%",
            ),
            padding_x="2em",
            padding_y="2em",
        ),
        width="100%",
    )
