# AIAgentForge/pages/posts/post_detail.py

import reflex as rx
from AIAgentForge.components.navbar import navbar
from AIAgentForge.state.post_state import PostDetailState
from AIAgentForge.state.auth_state import AuthState

# --- 댓글 UI 컴포넌트 추가 ---

def comment_form() -> rx.Component:
    """새 댓글 작성을 위한 폼 컴포넌트."""
    return rx.form(
        rx.vstack(
            rx.text_area(
                name="comment_content",
                value=PostDetailState.new_comment_content,
                on_change=PostDetailState.set_new_comment_content,
                placeholder="댓글을 입력하세요...",
                width="100%",
            ),
            rx.button("댓글 작성", type="submit", width="100%"),
            spacing="3",
            width="100%",
        ),
        on_submit=PostDetailState.create_comment,
        width="100%",
    )

def comment_view(comment: dict) -> rx.Component:
    """개별 댓글을 보여주는 컴포넌트."""
    return rx.box(
        rx.hstack(
            rx.text(comment.get("author_email", "익명"), font_weight="bold"),
            rx.text(comment.get("formatted_created_at", ""), color_scheme="gray", size="2"),
            rx.spacer(),
            # 로그인한 사용자가 댓글 작성자일 경우에만 삭제 버튼 표시
            rx.cond(
                AuthState.user.get("id", "") == comment.get("user_id", ""),
                rx.alert_dialog.root(
                    rx.alert_dialog.trigger(
                        rx.icon_button("trash-2", size="1", variant="ghost", color_scheme="red", cursor="pointer")
                    ),
                    rx.alert_dialog.content(
                        rx.alert_dialog.title("댓글 삭제"),
                        rx.alert_dialog.description("정말로 이 댓글을 삭제하시겠습니까?"),
                        rx.flex(
                            rx.alert_dialog.cancel(
                                rx.button("취소", variant="soft", color_scheme="gray")
                            ),
                            rx.alert_dialog.action(
                                rx.button("삭제", color_scheme="red", on_click=lambda: PostDetailState.delete_comment(comment["id"]))
                            ),
                            spacing="3",
                            margin_top="16px",
                            justify="end",
                        ),
                    ),
                ),
            ),
            align="center",
        ),
        rx.text(comment.get("content", "")),
        padding_y="1em",
        width="100%",
    )

def comments_section() -> rx.Component:
    """댓글 목록과 작성 폼을 포함하는 전체 섹션."""
    return rx.vstack(
        rx.heading("댓글", size="5"),
        rx.divider(),
        # 로그인한 사용자에게만 댓글 작성 폼을 보여줌
        rx.cond(
            AuthState.is_authenticated,
            comment_form(),
            rx.center(
                rx.text("댓글을 작성하려면 로그인이 필요합니다.", color_scheme="gray"),
                width="100%",
                padding_y="1em",
            )
        ),
        rx.vstack(
            # 댓글 목록을 순회하며 표시
            rx.foreach(
                PostDetailState.comments,
                comment_view
            ),
            rx.cond(
                # 댓글이 없을 때 메시지 표시
                PostDetailState.no_comments,
                rx.center(
                    rx.text("아직 댓글이 없습니다.", color_scheme="gray"),
                    padding_y="2em",
                )
            ),
            spacing="1",
            width="100%",
        ),
        spacing="4",
        width="100%",
        padding_top="2em",
    )

# ------------------------------------

def post_view() -> rx.Component:
    """게시물 내용을 보여주는 컴포넌트."""
    return rx.vstack(
        rx.heading(PostDetailState.post.get("title", "제목 없음"), size="8"),
        rx.hstack(
            rx.text(f"작성자: {PostDetailState.post.get('author_email', '알 수 없음')}", color_scheme="gray"),
            rx.spacer(),
            rx.text(f"작성일: {PostDetailState.formatted_created_at}", color_scheme="gray"),
            width="100%",
            padding_y="1em",
        ),
        rx.divider(),
        rx.box(
            rx.markdown(PostDetailState.post.get("content", "")), # 마크다운 지원을 위해 rx.markdown 사용
            padding_y="2em",
            width="100%",
            min_height="30vh",
        ),
        align="start",
        width="100%",
    )

def edit_post_view() -> rx.Component:
    """게시물 수정을 위한 폼 컴포넌트."""
    return rx.form(
        rx.vstack(
            rx.input(
                default_value=PostDetailState.post.get("title", ""), 
                name="title",
                width="100%",
            ),
            rx.text_area(
                default_value=PostDetailState.post.get("content", ""), 
                name="content",
                width="100%",
                height="25em",
            ),
            rx.hstack(
                rx.button("취소", on_click=PostDetailState.toggle_edit, color_scheme="gray", variant="soft"),
                rx.button("저장", type="submit"),
                justify="end",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        on_submit=PostDetailState.update_post,
    )

@rx.page(route="/posts/[post_id]", on_load=[AuthState.check_auth, PostDetailState.load_post])
def post_detail_page() -> rx.Component:
    """게시물 상세 정보를 보여주는 페이지."""
    return rx.box(
        navbar(),
        rx.container(
            rx.cond(
                PostDetailState.is_loading,
                rx.center(rx.spinner(), height="80vh"),
                rx.vstack(
                    rx.cond(
                        PostDetailState.is_editing,
                        edit_post_view(),
                        post_view(),
                    ),
                    rx.hstack(
                        rx.link(
                            rx.button("목록으로", variant="soft"),
                            href=f"/boards/{PostDetailState.post.get('board_id', '')}",
                        ),
                        rx.spacer(),
                        rx.cond(
                            PostDetailState.is_author,
                            rx.hstack(
                                rx.button("수정", on_click=PostDetailState.toggle_edit),
                                rx.alert_dialog.root(
                                    rx.alert_dialog.trigger(
                                        rx.button("삭제", color_scheme="red")
                                    ),
                                    rx.alert_dialog.content(
                                        rx.alert_dialog.title("게시물 삭제"),
                                        rx.alert_dialog.description(
                                            "정말로 이 게시물을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다."
                                        ),
                                        rx.flex(
                                            rx.alert_dialog.cancel(
                                                rx.button("취소", variant="soft", color_scheme="gray")
                                            ),
                                            rx.alert_dialog.action(
                                                rx.button("삭제", color_scheme="red", on_click=PostDetailState.delete_post)
                                            ),
                                            spacing="3",
                                            margin_top="16px",
                                            justify="end",
                                        ),
                                    ),
                                ),
                                spacing="3",
                            ),
                        ),
                        width="100%",
                    ),
                    # --- 댓글 섹션 추가 ---
                    comments_section(),
                    # --------------------
                    spacing="5",
                    padding_y="2em",
                ),
            ),
            max_width="960px",
        ),
    )
