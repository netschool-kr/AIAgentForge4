# Python 3.11 정식 버전을 기반으로 이미지를 만듭니다.
# 'slim' 버전과 달리, 필요한 시스템 라이브러리가 포함되어 있어 호환성 문제가 적습니다.
FROM python:3.11

# 컨테이너 내 작업 디렉터리를 설정합니다.
WORKDIR /app

# 시스템에 필요한 패키지들을 설치합니다.
# git과 build-essential은 파이썬 라이브러리 설치 시 필요할 수 있습니다.
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
 && rm -rf /var/lib/apt/lists/* \
 && curl -fsSL https://bun.sh/install | bash \
 && mv /root/.bun/bin/bun /usr/local/bin/bun \
 && bun --version

# 파이썬 의존성 파일인 requirements.txt를 먼저 복사하여 캐싱을 활용합니다.
# 의존성 파일이 변경되지 않으면 이 단계는 재빌드되지 않아 효율적입니다.
COPY requirements.txt .

# 필요한 파이썬 라이브러리를 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# .dockerignore에 명시된 파일을 제외하고, 나머지 모든 프로젝트 파일들을 컨테이너로 복사합니다.
COPY . .

# Reflex 앱의 프론트엔드(3000)와 백엔드(8000) 포트를 외부에 노출합니다.
EXPOSE 3000
EXPOSE 8000

# 컨테이너가 시작될 때 실행될 명령어입니다.
# Reflex 앱을 프로덕션 모드로 실행하고, 컨테이너 외부에서 접근 가능하도록 --backend-host를 설정합니다.
CMD ["reflex", "run", "--env", "prod", "--backend-host", "0.0.0.0"]
