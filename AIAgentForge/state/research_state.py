import os
import reflex as rx
import asyncio
import logging
from typing import List, Dict, Any
from ..agents.researcher import (
    get_sub_questions,
    run_researcher,
    write_report,
)

# --- Basic logging configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ResearchState(rx.State):
    """
    Manages the entire research process, from user input to final report generation.
    """
    # Core state variables
    main_question: str = ""
    tavily_api_key: str = ""
    sub_questions: List[str] = []
    research_results: List[Dict[str, Any]] = []
    report: str = ""

    # UI control variables
    is_generating: bool = False
    current_status: str = ""
    # New variable to manage the research flow stage
    research_stage: str = "initial"  # Stages: "initial", "editing_subquestions", "researching", "complete"

    @rx.var
    def is_form_valid(self) -> bool:
        """Check if the form can be submitted."""
        return bool(self.main_question.strip())

    # --- Event Handlers for Sub-question Editing ---
    def update_sub_question(self, index: int, value: str):
        """Updates a sub-question at a given index."""
        if 0 <= index < len(self.sub_questions):
            self.sub_questions[index] = value

    def delete_sub_question(self, index: int):
        """Deletes a sub-question at a given index."""
        if 0 <= index < len(self.sub_questions):
            self.sub_questions.pop(index)
    
    def add_sub_question(self):
        """Adds a new, empty sub-question to the list."""
        self.sub_questions.append("새로운 질문을 입력하세요...")

    # --- Main Process Flow ---
    @rx.event(background=True)
    async def generate_sub_questions_for_editing(self, form_data: dict):
        """Step 1: Generate initial sub-questions and enter the editing stage."""
        # --- [FIXED] Move state modifications inside the async context manager ---
        main_question_from_form = form_data.get("main_question", "").strip()
        
        async with self:
            self.main_question = main_question_from_form
            if not self.main_question:
                return

            # Reset state for a new task
            self.is_generating = True
            self.sub_questions = []
            self.research_results = []
            self.report = ""
            self.research_stage = "initial"
            self.current_status = "초기 하위 질문 생성 중..."
        
        try:
            logging.info("Generating initial sub-questions...")
            sub_qs = await asyncio.to_thread(get_sub_questions, self.main_question)
            async with self:
                self.sub_questions = sub_qs
                self.research_stage = "editing_subquestions"
                self.current_status = "생성된 하위 질문을 검토하고 수정하세요."
            logging.info(f"✅ Generated {len(self.sub_questions)} sub-questions for editing.")
        except Exception as e:
            logging.error(f"Error generating sub-questions: {e}", exc_info=True)
            async with self:
                self.current_status = f"오류 발생: {e}"
        finally:
            async with self:
                self.is_generating = False

    @rx.event(background=True)
    async def run_research_on_sub_questions(self):
        """Step 2: Run research on the (potentially edited) list of sub-questions."""
        async with self:
            if not self.sub_questions or all(not q.strip() for q in self.sub_questions):
                self.current_status = "리서치를 진행할 하위 질문이 없습니다."
                return

            self.is_generating = True
            self.research_stage = "researching"
            self.research_results = []
            self.report = ""
            self.current_status = f"{len(self.sub_questions)}개의 하위 질문에 대해 리서치 진행 중..."

        try:
            logging.info(f"Starting research for sub-questions: {self.sub_questions}")
            
            # Use asyncio.gather to run all research tasks concurrently and maintain order
            tasks = [run_researcher(sq, self.tavily_api_key) for sq in self.sub_questions]
            all_results = await asyncio.gather(*tasks)
            
            async with self:
                self.research_results = all_results
                self.current_status = f"리서치 완료 ({len(self.sub_questions)}/{len(self.sub_questions)})"
            logging.info("✅ All research tasks completed.")

            # Step 3: Write the Final Report
            async with self:
                self.current_status = "최종 보고서 작성 중..."
            
            logging.info("Writing final report...")
            final_report = await asyncio.to_thread(write_report, self.research_results, self.main_question)
            async with self:
                self.report = final_report
                self.research_stage = "complete"
            logging.info("✅ Final report generated.")

            async with self:
                self.current_status = "리서치 완료!"
            logging.info("🎉 Research process finished successfully.")

        except Exception as e:
            logging.error(f"An error occurred during the research process: {e}", exc_info=True)
            async with self:
                self.current_status = f"오류 발생: {e}"
        finally:
            async with self:
                self.is_generating = False
            logging.info("State `is_generating` set to False. Process ended.")
