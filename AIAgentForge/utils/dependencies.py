# AIAgentForge/utils/dependencies.py

import os
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from supabase import create_client, Client
from gotrue.types import User

#.env 파일에서 Supabase 설정 로드
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# Supabase 클라이언트 생성
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# OAuth2 스키마 정의. tokenUrl은 실제 토큰 발급 엔드포인트를 가리키지만,
# 여기서는 주로 OpenAPI 문서 생성을 위해 사용됩니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Authorization 헤더의 Bearer 토큰을 검증하고,
    유효한 경우 Supabase 사용자 객체를 반환하는 의존성 함수입니다.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Supabase 클라이언트를 사용하여 토큰의 유효성을 서버 측에서 확인합니다.
        response = supabase_client.auth.get_user(token)
        user = response.user
        if not user:
            raise credentials_exception
        return user
    except Exception:
        # 토큰이 만료되었거나 유효하지 않은 경우 예외가 발생합니다.
        raise credentials_exception

