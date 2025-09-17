# AIAgentForge/utils/v1_router.py

import json
from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from gotrue.types import User

from AIAgentForge.state.base import BaseState # Supabase 클라이언트 접근
from AIAgentForge.utils.dependencies import get_current_user
from AIAgentForge.utils.embedder import generate_embeddings

# API 버전 1을 위한 라우터를 생성합니다.
api_v1_router = APIRouter(prefix="/api/v1")

@api_v1_router.get("/health")
async def health_check():
    """API 서버의 상태를 확인하는 간단한 엔드포인트입니다."""
    return {"status": "ok"}

class McpRequest(BaseModel):
    query: str
    collection_id: str
    match_count: int = 10

@api_v1_router.post("/mcp/stream")
async def mcp_stream_endpoint(
    request_data: McpRequest,
    current_user: User = Depends(get_current_user)
):
    """
    AI 어시스턴트를 위한 MCP 스트리밍 엔드포인트입니다.
    하이브리드 검색을 수행하고 그 과정을 SSE로 스트리밍합니다.
    """
    async def event_stream_generator():
        try:
            # 1. 작업 시작 알림
            yield {
                "event": "search_started",
                "data": json.dumps({"query": request_data.query})
            }

            # 2. 쿼리 임베딩 생성
            # generate_embeddings는 임베딩 목록을 반환하므로 첫 번째 항목을 가져옵니다.
            embeddings_list = await generate_embeddings([request_data.query])
            if not embeddings_list:
                raise ValueError("임베딩 생성에 실패했습니다.")
            query_embedding = embeddings_list[0]
            
            # 3. RPC 파라미터 준비
            rpc_params = {
                "query_text": request_data.query,
                "query_embedding": query_embedding, # 수정: 1차원 배열로 전달
                "p_collection_id": request_data.collection_id,
                "match_count": request_data.match_count,
                "p_owner_id": str(current_user.id)
            }

            # 4. hybrid_search_multilingual RPC 실행
            response =  BaseState.supabase_client.rpc(
                "hybrid_search_multilingual",
                params=rpc_params
            ).execute()

            # 5. 검색 결과 스트리밍
            yield {
                "event": "chunks_found",
                "data": json.dumps(response.data)
            }

        except Exception as e:
            # 오류 발생 시 에러 이벤트 전송
            yield {
                "event": "error",
                "data": json.dumps({"detail": str(e)})
            }
        finally:
            # 6. 스트림 종료 알림
            yield {
                "event": "stream_end",
                "data": json.dumps({"message": "Stream completed."})
            }

    return EventSourceResponse(event_stream_generator())
