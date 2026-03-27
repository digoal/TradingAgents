from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import (
    build_instrument_context,
    get_balance_sheet,
    get_cashflow,
    get_fundamentals,
    get_income_statement,
    get_insider_transactions,
)
from tradingagents.dataflows.config import get_config


def create_fundamentals_analyst(llm):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        instrument_context = build_instrument_context(state["company_of_interest"])

        tools = [
            get_fundamentals,
            get_balance_sheet,
            get_cashflow,
            get_income_statement,
        ]

        system_message = (
            "你是一名基本面研究员，负责分析某家公司过去一周内可获得的基本面信息。请撰写一份全面、细致的中文报告，覆盖公司概况、财务报表、核心财务指标、历史财务表现，以及这些信息对交易和投资决策的影响。尽量提供充分细节，并基于证据给出具体、可执行的判断。"
            + " 报告最终必须使用中文 Markdown 输出，并在末尾附上一张 Markdown 表格，用于清晰整理关键结论、主要证据、潜在风险和交易含义。"
            + " 可使用以下工具：`get_fundamentals` 用于公司综合分析，`get_balance_sheet`、`get_cashflow` 和 `get_income_statement` 用于获取具体财务报表。",
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
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node
