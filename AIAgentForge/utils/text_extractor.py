# langconnect_fullstack/utils/text_extractor.py
import io
from docx import Document
from PyPDF2 import PdfReader

def extract_text_from_pdf(file_content: bytes) -> str:
    """PDF 파일 내용(bytes)에서 텍스트를 추출합니다."""
    text = ""
    with io.BytesIO(file_content) as pdf_file:
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(file_content: bytes) -> str:
    """DOCX 파일 내용(bytes)에서 텍스트를 추출합니다."""
    text = ""
    with io.BytesIO(file_content) as docx_file:
        doc = Document(docx_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

def extract_text_from_file(file_content: bytes, mime_type: str) -> str:
    """MIME 타입에 따라 적절한 텍스트 추출 함수를 호출합니다."""
    if mime_type == "application/pdf":
        return extract_text_from_pdf(file_content)
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file_content)
    # TODO: 다른 파일 형식(예:.txt,.md)에 대한 처리 추가
    else:
        # 지원하지 않는 형식의 경우, 텍스트로 디코딩 시도
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            return "지원하지 않는 파일 형식이거나 텍스트를 추출할 수 없습니다."
