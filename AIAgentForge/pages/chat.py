#AIAgentForge/pages/chat.py

import reflex as rx
from AIAgentForge.state.chat_state import ChatState
from AIAgentForge.components.chat_bubble import chat_bubble
from AIAgentForge.components.navbar import navbar  # Navbar 임포트 추가
from AIAgentForge.state.language_state import LanguageState

def desktop_chat_view() -> rx.Component:
    """데스크톱용 채팅 UI 컴포넌트입니다."""
    return rx.box(
        # rx.foreach를 사용하여 chat_history 리스트를 순회하며
        # 각 메시지에 대해 chat_bubble 컴포넌트를 렌더링합니다.
        rx.foreach(ChatState.chat_history, chat_bubble),
        width="100%",
        padding_x="2em",
        padding_top="2em",
    )
    
def mobile_chat_view() -> rx.Component:
    """모바일용 채팅 UI 컴포넌트입니다."""
    return rx.box(
        rx.foreach(ChatState.chat_history, chat_bubble),
        width="100%",
        max_height="80vh",
        overflow_y="auto",
    )

# def action_bar() -> rx.Component:
#     return rx.center(
#         rx.vstack(
#             rx.box(
#                 rx.form(
#                     rx.hstack(
#                         rx.input(
#                             placeholder="질문을 입력하세요...",
#                             value=ChatState.question,
#                             on_change=ChatState.set_question,
#                             flex=1,          # 남는 공간 전부 차지
#                             min_width=0,     # flexbox에서 폭 축소/확장 허용
#                         ),
#                         rx.button("전송", type="submit", flex_shrink=0),
#                         width="100%",          # ⬅ 부모가 전체 폭
#                         align_items="stretch",
#                         gap="0.5rem",
#                     ),
#                     on_submit=ChatState.answer,
#                     reset_on_submit=True,
#                     width="100%",
#                 ),
#                 width="100%",
#             ),
#             padding_bottom="2em",
#             padding_top="1em",
#         ),
#         position="sticky",
#         bottom="0",
#         background_color=rx.color("gray", 2),
#         width="100%",
#     )

def action_bar() -> rx.Component:
    """사용자 입력을 받는 하단의 액션 바 컴포넌트입니다."""
    return rx.center(
        rx.vstack(
            rx.form(
                rx.hstack(
                    rx.input(
                        placeholder=LanguageState.t["input_placeholder"],
                        value=ChatState.question,
                        on_change=ChatState.set_question,
                        flex_grow=1,
                    ),
                    rx.button(LanguageState.t["send_button"], type="submit"),
                ),
                on_submit=ChatState.answer,
                reset_on_submit=True,
                width="100%",
            ),
            width="60%",
            padding_bottom="2em",
            padding_top="1em"
        ),
        position="sticky",
        bottom="0",
        background_color=rx.color("gray", 2),
        width="100%",
    )


def chat_page() -> rx.Component:
    """
    채팅 페이지의 메인 UI를 정의하는 컴포넌트 함수입니다.
    """
    return rx.vstack(
        navbar(),
        rx.mobile_only(mobile_chat_view()),
        rx.desktop_only(desktop_chat_view()),
        rx.spacer(),
        action_bar(),
        rx.hstack(
            rx.button("한국어", on_click=LanguageState.set_locale("ko")),
            rx.button("English", on_click=LanguageState.set_locale("en")),
            rx.button("日本語", on_click=LanguageState.set_locale("ja")),
            spacing="4",
        ),
        align="center",
        width="100%",
        height="100vh",
    )

# def chat_page() -> rx.Component:
#     """
#     채팅 페이지의 메인 UI를 정의하는 컴포넌트 함수입니다.
#     """
#     return rx.vstack(
#         rx.box(
#             # rx.foreach를 사용하여 chat_history 리스트를 순회하며
#             # 각 메시지에 대해 chat_bubble 컴포넌트를 렌더링합니다.
#             rx.foreach(ChatState.chat_history, chat_bubble),
#             width="100%",
#             padding_x="2em",
#             padding_top="2em"
#         ),
#         rx.spacer(), # 채팅 내용과 액션 바 사이의 공간을 채웁니다.
#         action_bar(),
#         align="center",
#         width="100%",
#         height="100vh", # 전체 화면 높이를 차지하도록 설정
#     )
