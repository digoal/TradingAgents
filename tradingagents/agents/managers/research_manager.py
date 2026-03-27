import time
import json

from tradingagents.agents.utils.agent_utils import build_instrument_context


def create_research_manager(llm, memory):
    def research_manager_node(state) -> dict:
        instrument_context = build_instrument_context(state["company_of_interest"])
        history = state["investment_debate_state"].get("history", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        investment_debate_state = state["investment_debate_state"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""你现在是投资研究经理兼辩论主持人。你的任务是审慎评估本轮多空辩论，并做出明确结论：支持看空、支持看多，或者只有在论据非常充分时才选择 Hold。

请简明总结双方最关键的论点，重点关注最有说服力的证据和推理。你的建议必须清晰、可执行，并避免因为双方都有道理就机械地选择 Hold。你需要基于更强的一方给出明确立场。

此外，你还要为交易员制定一份详细的投资计划，至少包括：
- 你的结论：明确给出 Buy、Sell 或 Hold。
- 结论依据：说明为什么这些证据和推理支持你的判断。
- 执行策略：给出具体执行步骤，例如观察点、入场思路、仓位节奏、风险控制重点。

请结合以往类似情境中的错误反思，修正你的判断方式并持续改进。最终输出必须为中文，语气自然，但结构要清晰。

以下是你过去的反思记录：
\"{past_memory_str}\"

{instrument_context}

以下是本轮辩论内容：
辩论历史：
{history}"""
        response = llm.invoke(prompt)

        new_investment_debate_state = {
            "judge_decision": response.content,
            "history": investment_debate_state.get("history", ""),
            "bear_history": investment_debate_state.get("bear_history", ""),
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": response.content,
            "count": investment_debate_state["count"],
        }

        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": response.content,
        }

    return research_manager_node
