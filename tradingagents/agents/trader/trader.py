import functools
import time
import json

from tradingagents.agents.utils.agent_utils import build_instrument_context


def create_trader(llm, memory):
    def trader_node(state, name):
        company_name = state["company_of_interest"]
        instrument_context = build_instrument_context(company_name)
        investment_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            past_memory_str = "No past memories found."

        context = {
            "role": "user",
            "content": f"以下是一份基于分析师团队综合研究后形成、适用于 {company_name} 的投资计划。{instrument_context} 该计划综合考虑了当前技术面、宏观环境与社交媒体情绪。请以此为基础，评估并形成你的下一步交易决策。\n\n建议投资计划：{investment_plan}\n\n请结合这些信息做出审慎且具有执行性的判断，最终输出使用中文。",
        }

        messages = [
            {
                "role": "system",
                "content": f"""你是一名交易员，负责基于市场信息做出投资决策。请给出明确的买入、卖出或持有建议，并用中文说明你的逻辑、执行思路、关键风险与观察点。为了兼容系统流程，你的回答最后一行必须保留英文标记 'FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**'，不要翻译这行。请吸收过去类似交易中的经验教训，提升这次分析质量。以下是类似情境下的历史反思：{past_memory_str}""",
            },
            context,
        ]

        result = llm.invoke(messages)

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")
