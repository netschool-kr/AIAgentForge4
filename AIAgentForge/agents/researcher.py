import os
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults
from .prompts import SUB_QUESTION_PROMPT, RESEARCHER_PROMPT, WRITER_PROMPT

# It's recommended to set OPENAI_API_KEY in your environment variables
# For this app, TAVILY_API_KEY is passed from the UI
# os.environ["OPENAI_API_KEY"] = "sk-..."

def get_llm():
    """Initializes and returns the ChatOpenAI model."""
    return ChatOpenAI(model="gpt-4o", temperature=0)

def get_sub_questions(main_question: str) -> List[str]:
    """
    Generates a list of sub-questions from the main user question.
    """
    llm = get_llm()
    chain = SUB_QUESTION_PROMPT | llm | StrOutputParser()
    result = chain.invoke({"main_question": main_question})
    # Split the result into a list of questions
    return [q.strip() for q in result.strip().split("\n") if q.strip()]

async def run_researcher(sub_question: str, tavily_api_key: str) -> Dict[str, Any]:
    """
    Performs research for a single sub-question using Tavily and summarizes the results.
    This is an async function to allow for concurrent execution.
    """
    # 1. Search for context
    search_tool = TavilySearchResults(api_key=tavily_api_key, max_results=5)
    context_results = await search_tool.ainvoke(sub_question)
    
    # Format context for the LLM
    context = "\n\n".join([f"URL: {res['url']}\nContent: {res['content']}" for res in context_results])

    # 2. Summarize context
    llm = get_llm()
    chain = RESEARCHER_PROMPT | llm | StrOutputParser()
    summary = await chain.ainvoke({
        "sub_question": sub_question,
        "context": context
    })
    
    return {"sub_question": sub_question, "summary": summary}

def write_report(research_results: List[Dict[str, Any]], main_question: str) -> str:
    """
    Writes the final report by synthesizing all research summaries.
    """
    # Format the summaries for the writer prompt
    formatted_summaries = "\n\n".join(
        [f"### {res['sub_question']}\n{res['summary']}" for res in research_results]
    )
    
    llm = get_llm()
    chain = WRITER_PROMPT | llm | StrOutputParser()
    report = chain.invoke({
        "main_question": main_question,
        "summaries": formatted_summaries
    })
    return report

