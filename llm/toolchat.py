"""
带工具的LLM聊天系统 - 与LLMChat相同的接口，但能调用工具
"""
from tools.base import AIToolRegistry, registry, ToolCall, AIResponse
from llm.chat import LLMChat
from typing import Any


def ToolChat(data: Any, question: str, return_type: Any = str, max_iterations: int = 5) -> Any:
    """
    递归式工具调用LLM - 每次只调用一个工具，根据结果决定下一步

    Args:
        data: 输入数据
        question: 处理要求
        return_type: 返回类型
        max_iterations: 最大工具调用轮次

    Returns:
        指定类型的结果
    """
    # 初始化上下文
    context = f"原始数据: {str(data)}\n用户要求: {question}\n\n执行过程:\n"

    for iteration in range(max_iterations):
        # 构建提示词
        tools_desc = registry.get_tools_description()

        prompt = f"""你是一个智能助手，可以使用工具来完成任务。

可用工具:
{tools_desc}

当前上下文:
{context}

请分析当前情况：
1. 如果还需要调用工具来完成任务，返回AIResponse，response_type="tool_call"，包含下一个要调用的工具
2. 如果任务已完成，返回AIResponse，response_type="direct_reply"，包含最终结果

注意：每次只能调用一个工具，根据工具结果再决定下一步。

回复:"""

        # 获取AI响应
        ai_response = LLMChat(prompt, "分析当前情况并决定下一步", AIResponse)

        # 检查响应类型
        if isinstance(ai_response, AIResponse) and ai_response.is_tool_call():
            # 调用单个工具
            tool_call = ai_response.tool_call
            try:
                tool_result = registry.call_tool(tool_call.name, **tool_call.parameters)
                context += f"步骤{iteration+1}: 调用 {tool_call.name}({tool_call.parameters}) -> {tool_result}\n"

                # 继续下一轮
                continue

            except Exception as e:
                context += f"步骤{iteration+1}: 调用 {tool_call.name} 失败: {e}\n"
                continue

        elif isinstance(ai_response, AIResponse) and ai_response.message:
            # 任务完成，返回最终结果
            final_result = ai_response.message

            # 转换为目标类型
            if return_type == str:
                return final_result
            else:
                return LLMChat(final_result, f"转换为{return_type.__name__ if hasattr(return_type, '__name__') else str(return_type)}", return_type)
        else:
            # 异常情况
            context += f"步骤{iteration+1}: AI响应异常: {ai_response}\n"
            continue

    # 达到最大轮次，强制结束
    final_prompt = f"""基于以下执行过程，给出最终结果：

{context}

用户原始要求: {question}
要求返回类型: {return_type.__name__ if hasattr(return_type, '__name__') else str(return_type)}

请总结执行结果并给出最终答案:"""

    return LLMChat(final_prompt, "总结最终结果", return_type)