import reflex as rx
from AIAgentForge.state.n8n2langgraph_state import N8nConvertState
from AIAgentForge.components.navbar import navbar

def env_hint_list():
    return rx.vstack(
        rx.heading("ENV 힌트", size="4"),
        rx.cond(
            N8nConvertState.env_hints,
            rx.vstack(
                rx.foreach(
                    N8nConvertState.env_hints_list,
                    lambda kv: rx.box(
                        rx.text(f"툴: {kv[0]}"),
                        rx.unordered_list(
                            rx.foreach(kv[1], lambda e: rx.list_item(e))
                        ),
                        padding="0.5rem",
                        border=f"1px solid {rx.color('gray', 5)}",
                        border_radius="8px",
                        width="100%",
                    ),
                ),
                spacing="2",
                width="100%",
            ),
            rx.text("필요한 ENV 없음"),
        ),
        width="100%",
        spacing="3",
    )


def code_preview():
    return rx.box(
        rx.heading("생성된 코드", size="4"),
        rx.box(
            rx.text(N8nConvertState.converted_code, font_family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas", white_space="pre-wrap"),
            padding="0.75rem",
            border=f"1px solid {rx.color('gray',5)}",
            border_radius="8px",
            max_height="50vh",
            overflow_y="auto",
            width="100%",
        ),
        rx.hstack(
            rx.button("다운로드", on_click=N8nConvertState.download_py, disabled=rx.cond(N8nConvertState.converted_code == "", True, False)),
            spacing="3",
        ),
        width="100%",
        spacing="3",
    )

def input_section():
    return rx.vstack(
        rx.heading("n8n 워크플로우 JSON 입력", size="5"),
        rx.upload(
            rx.vstack(
                rx.text("여기에 JSON 파일을 드롭하거나 클릭해서 선택"),
                rx.button("파일 선택"),
                rx.text(N8nConvertState.uploaded_filename, color=rx.color("gray", 10)),
                align="center",
            ),
            accept={"application/json"},
            max_files=1,
            on_drop=N8nConvertState.handle_upload,
            width="100%",
            border=f"2px dashed {rx.color('gray',7)}",
            padding="1rem",
            border_radius="10px",
        ),
        rx.text_area(
            placeholder="여기에 JSON을 직접 붙여넣기",
            value=N8nConvertState.json_text,
            on_change=N8nConvertState.set_json_text,
            min_height="220px",
            width="100%",
        ),
        rx.hstack(
            rx.button("변환", on_click=N8nConvertState.convert),
            rx.text(N8nConvertState.error, color="red"),
            spacing="3",
        ),
        width="100%",
        spacing="3",
    )

def n8n_convert_page() -> rx.Component:
    return rx.vstack(
        navbar(),
        rx.vstack(
            input_section(),
            env_hint_list(),
            code_preview(),
            width="100%",
            max_width="980px",
            spacing="6",
        ),
        align="center",
        width="100%",
        padding_x="1rem",
        padding_y="1rem",
    )
