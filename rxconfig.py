import reflex as rx
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# 환경 변수가 없을 경우를 대비해 기본값으로 None을 설정합니다.
REFLEX_DB_URL = os.environ["REFLEX_DB_URL"]
print(f"REFLEX_DB_URL={REFLEX_DB_URL}")
# 배포 환경을 확인하고 api_url을 설정합니다.
# Fly.io에 배포될 경우 FLY_APP_NAME 환경 변수가 자동으로 설정됩니다.
fly_app_name = os.environ.get("FLY_APP_NAME")
if fly_app_name:
    # Fly.io에 배포될 경우, 앱 이름과 fly.dev 주소를 사용합니다.
    # Fly.io의 환경 변수 FLY_APP_NAME을 활용하여 URL을 구성합니다.
    # 웹소켓 연결을 위해 wss 프로토콜을 사용합니다.
    api_url = f"wss://{fly_app_name}.fly.dev/_event"
else:
    # 로컬 개발 환경일 경우 localhost를 사용합니다.
    api_url = "http://localhost:8000"

# 애플리케이션 이름과 다른 설정을 포함하는 Config 객체를 생성합니다.
config = rx.Config(
    app_name="AIAgentForge",
    api_url=api_url,
    db_url=REFLEX_DB_URL,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
)
