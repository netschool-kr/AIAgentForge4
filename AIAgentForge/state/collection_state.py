# AIAgentForge/state/collection_state.py
import reflex as rx
from .base import BaseState
from .auth_state import AuthState
from .language_state import LanguageState
import os
from dotenv import load_dotenv
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

class CollectionState(BaseState):
    """컬렉션 관리와 관련된 모든 상태와 로직을 중앙에서 관리합니다."""

    collections: list[dict] = []
    is_loading: bool = False

    show_alert: bool = False
    alert_message: str = ""
    alert_message_key: str = ""  # UI에서 lang.t[...]로 해석할 수 있도록 키도 유지

    show_confirm_modal: bool = False
    collection_id_to_delete: Optional[str] = None
    new_collection_name: str = ""

    def set_new_collection_name(self, value: str):
        """새 컬렉션 이름 입력 필드의 값을 설정합니다."""
        self.new_collection_name = value

    @rx.event
    def set_show_confirm_modal(self, open: bool):
        """확인 모달 표시 여부 설정."""
        self.show_confirm_modal = open
        if not open:
            self.collection_id_to_delete = None

    @rx.event
    def show_confirm(self, collection_id: str):
        """삭제 확인 모달 표시."""
        self.collection_id_to_delete = collection_id
        self.set_show_confirm_modal(True)

    @rx.event
    def cancel_delete(self):
        """삭제 취소."""
        self.set_show_confirm_modal(False)

    # ID를 먼저 지역 변수에 저장한 후 삭제 작업을 수행.
    @rx.event
    async def confirm_delete(self):
        """모달에서 확인 시 실제 삭제."""
        collection_id = self.collection_id_to_delete
        self.set_show_confirm_modal(False)
        if collection_id is None:
            return

        lang = await self.get_state(LanguageState)
        try:
            client = await self._get_authenticated_client()
            client.from_("collections").delete().eq("id", collection_id).execute()
            # 목록 새로고침
            yield CollectionState.load_collections
        except Exception as e:
            self.alert_message = f"{lang.tr_str('collection_delete_fail')}: {e}"
            self.show_alert = True
            yield

    async def delete_collection(self, collection_id: str):
        """지정된 ID의 컬렉션을 삭제합니다."""
        self.is_loading = True
        yield
        lang = await self.get_state(LanguageState)

        try:
            client = await self._get_authenticated_client()
            client.from_("collections").delete().eq("id", collection_id).execute()
            self.alert_message = lang.tr_str("collection_delete_success")
            self.show_alert = True
            yield CollectionState.load_collections
        except Exception as e:
            self.alert_message = f"{lang.tr_str('collection_delete_fail')}: {e}"
            self.show_alert = True
        finally:
            self.is_loading = False
            yield

    async def load_collections(self):
        """사용자 소유의 모든 컬렉션을 데이터베이스에서 불러옵니다."""
        self.is_loading = True
        yield
        lang = await self.get_state(LanguageState)
        try:
            auth_state = await self.get_state(AuthState)
            if not auth_state.user:
                # 비로그인 상태라면 조용히 종료
                self.is_loading = False
                return

            client = await self._get_authenticated_client()
            response = client.from_("collections") \
                .select("*") \
                .eq("owner_id", auth_state.user.id) \
                .order("created_at", desc=True) \
                .execute()
            self.collections = response.data
        except Exception as e:
            self.alert_message = f"{lang.tr_str('doc_loading_failed', error='collections')}: {e}"
            self.show_alert = True
        finally:
            self.is_loading = False
            yield

    async def create_collection(self, form_data: dict):
        """새로운 컬렉션을 생성합니다."""
        lang = await self.get_state(LanguageState)

        if not self.new_collection_name.strip():
            # i18n 키를 UI에서 해석할 수 있게 유지
            self.alert_message_key = "collection_name_empty_error"
            self.alert_message = ""
            self.show_alert = True
            return

        self.is_loading = True
        yield

        try:
            auth_state = await self.get_state(AuthState)
            if not auth_state.user:
                raise Exception(lang.tr_str("user_not_found"))

            client = await self._get_authenticated_client()
            client.from_("collections").insert({
                "name": self.new_collection_name,
                "owner_id": auth_state.user.id
            }).execute()

            # 입력 필드 초기화 및 성공 알림
            self.new_collection_name = ""
            self.alert_message_key = "collection_create_success"
            self.alert_message = ""
            self.show_alert = True

            yield CollectionState.load_collections
        except Exception as e:
            self.alert_message_key = ""
            self.alert_message = f"{lang.tr_str('collection_create_fail')} {e}"
            self.show_alert = True
        finally:
            self.is_loading = False
            yield
