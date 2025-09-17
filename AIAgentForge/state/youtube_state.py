# AIAgentForge/state/youtube_state.py
# -*- coding: utf-8 -*-
import re
import reflex as rx
from typing import Tuple

# LangChain
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

# YouTube transcripts
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

from AIAgentForge.state.language_state import LanguageState  # i18n

# ----- LLM chains -----
llm = ChatOpenAI(model="gpt-4o", temperature=0, streaming=True)

translation_prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 한국어로 번역하는 번역 전문가야. 다음 내용을 한국어로 번역해줘."),
    MessagesPlaceholder(variable_name="messages"),
])

summary_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 전문 요약가입니다. 사용자가 제공하는 전체 텍스트를 간결하고 구조적으로 요약하세요."),
    MessagesPlaceholder(variable_name="messages"),
])

translation_chain = translation_prompt | llm
summary_chain = summary_prompt | llm


# ----- Helpers -----
def extract_video_id(url: str) -> str:
    m = re.search(r"(?:v=|/)([0-9A-Za-z_-]{11})", url)
    if not m:
        # 검증은 상태에서 메시지로 처리. 여기서는 ValueError만 던짐.
        raise ValueError("INVALID_YOUTUBE_URL")
    return m.group(1)


def get_script_from_youtube(url: str) -> Tuple[str, str]:
    """자막 텍스트와 언어코드 반환."""
    video_id = extract_video_id(url)
    api = YouTubeTranscriptApi()
    transcript_list = api.list(video_id)

    language_codes = [t.language_code for t in transcript_list]
    found = None
    try:
        found = transcript_list.find_manually_created_transcript(language_codes)
    except NoTranscriptFound:
        try:
            found = transcript_list.find_generated_transcript(language_codes)
        except NoTranscriptFound:
            raise TranscriptsDisabled(video_id)

    if not found:
        raise TranscriptsDisabled(video_id)

    data = found.fetch()
    # 원본 코드의 오타(entry.terx) 의심. 일반적으로 'text' 필드.
    full = " ".join(getattr(entry, "text", getattr(entry, "terx", "")) for entry in data).strip()
    return full, found.language_code


# ----- State -----
class YoutubeState(rx.State):
    """YouTube 요약·번역 워크플로우 상태."""
    # youtube.py와 이름 일치
    video_url: str = ""
    original_transcript: str = ""
    translated_text: str = ""
    summary_text: str = ""
    source_language: str = ""

    is_processing: bool = False
    status_text: str = ""
    error_text: str = ""   # 내부 오류 저장. UI에서는 status_text 또는 별도 알림에 바인딩 가능.

    # --------------- setters ---------------
    def set_video_url(self, value: str):
        self.video_url = value

    # --------------- main flow ---------------
    async def run(self):
        """[추출 → 번역 → 요약]"""
        lang = await self.get_state(LanguageState)

        if not self.video_url.strip():
            self.status_text = lang.tr_str("yt_err_enter_url")
            return

        # 초기화
        self.is_processing = True
        self.status_text = ""
        self.error_text = ""
        self.original_transcript = ""
        self.translated_text = ""
        self.summary_text = ""
        self.source_language = ""
        yield

        try:
            # 1) 자막 추출
            self.status_text = lang.tr_str("yt_status_extracting")
            yield
            script, lang_code = get_script_from_youtube(self.video_url)
            self.original_transcript = script

            # 간단한 언어 표시
            language_map = {"en": "English", "ja": "Japanese", "es": "Spanish", "fr": "French", "ko": "Korean"}
            self.source_language = language_map.get(lang_code, lang_code)

            # 2) 번역 또는 스킵
            if lang_code == "ko":
                self.translated_text = lang.tr_str("yt_skip_translation")
                script_to_summarize = self.original_transcript
                yield
            else:
                self.status_text = lang.tr_str("yt_status_translating")
                yield
                req = HumanMessage(content=self.original_transcript)
                script_to_summarize = ""
                async for chunk in translation_chain.astream({"messages": [req]}):
                    self.translated_text += chunk.content
                    script_to_summarize += chunk.content
                    yield

            # 3) 요약
            self.status_text = lang.tr_str("yt_status_summarizing")
            yield
            req = HumanMessage(content=script_to_summarize)
            async for chunk in summary_chain.astream({"messages": [req]}):
                self.summary_text += chunk.content
                yield

            # 완료
            self.status_text = ""

        except ValueError as ve:
            # URL 형식 오류
            if str(ve) == "INVALID_YOUTUBE_URL":
                self.status_text = lang.tr_str("yt_err_invalid_url")
            else:
                self.status_text = lang.tr_str("yt_err_prefix", error=str(ve))
        except Exception as e:
            # 기타 오류
            self.status_text = lang.tr_str("yt_err_prefix", error=str(e))
            self.error_text = str(e)
        finally:
            self.is_processing = False
            yield
