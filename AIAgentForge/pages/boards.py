# AIAgentForge/pages/boards.py
import reflex as rx
from AIAgentForge.state.board_state import BoardState
from AIAgentForge.state.auth_state import AuthState
from AIAgentForge.components.navbar import navbar
from AIAgentForge.state.language_state import LanguageState  # 추가

def board_card(board: dict) -> rx.Component:
    return rx.link(
        rx.card(
            rx.vstack(
                rx.heading(board["name"], size="5"),
                rx.text(
                    board.get("description", LanguageState.t["board_card_no_desc"]),
                    size="2",
                    color_scheme="gray",
                ),
                spacing="2",
                align="start",
                width="100%",
            ),
            as_child=True,
            width="100%",
            _hover={"background_color": rx.color("gray", 2)},
        ),
        href=f"/boards/{board['id']}",
        on_click=lambda: rx.console_log(f"Navigating to board {board['id']}"),
        width="100%",
    )

@rx.page(route="/boards", on_load=[AuthState.check_auth, BoardState.load_visible_boards])
def boards_page() -> rx.Component:
    return rx.vstack(
        navbar(),
        rx.heading(LanguageState.t["boards_page_title"], size="8", margin_bottom="1em"),
        rx.cond(
            BoardState.is_loading_boards,
            rx.center(rx.spinner(), height="20vh"),
            rx.vstack(
                rx.foreach(BoardState.visible_boards, board_card),
                spacing="4",
                width="100%",
                max_width="800px",
            ),
        ),
        rx.hstack(
            rx.button("한국어", on_click=LanguageState.set_locale("ko")),
            rx.button("English", on_click=LanguageState.set_locale("en")),
            rx.button("日本語", on_click=LanguageState.set_locale("ja")),
            spacing="4",
        ),
        spacing="5",
        align="center",
        padding_y="2em",
        width="100%",
    )
