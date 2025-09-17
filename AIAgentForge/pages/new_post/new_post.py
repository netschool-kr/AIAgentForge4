import reflex as rx
from AIAgentForge.state.language_state import LanguageState  # 추가
from AIAgentForge.state.post_state import PostState
from AIAgentForge.state.auth_state import AuthState
from AIAgentForge.components.navbar import navbar

def new_post_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input(
                placeholder=LanguageState.t["input_title_placeholder"],
                on_change=PostState.set_title,
                required=True,
                width="100%",
            ),
            rx.text_area(
                placeholder=LanguageState.t["input_content_placeholder"],
                on_change=PostState.set_content,
                required=True,
                width="100%",
                height="25em",
            ),
            rx.hstack(
                rx.button(
                    LanguageState.t["btn_cancel"],
                    on_click=rx.redirect("/boards/" + PostState.board_id),
                    color_scheme="gray",
                    variant="soft",
                ),
                rx.button(LanguageState.t["btn_submit_post"], type="submit"),
                spacing="4",
                justify="end",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        on_submit=PostState.create_post,
        width="100%",
    )

@rx.page(route="/new-post/[board_id]", on_load=[AuthState.check_auth, PostState.load_board_details])
def new_post_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                rx.vstack(
                    rx.heading(LanguageState.t["new_post_heading"], size="8"),
                    rx.text(f"{LanguageState.t['current_board_label']} {PostState.board_name}",
                        color_scheme="gray",
                    ),
                    align="start",
                    width="100%",
                    margin_bottom="1.5em",
                ),
                new_post_form(),
                spacing="5",
            ),
            padding_y="2em",
            max_width="960px",
        ),
    )
