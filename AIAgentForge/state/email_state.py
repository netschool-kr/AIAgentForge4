# AIAgentForge/state/email_state.py
import reflex as rx
import os
import httpx
from supabase import create_client, Client

# Supabase 클라이언트 설정
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_ANON_KEY")
# 직접적인 DB 접근 대신 함수 호출에만 사용됩니다.
supabase: Client = create_client(url, key)

class EmailState(rx.State):
    emails: list[str] = []
    is_loading: bool = False
    message: str = ""

    # 1. Supabase Edge Function을 호출하여 모든 사용자 이메일 가져오기
    async def fetch_emails(self):
        self.is_loading = True
        self.message = "이메일 목록을 불러오는 중입니다..."
        yield

        try:
            function_url = f"{url}/functions/v1/get-all-users"
            headers = {"Authorization": f"Bearer {key}"}

            async with httpx.AsyncClient() as client:
                response = await client.post(function_url, headers=headers, timeout=30)
                response.raise_for_status() # 오류가 있으면 예외 발생
                
                result = response.json()
                self.emails = result.get("emails", [])
                self.message = f"총 {len(self.emails)}명의 이메일을 불러왔습니다."

        except Exception as e:
            self.message = f"이메일 로딩 실패: {e}"
        
        self.is_loading = False
        yield

    # 2. Supabase Edge Function을 호출하여 이메일 전송 요청 (기존과 동일)
    async def send_emails(self, form_data: dict):
        self.is_loading = True
        self.message = "이메일 전송을 시작합니다..."
        yield

        subject = form_data.get("subject")
        html = form_data.get("html_content")

        if not all([subject, html, self.emails]):
            self.message = "제목, 내용, 이메일 목록이 모두 필요합니다."
            self.is_loading = False
            return

        try:
            #function_url = f"{url}/functions/v1/send-emails"
            function_url = f"{url}/functions/v1/send-supabase-invites"
            headers = {"Authorization": f"Bearer {key}"}
            payload = {"emails": self.emails, "subject": subject, "html": html}

            async with httpx.AsyncClient() as client:
                response = await client.post(function_url, json=payload, headers=headers, timeout=180)
                response.raise_for_status()
                self.message = "이메일 전송 요청이 성공적으로 완료되었습니다!"

        except Exception as e:
            self.message = f"이메일 전송 실패: {e}"
        self.is_loading = False
