#AIAgentForge/components/chat_bubble.py


import reflex as rx
from AIAgentForge.state.chat_state import Message

# 채팅 말풍선의 스타일을 정의합니다. 튜토리얼의 스타일을 참조하여 재구성합니다. [2]
message_style = dict(
    padding="1em",
    border_radius="5px",
    margin_y="0.5em",
    box_shadow="rgba(0, 0, 0, 0.15) 0px 2px 8px",
    max_width="60%",
    display="inline-block",
)

# 질문(사용자) 말풍선 스타일
question_style = message_style | dict(
    background_color=rx.color("gray", 4),
    margin_left="20%",
)

# 답변(어시스턴트) 말풍선 스타일
answer_style = message_style | dict(
    background_color=rx.color("accent", 8),
    margin_right="20%",
)

def chat_bubble(message: Message) -> rx.Component:
    """
    하나의 채팅 메시지를 표시하는 재사용 가능한 컴포넌트입니다.
    메시지의 'role'에 따라 다른 스타일과 정렬을 적용합니다.
    """
    is_user = message.role == "user"
    
    return rx.box(
        rx.box(
            rx.markdown(
                message.content,
                background="transparent",
                color= rx.cond(is_user, rx.color("gray", 12), "white"),
            ),
            # role에 따라 다른 스타일을 적용합니다.
            style=rx.cond(is_user, question_style, answer_style),
        ),
        # role에 따라 전체 박스의 정렬을 변경합니다.
        text_align=rx.cond(is_user, "right", "left"),
        width="100%",
    )