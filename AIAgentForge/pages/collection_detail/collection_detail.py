# AIAgentForge/pages/collection_detail/collection_detail.py
import reflex as rx
from ...state.document_state import DocumentState
from ...state.auth_state import AuthState
from AIAgentForge.components.navbar import navbar  # Navbar 임포트 추가
from ...state.language_state import LanguageState  # ← 추가

def render_upload_progress() -> rx.Component:
    """각 파일의 업로드 진행 상황을 동적으로 렌더링합니다."""
    return rx.cond(
        DocumentState.is_uploading,
        rx.vstack(
            rx.foreach(
                DocumentState.upload_status.keys(),
                lambda filename: rx.vstack(
                    rx.hstack(
                        rx.text(filename, as_="b"),
                        rx.text(DocumentState.upload_status.get(filename, "")),
                        spacing="3",
                    ),
                    rx.progress(value=DocumentState.upload_progress.get(filename, 0), width="100%"),
                    rx.cond(
                        DocumentState.upload_errors.get(filename),
                        rx.callout(
                            DocumentState.upload_errors.get(filename, ""),
                            icon="triangle_alert",
                            color_scheme="red",
                            width="100%",
                        ),
                    ),
                    width="100%",
                    padding_y="0.5em",
                ),
            ),
            width="100%",
            padding_top="1em",
        ),
    )

def document_list() -> rx.Component:
    """DB에 저장된 문서 목록을 표시합니다."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell(LanguageState.t["col_doc_name"]),
                rx.table.column_header_cell(LanguageState.t["col_created_at"]),
                rx.table.column_header_cell(LanguageState.t["col_actions"]),
            )
        ),
        rx.table.body(
            rx.foreach(
                DocumentState.documents,
                lambda doc: rx.table.row(
                    rx.table.cell(doc["name"]),
                    rx.table.cell(doc["created_at"]),
                    rx.table.cell(
                        rx.button(
                            LanguageState.t["btn_delete"],
                            color_scheme="red",
                            variant="soft",
                            on_click=DocumentState.delete_document(doc["id"])
                        )
                    ),
                )
            )
        ),
        width="100%",
    )


@rx.page(
    route="/collections/[collection_id]",
    on_load=[DocumentState.init_on_load],  # check_auth를 따로 넣지 않음
)
def collection_detail_page() -> rx.Component:
    """컬렉션 상세 페이지 UI (업로드 기능 포함)"""
    return rx.container(
        navbar(),
        rx.hstack(
            # "컬렉션: {name}" → 다국어 + 이름 분리 렌더링
            rx.heading(LanguageState.t["collection_heading"], size="5", margin_bottom="1em"),
            rx.heading(DocumentState.collection_name, size="5", margin_bottom="1em"),
            rx.spacer(),
            rx.link(LanguageState.t["link_search"], href="/search", size="5", margin_bottom="1em"),
            rx.spacer(),
            rx.spacer(),
        ),
        rx.hstack(
            spacing="4",
            margin_bottom="1em",
        ),
        rx.upload(
            rx.vstack(
                rx.button(LanguageState.t["btn_choose_files"], type="button"),
                rx.text(LanguageState.t["upload_drag_drop_hint"]),
                align="center",
            ),
            id="upload",
            border="1px dotted rgb(107, 114, 128)",
            padding="2em",
            width="100%",
            is_disabled=DocumentState.is_uploading,
            on_drop=DocumentState.handle_upload(
                rx.upload_files(upload_id="upload")
            ),
        ),
        render_upload_progress(),
        rx.divider(margin_y="2em"),
        rx.heading(LanguageState.t["heading_uploaded_docs"], size="4", margin_bottom="1em"),
        rx.cond(
            DocumentState.is_loading,
            rx.spinner(),
            document_list()
        ),
    )
