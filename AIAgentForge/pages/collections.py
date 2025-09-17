# langconnect_fullstack/pages/collections.py
import reflex as rx
from ..state.collection_state import CollectionState
from ..state.auth_state import AuthState
from AIAgentForge.components.navbar import navbar
from AIAgentForge.state.language_state import LanguageState  # ← 추가

def collection_row(collection: dict) -> rx.Component:
    """테이블의 각 행을 렌더링하고 상세 페이지로 연결"""
    return rx.table.row(
        rx.table.cell(
            rx.link(
                collection["name"],
                href=f"/collections/{collection['id']}",
            )
        ),
        rx.table.cell(collection["created_at"]),
        rx.table.cell(
            rx.button(
                LanguageState.t["delete_button"],
                on_click=lambda: CollectionState.show_confirm(collection["id"]),
                color_scheme="red",
            )
        ),
    )

@rx.page(route="/collections", on_load=[AuthState.check_auth, CollectionState.load_collections])
def collections_page() -> rx.Component:
    """컬렉션 관리 페이지 UI"""
    return rx.cond(
        AuthState.is_authenticated,
        rx.container(
            navbar(),
            rx.heading(LanguageState.t["collections_title"], size="5"),
            rx.form.root(
                rx.hstack(
                    rx.input(
                        name="name",
                        placeholder=LanguageState.t["new_collection_name_placeholder"],
                        required=True,
                    ),
                    rx.button(LanguageState.t["create_button"], type="submit"),
                ),
                on_submit=CollectionState.create_collection,
                reset_on_submit=True,
            ),
            rx.cond(
                CollectionState.is_loading,
                rx.spinner(),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell(LanguageState.t["name"]),
                            rx.table.column_header_cell(LanguageState.t["col_created_at"]),
                            rx.table.column_header_cell(LanguageState.t["col_actions"]),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(CollectionState.collections, collection_row)
                    ),
                ),
            ),
            rx.dialog.root(
                rx.dialog.content(
                    rx.dialog.title(LanguageState.t["delete_button"]),
                    rx.dialog.description(LanguageState.t["collection_delete_fail"]),  # 설명 키가 없으므로 임시로 재사용
                    rx.flex(
                        rx.button(
                            LanguageState.t["login_link"],  # '취소' 전용 키가 없으므로 임시 재사용 시 교체 권장
                            on_click=CollectionState.cancel_delete,
                            color_scheme="gray",
                            variant="soft",
                        ),
                        rx.button(
                            LanguageState.t["delete_button"],
                            on_click=CollectionState.confirm_delete,
                            color_scheme="red",
                        ),
                        spacing="3",
                        margin_top="16px",
                        justify="end",
                    ),
                ),
                open=CollectionState.show_confirm_modal,
                on_open_change=CollectionState.set_show_confirm_modal,
            ),
            rx.hstack(
                rx.button("한국어", on_click=lambda: LanguageState.set_locale("ko")),
                rx.button("English", on_click=lambda: LanguageState.set_locale("en")),
                rx.button("日本語", on_click=lambda: LanguageState.set_locale("ja")),
                spacing="4"
            ),
                        
            size="4",
        ),
        rx.container(
            rx.text(LanguageState.t["login_heading"]),
            rx.link(LanguageState.t["login_link"], href="/login"),
            size="4",
        ),
    )
