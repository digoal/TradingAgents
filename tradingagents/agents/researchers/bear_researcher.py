from langchain_core.messages import AIMessage
import time
import json


def create_bear_researcher(llm, memory):
    def bear_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")

        current_response = investment_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""你是一名看空研究员，负责建立一套反对投资该股票的严谨论证。你的目标是突出风险、挑战和负面信号，并有效反驳看多观点。

请重点围绕以下方面展开：
- 风险与挑战：市场饱和、财务不稳定、宏观逆风、监管或行业压力等。
- 竞争劣势：市场地位下降、创新乏力、竞争对手威胁、盈利模式脆弱等。
- 负面信号：财务数据恶化、技术走势不佳、近期利空新闻、情绪走弱等。
- 反驳看多观点：用具体数据和严谨逻辑指出对方论据中的漏洞、夸大或过度乐观假设。
- 讨论方式：请以辩论口吻直接回应对方观点，不要只是列事实。

可用资料：
市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新时事与宏观新闻：{news_report}
公司基本面报告：{fundamentals_report}
当前辩论历史：{history}
上一轮看多观点：{current_response}
类似情境下的历史反思与经验：{past_memory_str}

请基于以上信息，输出一段有说服力的中文辩论内容。你必须吸收历史反思中的经验教训，避免重复过去的错误。
"""

        response = llm.invoke(prompt)

        argument = f"Bear Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bear_node
