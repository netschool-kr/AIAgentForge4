# AIAgentForge/aiagentforge/pages/research.py
import reflex as rx
from ..state.research_state import ResearchState
from AIAgentForge.components.navbar import navbar
from AIAgentForge.state.language_state import LanguageState  # i18n



def step_card(*children, **props):
    """단계별 UI를 감싸는 카드 컴포넌트."""
    return rx.card(
        rx.vstack(
            *children,
            spacing="4",
            align="stretch",
        ),
        width="100%",
        **props,
    )


def result_card(title: rx.Var | str, content: rx.Component) -> rx.Component:
    """결과 섹션 카드."""
    return step_card(
        rx.heading(title, size="5"),
        content,
    )


def sub_question_editor() -> rx.Component:
    """하위 질문 편집 섹션."""
    return rx.vstack(
        rx.foreach(
            ResearchState.sub_questions,
            lambda item, i: rx.hstack(
                rx.input(
                    value=item,
                    on_change=lambda val: ResearchState.update_sub_question(i, val),
                    # Corrected: Use an f-string to embed the Reflex variable directly.
                    placeholder=f'{LanguageState.t["subq_placeholder_indexed_prefix"]} #{i + 1}',
                    width="100%",
                ),
                rx.icon_button(
                    rx.icon("trash-2", size=20),
                    on_click=lambda: ResearchState.delete_sub_question(i),
                    variant="soft",
                    color_scheme="red",
                ),
                spacing="2",
                width="100%",
            ),
        ),
        rx.hstack(
            rx.button(
                LanguageState.t["btn_add_question"],
                on_click=ResearchState.add_sub_question,
                variant="outline",
            ),
            rx.spacer(),
            rx.button(
                LanguageState.t["btn_start_research_with_edits"],
                on_click=ResearchState.run_research_on_sub_questions,
                is_loading=ResearchState.is_generating,
                disabled=ResearchState.is_generating,
                size="3",
            ),
            width="100%",
            justify="between",
        ),
        spacing="3",
        width="100%",
    )


def research_page() -> rx.Component:
    """리서치 에이전트 메인 페이지."""
    return rx.container(
        rx.vstack(
            navbar(),

            # 타이틀, 서브타이틀
            rx.heading(LanguageState.t["research_agent_title"], size="8", text_align="center"),
            rx.text(LanguageState.t["research_agent_subtitle"], text_align="center"),

            rx.divider(margin_y="6"),

            # 1단계: 메인 질문 입력
            rx.cond(
                ResearchState.research_stage == "initial",
                step_card(
                    rx.heading(LanguageState.t["step1_heading_main_question"], size="5"),
                    rx.form(
                        rx.vstack(
                            rx.text_area(
                                name="main_question",
                                placeholder=LanguageState.t["main_question_placeholder"],
                                width="100%",
                                height="120px",
                                is_required=True,
                            ),
                            rx.button(
                                LanguageState.t["btn_generate_sub_questions"],
                                type="submit",
                                size="3",
                                width="100%",
                                is_loading=ResearchState.is_generating,
                                disabled=ResearchState.is_generating,
                            ),
                            spacing="4",
                        ),
                        on_submit=ResearchState.generate_sub_questions_for_editing,
                        width="100%",
                    ),
                ),
            ),

            # 진행 상태 표시
            rx.cond(
                ResearchState.is_generating,
                step_card(
                    rx.hstack(
                        rx.spinner(),
                        rx.text(ResearchState.current_status),
                        spacing="4",
                        align="center",
                    )
                ),
            ),

            # 2단계: 하위 질문 편집
            rx.cond(
                ResearchState.research_stage == "editing_subquestions",
                result_card(
                    LanguageState.t["card_generated_subqs_editable"],
                    sub_question_editor(),
                ),
            ),

            # 3단계: 사용될 하위 질문 목록 + 요약 진행/결과
            rx.cond(
                (ResearchState.research_stage == "researching") | (ResearchState.research_stage == "complete"),
                rx.fragment(
                    result_card(
                        LanguageState.t["card_subqs_used"],
                        rx.ordered_list(
                            rx.foreach(ResearchState.sub_questions, lambda item: rx.list_item(item))
                        ),
                    ),
                    rx.cond(
                        ResearchState.research_results,
                        result_card(
                            LanguageState.t["card_subq_summaries"],
                            rx.vstack(
                                rx.foreach(
                                    ResearchState.research_results,
                                    lambda res: rx.box(
                                        rx.heading(res["sub_question"], size="3"),
                                        rx.markdown(res["summary"]),
                                        border="1px solid",
                                        border_color=rx.color("gray", 6),
                                        padding="4",
                                        border_radius="var(--radius-3)",
                                        width="100%",
                                    ),
                                ),
                                spacing="4",
                                width="100%",
                            ),
                        ),
                    ),
                ),
            ),

            # 4단계: 최종 보고서
            rx.cond(
                ResearchState.report,
                result_card(
                    LanguageState.t["card_final_report"],
                    rx.box(
                        rx.markdown(
                            ResearchState.report,
                            component_map={
                                "h1": lambda text: rx.heading(text, size="7", margin_y="15px"),
                                "h2": lambda text: rx.heading(text, size="6", margin_y="12px"),
                                "h3": lambda text: rx.heading(text, size="5", margin_y="10px"),
                            },
                        ),
                        border="1px solid",
                        border_color=rx.color("gray", 6),
                        padding="6",
                        border_radius="var(--radius-3)",
                        width="100%",
                    ),
                ),
            ),


            spacing="6",
            width="100%",
            margin_x="auto",
            padding_y="8",
        ),
        size="4",
        # blog.py와 동일 패턴을 원하면 다음 라인을 사용하세요.
        # on_mount=ResearchState.init_state,
    )
