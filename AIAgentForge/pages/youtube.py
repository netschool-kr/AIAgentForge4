# AIAgentForge/pages/youtube.py
import reflex as rx
from AIAgentForge.components.navbar import navbar
from AIAgentForge.state.language_state import LanguageState  # i18n
from AIAgentForge.state.youtube_state import YoutubeState    # 클래스명이 YouTubeState라면 임포트만 맞게 바꾸세요.

@rx.page(route="/youtube", title="YouTube")
def youtube_page() -> rx.Component:
    return rx.container(
        rx.vstack(
            navbar(),

            # 페이지 타이틀
            rx.heading(LanguageState.t["yt_page_title"], size="8", text_align="center"),
            rx.divider(margin_y="6"),

            # URL 입력 + 실행 버튼
            rx.hstack(
                rx.input(
                    value=YoutubeState.video_url,
                    on_change=YoutubeState.set_video_url,
                    placeholder=LanguageState.t["yt_input_placeholder"],
                    size="3",
                    flex_grow=1,
                ),
                rx.button(
                    LanguageState.t["yt_btn_run"],
                    on_click=YoutubeState.run,                 # 기존 실행 이벤트명에 맞춰 조정
                    is_loading=YoutubeState.is_processing,     # 기존 로딩 플래그명에 맞춰 조정
                    size="3",
                ),
                spacing="3",
                width="100%",
            ),

            rx.cond(
                YoutubeState.status_text != "",
                rx.text(YoutubeState.status_text, color_scheme="gray"),
            ),

            rx.divider(margin_y="4"),

            # 원문 스크립트
            rx.cond(
                YoutubeState.original_transcript != "",
                rx.vstack(
                    rx.heading(LanguageState.t["yt_result_original"], size="5"),
                    rx.box(
                        rx.text(YoutubeState.original_transcript, white_space="pre_wrap"),
                        background_color=rx.color("gray", 3),
                        padding="4",
                        border_radius="var(--radius-3)",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
            ),

            # 번역 결과
            rx.cond(
                YoutubeState.translated_text != "",
                rx.vstack(
                    rx.heading(LanguageState.t["yt_result_translated"], size="5"),
                    rx.box(
                        rx.text(YoutubeState.translated_text, white_space="pre_wrap"),
                        background_color=rx.color("gray", 3),
                        padding="4",
                        border_radius="var(--radius-3)",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
            ),

            # 요약 결과
            rx.cond(
                YoutubeState.summary_text != "",
                rx.vstack(
                    rx.heading(LanguageState.t["yt_result_summary"], size="5"),
                    rx.card(
                        rx.markdown(YoutubeState.summary_text),
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
            ),

            spacing="6",
            width="100%",
            max_width="960px",
        ),
        padding_x="1em",
        padding_y="2em",
    )
