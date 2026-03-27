import time
import json


def create_neutral_debator(llm):
    def neutral_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        neutral_history = risk_debate_state.get("neutral_history", "")

        current_aggressive_response = risk_debate_state.get("current_aggressive_response", "")
        current_conservative_response = risk_debate_state.get("current_conservative_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        prompt = f"""你是中性风险分析师。你的职责是提供平衡视角，同时权衡交易员决策或计划的潜在收益与风险。你重视全面性，会同时考虑上行空间、下行风险、更广泛的市场趋势、潜在经济变化以及分散化策略。以下是交易员的决策：

{trader_decision}

你的任务是同时挑战激进派和保守派，指出两者在哪些地方可能过度乐观或过度谨慎。请结合以下资料，为一种更均衡、可持续的调整方案建立中文论证：

市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新时事与宏观报告：{news_report}
公司基本面报告：{fundamentals_report}
当前讨论历史：{history} 激进派上一轮观点：{current_aggressive_response} 保守派上一轮观点：{current_conservative_response}。如果其他视角尚未发言，请先基于现有资料提出你自己的主张。

请积极分析双方论点的优缺点，指出激进和保守立场中的薄弱环节，并说明为什么更均衡的风险策略可能兼顾成长性与稳健性。重点是辩论，而不是简单陈列数据。最终输出使用中文，自然表达即可，不需要特殊格式。"""

        response = llm.invoke(prompt)

        argument = f"Neutral Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "aggressive_history": risk_debate_state.get("aggressive_history", ""),
            "conservative_history": risk_debate_state.get("conservative_history", ""),
            "neutral_history": neutral_history + "\n" + argument,
            "latest_speaker": "Neutral",
            "current_aggressive_response": risk_debate_state.get(
                "current_aggressive_response", ""
            ),
            "current_conservative_response": risk_debate_state.get("current_conservative_response", ""),
            "current_neutral_response": argument,
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return neutral_node
