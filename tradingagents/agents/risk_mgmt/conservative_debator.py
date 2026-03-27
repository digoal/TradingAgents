from langchain_core.messages import AIMessage
import time
import json


def create_conservative_debator(llm):
    def conservative_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        conservative_history = risk_debate_state.get("conservative_history", "")

        current_aggressive_response = risk_debate_state.get("current_aggressive_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        prompt = f"""你是保守型风险分析师。你的首要目标是保护资产、降低波动，并争取稳定、可持续的收益。你优先考虑安全性、稳健性和风险控制，会仔细评估潜在亏损、经济下行和市场波动。当你评估交易员的决策或计划时，请重点审视其中的高风险部分，指出该决策可能让组合暴露在哪些不必要的风险中，以及更谨慎的替代方案如何更有利于长期收益。以下是交易员的决策：

{trader_decision}

你的任务是正面反驳激进派和中性派的论点，指出他们在哪些地方忽略了潜在威胁，或者没有充分重视可持续性。请直接回应他们的观点，并结合以下资料为一种更低风险的调整方案建立有说服力的中文论证：

市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新时事与宏观报告：{news_report}
公司基本面报告：{fundamentals_report}
当前讨论历史：{history} 激进派上一轮观点：{current_aggressive_response} 中性派上一轮观点：{current_neutral_response}。如果其他视角尚未发言，请先基于现有资料提出你自己的主张。

请通过质疑他们的乐观假设，强调被忽略的下行风险，并逐点回应他们的论据，说明为什么保守立场更有利于保护组合资产。重点是辩论和批判性分析，而不只是陈述资料。最终输出使用中文，自然表达即可，不需要特殊格式。"""

        response = llm.invoke(prompt)

        argument = f"Conservative Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "aggressive_history": risk_debate_state.get("aggressive_history", ""),
            "conservative_history": conservative_history + "\n" + argument,
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Conservative",
            "current_aggressive_response": risk_debate_state.get(
                "current_aggressive_response", ""
            ),
            "current_conservative_response": argument,
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return conservative_node
