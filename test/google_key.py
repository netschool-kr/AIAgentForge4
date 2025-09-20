# Google Generative AI 라이브러리 설치 필요: pip install -q google-generativeai

import google.generativeai as genai
import os
import sys
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()
# cSpell 경고: 'generativeai' 단어는 코드 편집기의 철자 검사기가 인식하지 못하는 단어입니다.
# 이는 코드 실행에 영향을 주지 않으므로 무시해도 됩니다.
# API 키는 보안을 위해 환경 변수에 설정하는 것을 권장합니다.
# export GOOGLE_API_KEY="YOUR_API_KEY" (Linux/macOS)
# set GOOGLE_API_KEY="YOUR_API_KEY" (Windows)

try:
    api_key_env = os.getenv('GOOGLE_API_KEY')
    if not api_key_env:
        print("오류: GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다.")
        sys.exit()

    genai.configure(api_key=api_key_env)
    print("환경 변수에서 API 키가 성공적으로 로드되었습니다.")
except Exception as e:
    print(f"API 키 구성 중 오류 발생: {e}")
    sys.exit()

def test_gemini_api():
    """
    Gemini API를 호출하여 모델의 응답을 테스트하는 함수
    """
    try:
        print("\n사용 가능한 모델을 나열합니다...")
        
        # 'generateContent' 메서드를 지원하는 사용 가능한 모든 모델을 필터링합니다.
        # 이 로직은 API 키에 맞는 올바른 모델을 찾는 데 도움이 됩니다.
        available_models = [
            m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods
        ]
        
        if not available_models:
            print("오류: 'generateContent'를 지원하는 모델을 찾을 수 없습니다. API 키나 권한을 확인하세요.")
            return

        # 사용 가능한 첫 번째 모델을 선택합니다.
        model_name = available_models[0].name
        print(f"사용 가능한 모델을 찾았습니다: {model_name}")

        model = genai.GenerativeModel(model_name)

        # 모델에 보낼 프롬프트(질문)입니다.
        prompt = "안녕, 제미니! 간단한 농담 하나 해줘."

        print(f"\n모델에게 요청 중... 프롬프트: '{prompt}'")
        
        # 모델에게 요청을 보냅니다.
        response = model.generate_content(prompt)

        # 응답을 출력합니다.
        print("\n모델의 응답:")
        print("--------------------")
        print(response.text)
        print("--------------------")

    except genai.types.BlockedPromptException as e:
        print(f"\n프롬프트가 거부되었습니다. 이유: {e.response.prompt_feedback}")
    except Exception as e:
        print(f"\nAPI 호출 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    # 스크립트가 직접 실행될 때 함수를 호출합니다.
    test_gemini_api()
