#AIAgentForge/state/chat_state.py

import reflex as rx
from AIAgentForge.state.base import BaseState
import os
import openai
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv() #.env 파일에서 환경 변수를 로드합니다.

# Message 모델 정의: 채팅 메시지의 구조를 명확히 하기 위해 Pydantic 모델을 사용합니다.
class Message(rx.Base):
    role: str  # "user" 또는 "assistant"
    content: str

class ChatState(BaseState):
    """
    채팅 페이지의 상태를 관리하는 클래스입니다.
    채팅과 관련된 모든 변수(vars)와 이벤트 핸들러(event handlers)를 포함합니다.
    """

    # 사용자의 현재 입력을 저장하는 기본 변수(Base Var)
    question: str = ""

    # 채팅 기록을 저장하는 기본 변수. Message 모델의 리스트로 타입을 명시합니다.
    chat_history: list[Message] = []
    #chat_history: list[tuple[str, str]] = []   
    def set_question(self, question: str):
            """question 변수를 설정하는 메서드입니다."""
            self.question = question

    # AI가 응답을 처리 중인지 나타내는 상태 변수 추가
    processing: bool = False

    @rx.event
    async def answer(self):
        if not self.question.strip():
            return
        # 사용자의 질문을 채팅 기록에 추가합니다.
        text = self.question
        self.chat_history.insert(0, Message(role="user", content=text))        
        yield
        
        # Our chatbot has some brains now!
        client = AsyncOpenAI(
            api_key=os.environ["OPENAI_API_KEY"]
        )

        session = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": self.question}
            ],
            stop=None,
            temperature=0.7,
            stream=True,
        )
        self.question = ""

        # Add to the answer as the chatbot responds.
        answer = ""
        self.chat_history.insert(0, Message(role="assistant", content=answer))        
        # self.chat_history.append(Message(role="assistant", content=answer))

        # Yield here to clear the frontend input before continuing.
        yield

        async for item in session:
            if hasattr(item.choices[0].delta, "content"):
                if item.choices[0].delta.content is None:
                    # presence of 'None' indicates the end of the response
                    break
                answer += item.choices[0].delta.content
                self.chat_history[0] = (
                   Message(role="assistant", content=answer)
                )
                yield
        
    