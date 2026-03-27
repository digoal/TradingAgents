import time
import json


def create_aggressive_debator(llm):
    def aggressive_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        aggressive_history = risk_debate_state.get("aggressive_history", "")

        current_conservative_response = risk_debate_state.get("current_conservative_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        prompt = f"""你是激进型风险分析师。你的职责是积极主张高收益、高风险机会，强调大胆策略、上行空间和竞争优势。在评估交易员的决策或计划时，请重点关注潜在收益、成长性和创新带来的红利，即使这意味着更高波动和更高风险。请使用市场数据和情绪信息强化你的论点，并直接回应保守派和中性派的每个观点，用数据驱动的反驳和说服性推理挑战他们。指出他们的谨慎可能错过了哪些关键机会，或他们的假设为何过于保守。以下是交易员的决策：

{trader_decision}

你的任务是围绕交易员的决策建立一套有说服力的中文论证，通过质疑和批评保守派与中性派的立场，说明为什么高收益导向的视角更值得采纳。请结合以下资料展开：

市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新时事与宏观报告：{news_report}
公司基本面报告：{fundamentals_report}
当前讨论历史：{history} 保守派上一轮观点：{current_conservative_response} 中性派上一轮观点：{current_neutral_response}。如果其他视角尚未发言，请先基于现有资料提出你自己的主张。

请积极回应对方提出的具体担忧，指出其逻辑薄弱之处，并强调承担风险以争取超额收益的合理性。重点是辩论和说服，而不只是陈列数据。最终输出使用中文，自然表达即可，不需要特殊格式。"""

        response = llm.invoke(prompt)

        argument = f"Aggressive Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "aggressive_history": aggressive_history + "\n" + argument,
            "conservative_history": risk_debate_state.get("conservative_history", ""),
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Aggressive",
            "current_aggressive_response": argument,
            "current_conservative_response": risk_debate_state.get("current_conservative_response", ""),
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return aggressive_node
