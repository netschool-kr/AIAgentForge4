# AIAgentForge/state/document_state.py
import reflex as rx
from .base import BaseState
from .auth_state import AuthState
from .language_state import LanguageState
import os
from dotenv import load_dotenv
from postgrest import SyncPostgrestClient
import asyncio
from supabase import create_client, Client
from reflex.vars import Var
from typing import List
from ..utils.text_extractor import extract_text_from_file
from ..utils.chunker import chunk_text
from ..utils.embedder import generate_embeddings
from urllib.parse import parse_qs, quote # quote import 추가
import uuid
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
BUCKET_NAME = "document-files"
DOCUMENT_TABLE = "documents"

class DocumentState(BaseState):
    """특정 컬렉션의 문서 관리와 관련된 상태 및 로직을 처리합니다."""
    
    documents: list[dict] = []
    collection_name: str = ""
    collect_id: str=""
    is_loading: bool = False
    is_uploading: bool = False
    upload_progress: dict[str, int] = {}
    upload_status: dict[str, str] = {}
    upload_errors: dict[str, str] = {}

    show_alert: bool = False
    alert_message: str = ""

    async def init_on_load(self):
        # 1) 인증 이벤트 실행
        yield AuthState.check_auth

        # 2) 인증 결과 확인
        auth = await self.get_state(AuthState)
        if not auth.user:
            lang = await self.get_state(LanguageState)
            self.alert_message = lang.tr_str("user_not_found")
            self.show_alert = True
            return

        # 3) 문서 로딩 이벤트 실행
        yield DocumentState.load_documents_on_page_load
    
    def toggle_upload_document(self):
        """upload_document 상태를 토글합니다. (True ↔ False)"""
        self.upload_document = not self.upload_document

    def toggle_process_document(self):
        """process_document 상태를 토글합니다. (True ↔ False)"""
        self.process_document = not self.process_document
        
    def set_process_document(self, value: bool):
        self.process_document = value

    async def load_documents_on_page_load(self):
        logging.info(f"load_documents_on_page_load:{self.router.url}")
        collection_id = self.router.url.split('/')[-1]
        lang = await self.get_state(LanguageState)
        
        if not collection_id:
            self.alert_message = lang.tr_str("doc_collection_id_missing")
            self.show_alert = True
            return

        self.is_loading = True
        self.collection_id = collection_id
        
        yield
        try:
            client = await self._get_authenticated_client()
            
            collection_response = client.from_("collections").select("name").eq("id", collection_id).single().execute()
            if collection_response.data:
                default_name = lang.tr_str("name_untitled")
                self.collection_name = collection_response.data.get("name") or default_name
            else:
                self.collection_name = lang.tr_str("unknown_collection")
                            
            response = client.from_("documents").select("*").eq("collection_id", collection_id).execute()
            self.documents = response.data
        except Exception as e:
            self.alert_message = lang.tr_str("doc_loading_failed", error=str(e))
            self.show_alert = True
        finally:
            self.is_loading = False
            yield
            
    # Supabase Bucket에 file을 upload
    async def handle_upload(self, files: list[rx.UploadFile]):
        collection_id = self.router.url.split('/')[-1]
        lang = await self.get_state(LanguageState)
        
        if not collection_id:
            print(lang.tr_str("doc_collection_id_missing"))
            self.alert_message = lang.tr_str("doc_collection_id_missing")
            self.show_alert = True
            return

        if not files:
            return
            
        supabase_client = await self._get_supabase_client()

        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            print(lang.tr_str("user_not_found"))
            self.alert_message = lang.tr_str("user_not_found")
            self.show_alert = True
            self.is_uploading = False
            return
        user_id = auth_state.user.id
        
        db_client = await self._get_authenticated_client()

        self.is_uploading = True
        
        for file in files:
            filename = file.name
            self.upload_status[filename] = lang.tr_str("upload_waiting")
            self.upload_progress[filename] = 0
            self.upload_errors.pop(filename, None)
        yield

        successful_uploads = 0
        for file in files:
            original_filename = file.name
            try:
                existing_doc_res = db_client.from_("documents").select("id").eq("name", original_filename).eq("collection_id", collection_id).maybe_single().execute()
                
                if existing_doc_res and existing_doc_res.data:
                    logger.warning(f"File '{original_filename}' already exists in this collection. Skipping.")
                    self.upload_status[original_filename] = lang.tr_str("status_failed")
                    self.upload_errors[original_filename] = lang.tr_str("doc_exists_same_name")
                    self.upload_progress[original_filename] = 100
                    yield
                    continue
                
                file_content = await file.read()
                content_type = file.content_type

                self.upload_status[original_filename] = lang.tr_str("upload_storage_uploading")
                self.upload_progress[original_filename] = 10
                yield

                file_extension = os.path.splitext(original_filename)[1]
                storage_filename = f"{uuid.uuid4()}{file_extension}"
                storage_path = f"{user_id}/{collection_id}/{storage_filename}"
                
                logger.info(f"Attempting to upload to storage path: {storage_path}")

                storage_response = supabase_client.storage.from_(BUCKET_NAME).upload(
                    storage_path,
                    file_content,
                    {'content-type': content_type or 'application/octet-stream'}
                )

                if not storage_response.full_path:
                    error_detail = storage_response.text
                    raise Exception(f"Storage upload failed: {error_detail}")

                response = db_client.from_("documents").insert({
                    "name": original_filename,
                    "collection_id": collection_id,
                    "owner_id": user_id,
                    "storage_path": storage_response.full_path
                }).execute()

                if response.data:
                    inserted_document = response.data[0]
                    document_id = inserted_document['id']
                    print(f"새로 생성된 문서 ID: {document_id}")
                    
                self.upload_progress[original_filename] = 20
                self.upload_status[original_filename] = lang.tr_str("upload_text_extracting")
                successful_uploads += 1
                yield
                    
                print(" Process Document")
                
                self.upload_progress[original_filename] = 30                
                self.upload_status[original_filename] = lang.tr_str("upload_text_extracting")
                yield
                
                text = extract_text_from_file(file_content, content_type)
                logger.info(f"Extracted text length for {original_filename}: {len(text)}")
                if not text:
                    print(f"No text extracted for {original_filename}, content_type: {content_type}")
                    
                self.upload_progress[original_filename] = 50
                self.upload_status[original_filename] = lang.tr_str("upload_chunking")
                yield

                chunks = chunk_text(text)
                logger.info(f"Number of chunks for {original_filename}: {len(chunks)}")
                if not chunks:
                    print(f"No chunks created for {original_filename}")

                self.upload_progress[original_filename] = 60
                self.upload_status[original_filename] = lang.tr_str("upload_embedding")
                yield

                embeddings = await generate_embeddings([chunk['text'] for chunk in chunks])
                logger.info(f"Number of embeddings for {original_filename}: {len(embeddings)}")

                self.upload_progress[original_filename] = 80
                self.upload_status[original_filename] = lang.tr_str("upload_db_updating")
                yield

                logger.info(f"Using document_id: {document_id} for {original_filename}")
                records_to_insert = [
                    {
                        "owner_id": user_id,
                        "document_id": document_id,
                        "content": chunk['text'],
                        "embedding": embedding,
                    }
                    for chunk, embedding in zip(chunks, embeddings)
                ]
                logger.info(f"Number of records to insert for {original_filename}: {len(records_to_insert)}")
                
                if records_to_insert:
                    response = supabase_client.table("document_sections").insert(records_to_insert).execute()
                    logger.info(f"Insert response for {original_filename}: data length={len(response.data) if response.data else 0}, count={response.count}")
                else:
                    logger.info(f"No records to insert for {original_filename}")

                self.upload_progress[original_filename] = 100
                self.upload_status[original_filename] = lang.tr_str("status_done")

                yield
                    
            except Exception as e:
                self.upload_status[original_filename] = lang.tr_str("status_failed")
                self.upload_errors[original_filename] = lang.tr_str("upload_error", error=str(e))
                self.upload_progress[original_filename] = 100
                yield
                
        if successful_uploads > 0:
            self.alert_message = lang.tr_str("docs_upload_success_alert", ok=successful_uploads, total=len(files))
            self.show_alert = True
            yield DocumentState.load_documents_on_page_load
        
        await asyncio.sleep(5)
        self.is_uploading = False
        self.upload_progress = {}
        self.upload_status = {}
        self.upload_errors = {}
        yield
                                    
    async def delete_document(self, doc_id: str):
        self.is_loading = True
        yield
        lang = await self.get_state(LanguageState)

        try:
            auth_state = await self.get_state(AuthState)
            if not auth_state.user:
                raise Exception(lang.tr_str("user_not_found"))

            db_client = await self._get_authenticated_client()

            response = db_client.from_("documents").select("storage_path, owner_id").eq("id", doc_id).execute()
            if not response.data:
                raise Exception(lang.tr_str("doc_not_found"))

            doc_data = response.data[0]
            if doc_data["owner_id"] != auth_state.user.id:
                raise Exception(lang.tr_str("delete_no_permission"))

            storage_path = doc_data["storage_path"]

            if storage_path.startswith(f"{BUCKET_NAME}/"):
                path_to_remove = storage_path[len(f"{BUCKET_NAME}/"):]
            else:
                path_to_remove = storage_path

            supabase_client = await self._get_supabase_client()
            storage_response = supabase_client.storage.from_(BUCKET_NAME).remove([path_to_remove])
            if not storage_response:
                raise Exception(lang.tr_str("storage_delete_failed"))

            db_client.from_("documents").delete().eq("id", doc_id).execute()

            self.documents = [doc for doc in self.documents if doc["id"] != doc_id]

            self.alert_message = lang.tr_str("doc_delete_success")
            self.show_alert = True

        except Exception as e:
            self.alert_message = lang.tr_str("doc_delete_failed", error=str(e))
            self.show_alert = True

        finally:
            self.is_loading = False
            yield
