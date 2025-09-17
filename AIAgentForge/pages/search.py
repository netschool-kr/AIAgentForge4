# AIAgentForge/pages/search.py
import reflex as rx
from typing import Dict, Any
from AIAgentForge.components.navbar import navbar
from AIAgentForge.state.search_state import SearchState
from AIAgentForge.state.document_state import DocumentState
from AIAgentForge.state.language_state import LanguageState

SearchResult = Dict[str, Any]

def render_search_result(result: SearchResult) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(
                    rx.fragment(
                        LanguageState.t["label_id"], f": {result['id']}"
                    ),
                    size="3",
                ),
                rx.spacer(),
                rx.badge(
                    rx.fragment(
                        LanguageState.t["label_score"], f": {result['rrf_score']:.2f}"
                    ),
                    color_scheme="green",
                ),
                align="center",
                width="100%",
            ),
            rx.text(result["content"], as_="p", size="2", color_scheme="gray"),
            spacing="2",
            width="100%",
        ),
        width="100%",
    )

@rx.page(route="/search", title="Search")
def search_page() -> rx.Component:
    return rx.container(
        rx.vstack(
            navbar(),

            # 헤딩: Var와 str를 결합하지 말고 fragment로 묶기
            rx.heading(
                rx.fragment(
                    LanguageState.t["hybrid_search_engine"],
                    " (", DocumentState.collection_name, ")",
                ),
                size="7",
                align="center",
                margin_bottom="1em",
            ),

            rx.form(
                rx.hstack(
                    rx.input(
                        value=SearchState.search_query,
                        on_change=SearchState.set_search_query,
                        placeholder=LanguageState.t["input_placeholder"],
                        size="3",
                        flex_grow=1,
                    ),
                    rx.button(
                        LanguageState.t["btn_search"],
                        is_loading=SearchState.is_loading,
                        size="3",
                        type_="submit",
                    ),
                    spacing="2",
                    width="100%",
                ),
                on_submit=SearchState.handle_search,
                width="100%",
            ),

            rx.divider(margin_y="2em"),

            rx.cond(
                SearchState.is_loading,
                rx.center(rx.spinner(size="3"), width="100%"),
                rx.vstack(
                    rx.cond(
                        SearchState.llm_answer,
                        rx.vstack(
                            rx.heading(LanguageState.t["answer_heading"], size="5"),
                            rx.card(rx.markdown(SearchState.llm_answer), width="100%"),
                            align="start",
                            width="100%",
                        ),
                        rx.center(
                            rx.text(LanguageState.t["search_initial_hint"], color_scheme="gray"),
                            width="100%",
                            height="10em",
                        ),
                    ),
                    rx.cond(
                        SearchState.search_results,
                        rx.vstack(
                            rx.heading(LanguageState.t["sources_heading"], size="5", margin_top="2em"),
                            rx.foreach(SearchState.search_results, render_search_result),
                            spacing="4",
                            width="100%",
                            align="start",
                        ),
                    ),
                    spacing="5",
                    width="100%",
                ),
            ),
            spacing="4",
            width="100%",
            max_width="960px",
        ),
        # 언어 전환 버튼
        rx.hstack(
            rx.button("한국어", on_click=lambda: LanguageState.set_locale("ko")),
            rx.button("English", on_click=lambda: LanguageState.set_locale("en")),
            rx.button("日本語", on_click=lambda: LanguageState.set_locale("ja")),
            spacing="4"
        ),
        
        padding_x="1em",
        padding_y="2em",
    )
