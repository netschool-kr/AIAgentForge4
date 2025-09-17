# langconnect_fullstack/utils/embedder.py
import os
from openai import AsyncOpenAI

# 환경 변수에서 OpenAI API 키를 가져와 클라이언트를 초기화합니다.
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

async def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """OpenAI API를 사용하여 텍스트 목록에 대한 임베딩을 비동기적으로 생성합니다."""
    if not texts:
        # texts가 비어있을 경우 None 대신 빈 리스트를 반환하는 것이 더 일관성 있습니다.
        return []

    try:
        # 임베딩 API를 비동기적으로 호출합니다.
        res = await client.embeddings.create(
            input=texts,
            model="text-embedding-3-small"
        )
        # 응답에서 임베딩 데이터만 추출하여 반환합니다.
        embeddings = [record.embedding for record in res.data]
        return embeddings
    except Exception as e:
        print(f"임베딩 생성 중 오류 발생: {e}")
        # 실제 애플리케이션에서는 더 정교한 오류 처리가 필요합니다.
        # 오류 발생 시, 입력된 텍스트 수만큼 빈 리스트를 반환합니다.
        return [[] for _ in texts]