# AIAgentForge/state/search_state.py
import os
import reflex as rx
from .base import BaseState
from .document_state import DocumentState
from .auth_state import AuthState
from openai import AsyncOpenAI
from ..utils.embedder import generate_embeddings

# 환경 변수에서 OpenAI API 키를 가져와 클라이언트를 초기화합니다.
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class SearchState(BaseState):
    search_query: str = ""
    is_loading: bool = False
    search_results: list[dict] = []
    # LLM의 최종 답변을 저장할 상태 변수 추가
    llm_answer: str = ""
    
    def set_search_query(self, value: str):
        self.search_query = value
        
    async def handle_search(self):
        if not self.search_query.strip():
            return
        
        print("handle_search: ", self.search_query)

        self.is_loading = True
        # 이전 검색 결과와 답변을 초기화합니다.
        self.search_results = []
        self.llm_answer = ""
        yield

        try:
            # Step 1: 쿼리 임베딩 생성
            embeddings_list = await generate_embeddings([self.search_query])
            if not embeddings_list:
                raise ValueError("임베딩 생성에 실패했습니다.")
            query_embedding = embeddings_list[0]

            auth_state = await self.get_state(AuthState)
            if not auth_state.user:
                print("사용자를 찾을 수 없습니다.")
                self.alert_message = "사용자를 찾을 수 없습니다."
                self.show_alert = True
                self.is_loading = False
                yield
                return
            user_id = auth_state.user.id

            doc_state = await self.get_state(DocumentState)

            # Step 2: 데이터베이스에서 관련 문서 검색
            response = self.supabase_client.rpc(
                "hybrid_search_multilingual",
                params={
                    "query_text": self.search_query,
                    "query_embedding": query_embedding,
                    "p_collection_id": doc_state.collection_id,
                    "p_owner_id": user_id,
                    "match_count": 5,  # 컨텍스트 길이를 고려하여 5개로 조정
                }
            ).execute()
            
            self.search_results = response.data

            # Step 3: 검색된 문서를 기반으로 LLM에 질문
            if self.search_results:
                # 검색된 문서의 내용을 컨텍스트로 조합
                context = "\n\n---\n\n".join([item['content'] for item in self.search_results])
                
                # LLM에 전달할 프롬프트 구성
                prompt_message = f"""
                당신은 주어진 컨텍스트를 기반으로 사용자의 질문에 답변하는 AI 어시스턴트입니다.
                오직 제공된 컨텍스트만을 사용하여 답변을 생성해야 합니다.
                만약 컨텍스트에 답변에 대한 정보가 없다면, "제공된 문서에서 답변을 찾을 수 없습니다."라고 답변하세요.
                
                컨텍스트:
                {context}
                
                질문:
                {self.search_query}
                
                답변:
                """

                # OpenAI API 호출
                chat_completion = await client.chat.completions.create(
                    model="gpt-4o",  # 원하는 모델로 변경 가능
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant that answers questions based on the provided context in Korean."},
                        {"role": "user", "content": prompt_message},
                    ],
                    temperature=0.5,
                )
                
                if chat_completion.choices:
                    self.llm_answer = chat_completion.choices[0].message.content
                else:
                    self.llm_answer = "답변을 생성하지 못했습니다."
            else:
                self.llm_answer = "관련 문서를 찾지 못해 답변을 생성할 수 없습니다."

        except Exception as e:
            print(f"Search and answer generation failed: {e}")
            self.llm_answer = f"오류가 발생했습니다: {e}"
            self.search_results = []
        finally:
            self.is_loading = False
            yield