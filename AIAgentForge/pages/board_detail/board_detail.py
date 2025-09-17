# AIAgentForge/pages/board_detail/board_detail.py
import reflex as rx
from AIAgentForge.state.language_state import LanguageState  # 추가
from AIAgentForge.state.post_state import PostState
from AIAgentForge.state.auth_state import AuthState
from AIAgentForge.components.navbar import navbar

def post_list() -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell(LanguageState.t["column_title"]),
                rx.table.column_header_cell(LanguageState.t["column_created_at"]),
            )
        ),
        rx.table.body(
            rx.foreach(
                PostState.posts,
                lambda post: rx.table.row(
                    rx.table.cell(post["title"]),
                    rx.table.cell(post["created_at"]),
                    on_click=PostState.go_to_post(post["id"]),
                    _hover={"cursor": "pointer", "background_color": rx.color("gray", 3)},
                )
            )
        ),
        width="100%",
    )

@rx.page(route="/boards/[board_id]", on_load=[AuthState.check_auth, PostState.load_board_and_posts])
def board_detail_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                rx.vstack(
                    rx.heading(PostState.board_name, size="8"),
                    rx.text(PostState.board_description, color_scheme="gray"),
                    align="start",
                    width="100%",
                    margin_bottom="1.5em",
                ),
                rx.hstack(
                    rx.form(
                        rx.hstack(
                            rx.input(
                                value=rx.cond(PostState.search_query, PostState.search_query, ""),
                                on_change=PostState.set_search_query,
                                placeholder=LanguageState.t["search_placeholder"],
                            ),
                            rx.button(LanguageState.t["btn_search"], type="submit"),
                        ),
                        on_submit=PostState.handle_search,
                    ),
                    rx.spacer(),
                    rx.link(
                        rx.button(LanguageState.t["btn_write_post"], white_space="nowrap"),
                        href="/new-post/" + PostState.curr_board_id,
                    ),
                    width="100%",
                    margin_bottom="1.5em",
                ),
                rx.cond(PostState.is_loading, rx.center(rx.spinner(), height="30vh"), post_list()),
                spacing="5",
            ),
            padding_y="2em",
            max_width="960px",
        ),
    )
