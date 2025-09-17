# AIAgentForge/pages/blog.py
import reflex as rx
from ..state.blog_state import BlogState
from AIAgentForge.components.navbar import navbar
from AIAgentForge.state.language_state import LanguageState  # i18n

def step_card(*children, **props):
    """단계별 UI를 감싸는 카드 컴포넌트입니다."""
    return rx.card(
        rx.vstack(
            *children,
            spacing="4",
            align="stretch",
        ),
        width="100%",
        **props
    )

def blog_page() -> rx.Component:
    """블로그 포스팅 생성기 메인 페이지 UI입니다."""
    return rx.container(
        rx.vstack(
            navbar(),

            # 타이틀, 서브타이틀
            rx.heading(LanguageState.t["blog_generator_title"], size="8", text_align="center"),
            rx.text(LanguageState.t["blog_generator_subtitle"], text_align="center"),

            rx.divider(margin_y="6"),

            # --- 1단계: 키워드 입력 ---
            step_card(
                rx.heading(LanguageState.t["step1_heading"], size="5"),
                rx.hstack(
                    rx.input(
                        placeholder=LanguageState.t["step1_input_placeholder"],
                        value=BlogState.product_keyword,
                        on_change=BlogState.set_product_keyword,
                        on_blur=BlogState.generate_titles,
                        on_key_down=BlogState.handle_key_down,
                        size="3",
                        flex_grow=1,
                    ),
                    rx.button(
                        LanguageState.t["btn_generate_titles"],
                        on_click=BlogState.generate_titles,
                        is_loading=BlogState.is_generating_titles,
                        size="3",
                    ),
                    width="100%",
                ),
            ),

            # --- 2단계: 제목 선택 ---
            rx.cond(
                BlogState.is_generating_titles | (BlogState.title_candidates.length() > 0),
                step_card(
                    rx.heading(LanguageState.t["step2_heading"], size="5"),
                    rx.cond(
                        BlogState.is_generating_titles,
                        rx.center(rx.spinner()),
                        rx.vstack(
                            rx.foreach(
                                BlogState.title_candidates,
                                lambda title: rx.button(
                                    title,
                                    on_click=lambda: BlogState.select_title_and_generate_outline(title),
                                    width="100%",
                                    variant="outline",
                                    is_disabled=BlogState.is_generating_outline,
                                )
                            ),
                            spacing="3",
                            width="100%",
                        ),
                    ),
                ),
            ),

            # --- 3단계: 목차 확인 및 본문 생성 ---
            rx.cond(
                BlogState.is_generating_outline | (BlogState.generated_outline != ""),
                step_card(
                    rx.heading(LanguageState.t["step3_heading"], size="5"),
                    rx.cond(
                        BlogState.is_generating_outline,
                        rx.center(rx.spinner()),
                        rx.box(
                            rx.text(BlogState.generated_outline, white_space="pre_wrap"),
                            background_color=rx.color("gray", 3),
                            padding="4",
                            border_radius="var(--radius-3)",
                            width="100%",
                        ),
                    ),
                    rx.button(
                        LanguageState.t["btn_generate_final_posting"],
                        on_click=BlogState.generate_final_posting,
                        is_loading=BlogState.is_generating_posting,
                        size="3",
                        width="100%",
                        disabled=BlogState.generated_outline == "",
                    ),
                ),
            ),

            # --- 4단계: 최종 결과물 ---
            rx.cond(
                BlogState.is_generating_posting | BlogState.is_finished,
                step_card(
                    rx.heading(LanguageState.t["step4_heading"], size="5"),
                    rx.cond(
                        BlogState.is_generating_posting,
                        rx.center(rx.spinner()),
                        rx.box(
                            rx.markdown(BlogState.final_posting),
                            border="1px solid",
                            border_color=rx.color("gray", 6),
                            padding="6",
                            border_radius="var(--radius-3)",
                            width="100%",
                        ),
                    ),
                ),
            ),

            # --- 새로 시작하기 버튼 ---
            rx.cond(
                BlogState.is_finished,
                rx.center(
                    rx.button(
                        LanguageState.t["btn_restart"],
                        on_click=BlogState.reset_all,
                        size="3",
                        margin_top="6",
                    ),
                    width="100%",
                )
            ),

            spacing="6",
            width="100%",
            margin_x="auto",
            padding_y="8",
        ),
        size="4",
        on_mount=BlogState.init_state,
    )
