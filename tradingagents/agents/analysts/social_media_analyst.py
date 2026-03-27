from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import build_instrument_context, get_news
from tradingagents.dataflows.config import get_config


def create_social_media_analyst(llm):
    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        instrument_context = build_instrument_context(state["company_of_interest"])

        tools = [
            get_news,
        ]

        system_message = (
            "你是一名社交媒体与公司舆情分析研究员，负责分析某家公司过去一周内的社交媒体讨论、公司相关新闻和公众情绪。请撰写一份完整的中文报告，说明市场在讨论什么、情绪变化如何、哪些信息可能影响投资者预期，以及这些因素对交易和投资决策的意义。"
            + " 请使用 `get_news(query, start_date, end_date)` 搜索公司相关新闻和社交媒体相关讨论，尽量覆盖多种来源。"
            + " 报告最终必须使用中文 Markdown 输出，并在末尾附上一张 Markdown 表格，用于整理关键舆情主题、情绪方向、证据来源和交易启示。"
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一名与其他助手协作的 AI 助手。"
                    " 请使用提供的工具推进任务。"
                    " 如果你暂时无法完整回答，也没关系，其他具备不同工具的助手会接续完成。"
                    " 请先完成你当前能完成的部分。"
                    " 如果你或其他助手已经形成 FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** 或最终交付物，"
                    " 请保留该英文标记前缀不变，便于团队识别何时停止。"
                    " 你可以使用以下工具：{tool_names}。\n{system_message}"
                    " 当前日期是 {current_date}。{instrument_context}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(instrument_context=instrument_context)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "sentiment_report": report,
        }

    return social_media_analyst_node
