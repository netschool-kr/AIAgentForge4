# langconnect_fullstack/utils/chunker.py
from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_text(text: str) -> list[dict]:
    """LangChain을 사용하여 텍스트를 의미 있는 청크로 분할합니다."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # 각 청크의 최대 크기
        chunk_overlap=200,  # 청크 간의 중복되는 문자 수
        length_function=len,
        is_separator_regex=False,
    )
    # split_text는 문자열 리스트를 반환합니다.
    chunks_text = text_splitter.split_text(text)
    # 파이프라인의 다른 부분에서 사용하기 쉽도록 딕셔너리 리스트로 변환합니다.
    chunks = [{"text": chunk} for chunk in chunks_text]
    return chunks
