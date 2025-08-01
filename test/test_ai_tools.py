"""
AI工具系统测试脚本
测试AI智能体的工具调用能力
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import tools 
from tools.base import registry, ai_tool
from typing import List
import json
from llm.toolchat import ToolChat


def main():
    try:
        # 显示可用工具
        print("可用工具:")
        print(registry.get_tools_description())
        print()

        # 测试ToolChat - 与LLMChat相同的接口
        print("=== 测试时间查询 ===")
        result1 = ToolChat("", "现在几点了", str, 3)
        print(f"结果: {result1}")
        print(f"类型: {type(result1)}")
        print()

        # 测试计算
        print("=== 测试计算 ===")
        result2 = ToolChat("", "计算 15 + 27", int, 3)
        print(f"结果: {result2}")
        print(f"类型: {type(result2)}")
        print()

        # 测试复杂任务
        print("=== 测试复杂任务 ===")
        result3 = ToolChat("我需要知道当前时间，然后创建一个文件记录这个时间", "完成这个任务", json, 5)
        print(f"结果: {result3}")
        print()

        print("🎉 所有测试完成！")
        
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
