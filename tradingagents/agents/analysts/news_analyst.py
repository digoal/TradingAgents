from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import (
    build_instrument_context,
    get_global_news,
    get_news,
)
from tradingagents.dataflows.config import get_config


def create_news_analyst(llm):
    def news_analyst_node(state):
        current_date = state["trade_date"]
        instrument_context = build_instrument_context(state["company_of_interest"])

        tools = [
            get_news,
            get_global_news,
        ]

        system_message = (
            "你是一名新闻研究员，负责分析过去一周内与交易和宏观经济相关的重要新闻和趋势。请撰写一份全面的中文报告，概括当前全球环境、宏观驱动因素、行业或公司相关新闻，以及这些变化对交易决策可能带来的影响。"
            + " 你可以使用以下工具：`get_news(query, start_date, end_date)` 用于公司或主题定向新闻检索，`get_global_news(curr_date, look_back_days, limit)` 用于更广泛的宏观新闻检索。"
            + " 报告最终必须使用中文 Markdown 输出，并在末尾附上一张 Markdown 表格，用于整理关键事件、市场影响、风险点和潜在机会。"
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
            "news_report": report,
        }

    return news_analyst_node
