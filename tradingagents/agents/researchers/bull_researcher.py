from langchain_core.messages import AIMessage
import time
import json


def create_bull_researcher(llm, memory):
    def bull_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")

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

        prompt = f"""你是一名看多研究员，负责为投资该股票建立一套有说服力、基于证据的正面论证。你的重点是强调增长潜力、竞争优势、积极的市场信号，并有效反驳看空观点。

请重点围绕以下方面展开：
- 增长潜力：公司的市场机会、收入增长空间、业务扩张能力。
- 竞争优势：独特产品、品牌、渠道、技术壁垒或市场地位。
- 积极信号：财务健康度、行业趋势、近期利好新闻、经营改善等。
- 反驳看空观点：用具体数据和严谨逻辑回应对方的风险论点，说明为什么看多逻辑更强。
- 讨论方式：请以辩论口吻直接回应对方观点，不要只是罗列资料。

可用资料：
市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新时事与宏观新闻：{news_report}
公司基本面报告：{fundamentals_report}
当前辩论历史：{history}
上一轮看空观点：{current_response}
类似情境下的历史反思与经验：{past_memory_str}

请基于以上信息，输出一段有说服力的中文辩论内容。你必须吸收历史反思中的经验教训，避免重复过去的错误。
"""

        response = llm.invoke(prompt)

        argument = f"Bull Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node
