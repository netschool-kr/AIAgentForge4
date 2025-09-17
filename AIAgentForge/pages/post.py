from AIAgentForge.state.language_state import LanguageState  # 추가

@rx.page(route="/posts/[post_id]", on_load=PostDetailState.load_post, title="게시글")
def post_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.container(
            rx.cond(
                PostDetailState.is_loading,
                rx.center(rx.spinner(), height="50vh"),
                rx.vstack(
                    rx.vstack(
                        rx.heading(PostDetailState.post.get("title", LanguageState.t["title_untitled"]), size="8"),
                        rx.hstack(
                            rx.text(f"{LanguageState.t['author_label']} {PostDetailState.post.get('author_email', LanguageState.t['author_unknown'])}", size="3", color_scheme="gray"),
                            rx.spacer(),
                            rx.text(f"{LanguageState.t['created_at_label']} {PostDetailState.formatted_created_at}", size="3", color_scheme="gray"),
                            width="100%",
                            padding_y="0.5em",
                        ),
                        align="start",
                        width="100%",
                        border_bottom="1px solid #EAEAEA",
                        padding_bottom="1em",
                        margin_bottom="2em",
                    ),
                    rx.box(
                        rx.markdown(PostDetailState.post.get("content", LanguageState.t["content_none"])),
                        min_height="30vh",
                        width="100%",
                        padding_y="1em",
                    ),
                    rx.hstack(
                        rx.link(
                            rx.button(LanguageState.t["btn_back_to_list"], variant="soft"),
                            href=f"/boards/{PostDetailState.post.get('board_id', '')}",
                        ),
                        rx.spacer(),
                        rx.cond(
                            PostDetailState.is_author,
                            rx.hstack(
                                rx.link(rx.button(LanguageState.t["btn_edit"], color_scheme="blue"), href="#"),
                                rx.button(LanguageState.t["btn_delete"], on_click=PostDetailState.delete_post, color_scheme="red"),
                                spacing="3",
                            ),
                        ),
                        width="100%",
                        margin_top="2em",
                    ),
                    spacing="5",
                    width="100%",
                    padding_top="2em",
                ),
            ),
            padding_x="1em",
            max_width="960px",
        ),
    )
