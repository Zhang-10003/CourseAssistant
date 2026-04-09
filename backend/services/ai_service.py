from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from schemas.question import AIQuestionResponse
from setting import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL_NAME

model = ChatOpenAI(
    model=LLM_MODEL_NAME, # 建议使用 qwen-plus
    openai_api_key=LLM_API_KEY,
    openai_api_base=LLM_BASE_URL,
    temperature=0.7
)

parser = JsonOutputParser(pydantic_object=AIQuestionResponse)

async def generate_questions_with_langchain(user_input: str):
    """
    接收自然语言指令，智能提取意图并生成结构化题目
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "你是一个专业的教育专家。请分析用户的出题指令并生成题目。\n"
            "【任务】\n"
            "1. 从指令中识别『主题』和『数量』（若未指定数量则默认生成2道）。\n"
            "2. 严格按 JSON 格式输出。\n"
            "3. 【重要】correct_answer 必须是 options_data 的索引列表 [int]。\n"
            "4. 简答题 options_data 必须为 null。\n"
            "{format_instructions}"
        )),
        ("user", "{user_input}")
    ])

    chain = prompt | model | parser

    try:
        result = await chain.ainvoke({
            "user_input": user_input,
            "format_instructions": parser.get_format_instructions()
        })
        return result.get("questions", [])
    except Exception as e:
        print(f"AI 生成失败: {e}")
        raise e