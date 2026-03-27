from tradingagents.agents.utils.agent_utils import build_instrument_context


def create_portfolio_manager(llm, memory):
    def portfolio_manager_node(state) -> dict:

        instrument_context = build_instrument_context(state["company_of_interest"])

        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        sentiment_report = state["sentiment_report"]
        trader_plan = state["investment_plan"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""你现在是投资组合经理。请综合风险分析师之间的辩论，并给出最终交易决策。

{instrument_context}

---

**评级范围**（只能选择一个）：
- **Buy**：强烈看好，适合建立或增持仓位
- **Overweight**：整体偏积极，适合逐步提升敞口
- **Hold**：维持当前仓位，暂不采取行动
- **Underweight**：降低敞口，部分止盈或减仓
- **Sell**：退出仓位或避免入场

**背景信息：**
- 交易员建议方案：**{trader_plan}**
- 过往决策经验教训：**{past_memory_str}**

**输出结构要求：**
1. **Rating**：明确写出 Buy / Overweight / Hold / Underweight / Sell 中的一个。
2. **Executive Summary**：用中文简洁说明执行方案，包括入场策略、仓位思路、关键风险位和时间维度。
3. **Investment Thesis**：结合风险分析师辩论与历史反思，详细说明你的判断依据。

---

**风险分析师辩论历史：**
{history}

---

请用中文输出，结论必须果断，并且每一项判断都要尽量落在具体证据上。"""

        response = llm.invoke(prompt)

        new_risk_debate_state = {
            "judge_decision": response.content,
            "history": risk_debate_state["history"],
            "aggressive_history": risk_debate_state["aggressive_history"],
            "conservative_history": risk_debate_state["conservative_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_aggressive_response": risk_debate_state["current_aggressive_response"],
            "current_conservative_response": risk_debate_state["current_conservative_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response.content,
        }

    return portfolio_manager_node
