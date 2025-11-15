from langchain_core.prompts import ChatPromptTemplate
from app.llm.client import get_llm
from app.llm.prompts import LETTER_SYSTEM_PROMPT, LETTER_USER_PROMPT

# DO NOT create LLM here!
# _llm = get_llm()  ← Removed

_letter_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", LETTER_SYSTEM_PROMPT),
        ("user", LETTER_USER_PROMPT),
    ]
)


def generate_letter_node(state: dict) -> dict:
    """
    Generate appeal letter
    
    LLM is created here, not during module import
    """
    # Create LLM only when function is called
    llm = get_llm()
    
    msg = _letter_prompt.format(
        category_name=state["category_name"],
        service_name=state["service_name"],
        problem_text=state["problem_text"],
        service_phone=state.get("service_phone") or "Не вказано",
        service_email=state.get("service_email") or "Не вказано",
        service_address=state.get("service_address") or "Не вказано",
        user_name=state.get("user_name") or "Користувач",
        user_address=state.get("user_address") or "Не вказано",
        user_phone=state.get("user_phone") or "Не вказано",
    )

    resp = llm.invoke(msg)
    content = resp.content
    if isinstance(content, list):
        content = "".join(str(item) for item in content)
    
    return {
        **state,
        "letter_text": content.strip(),
    }
