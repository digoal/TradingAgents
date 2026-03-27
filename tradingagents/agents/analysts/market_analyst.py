from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import (
    build_instrument_context,
    get_indicators,
    get_stock_data,
)
from tradingagents.dataflows.config import get_config


def create_market_analyst(llm):

    def market_analyst_node(state):
        current_date = state["trade_date"]
        instrument_context = build_instrument_context(state["company_of_interest"])

        tools = [
            get_stock_data,
            get_indicators,
        ]

        system_message = (
            """你是一名市场技术分析助手，负责分析金融市场并撰写中文报告。你的任务是根据当前市场环境或交易策略，从下列指标中选择**最相关**的一组指标。目标是最多选择 **8 个**互补且不过度重复的指标。以下是指标分类及说明：

移动均线：
- close_50_sma: 50 日 SMA，中期趋势指标。用途：识别趋势方向并作为动态支撑/阻力。提示：滞后于价格，建议结合更快指标提升时效性。
- close_200_sma: 200 日 SMA，长期趋势基准。用途：确认整体趋势，识别金叉/死叉结构。提示：反应较慢，更适合战略级趋势确认。
- close_10_ema: 10 日 EMA，更灵敏的短期均线。用途：捕捉动量快速变化和潜在入场点。提示：震荡行情下噪音较多，建议搭配更长周期均线过滤假信号。

MACD 相关：
- macd: MACD，通过 EMA 差值计算动量。用途：观察交叉和背离，判断趋势变化。提示：低波动或横盘时需配合其他指标确认。
- macds: MACD Signal，MACD 线的平滑信号线。用途：与 MACD 线交叉配合触发交易。提示：应作为更完整策略的一部分，避免误判。
- macdh: MACD Histogram，显示 MACD 与信号线之间的差值。用途：可视化动量强弱并更早发现背离。提示：快速波动行情中可能较敏感，建议增加过滤条件。

动量指标：
- rsi: RSI，相对强弱指标。用途：识别超买/超卖，结合背离判断反转。提示：强趋势中 RSI 可能长时间停留在极值区间，需结合趋势判断。

波动率指标：
- boll: 布林中轨，即 20 日 SMA。用途：作为价格波动基准。提示：结合上下轨使用，更适合识别突破或反转。
- boll_ub: 布林上轨，通常高于中轨 2 个标准差。用途：提示潜在超买或突破区。提示：强趋势中价格可能沿轨运行，需结合其他工具确认。
- boll_lb: 布林下轨，通常低于中轨 2 个标准差。用途：提示潜在超卖。提示：需结合其他分析避免误判反转。
- atr: ATR，平均真实波幅。用途：根据当前波动设置止损和仓位。提示：它是偏滞后的波动度量，适合纳入更完整的风控框架。

成交量相关指标：
- vwma: VWMA，成交量加权均线。用途：结合价格与成交量确认趋势。提示：需留意异常放量带来的扭曲，建议结合其他量能分析。

请选取互补且多样化的指标，避免重复，例如不要选择高度重叠的指标组合。你需要简要说明每个指标为什么适合当前市场环境。调用工具时，请务必使用上面给出的精确指标名，否则调用会失败。请先调用 `get_stock_data` 获取生成指标所需的 CSV，再调用 `get_indicators` 并传入具体指标名。最后输出一份详细、细致的中文 Markdown 报告，解释你观察到的趋势、关键信号、可能的交易机会与风险，并在报告末尾附上一张结构清晰的 Markdown 表格。"""
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
            "market_report": report,
        }

    return market_analyst_node
