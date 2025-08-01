"""
AI工具系统 - 让任何函数都能变成AI工具
核心思想：装饰器 + 反射 + 自动调用
"""
import inspect
import json
from typing import Any, Dict, List, Callable, get_type_hints, Optional, Union
from functools import wraps
from pydantic import BaseModel, Field
from llm.chat import LLMChat


class ToolCall(BaseModel):
    """工具调用类 - AI返回这个类型来调用工具"""
    name: str = Field(description="要调用的工具名称")  # 改为name，匹配AI输出
    parameters: Dict[str, Any] = Field(default_factory=dict, description="工具参数")

    @property
    def tool_name(self) -> str:
        """兼容属性"""
        return self.name

    def __str__(self):
        return f"调用工具: {self.name}({self.parameters})"


class AIResponse(BaseModel):
    """AI响应类 - 简化版，只支持单个工具调用"""
    response_type: str = Field(description="响应类型: 'tool_call' 或 'direct_reply'")
    tool_call: Optional[ToolCall] = Field(default=None, description="单个工具调用信息")
    message: Optional[str] = Field(default="", description="直接回复消息")

    def model_post_init(self, __context):
        """后处理：清理空字符串"""
        if self.tool_call == "":
            self.tool_call = None
        if self.message == "":
            self.message = None

    def is_tool_call(self) -> bool:
        return self.response_type == "tool_call" and self.tool_call is not None


class AIToolRegistry:
    """AI工具注册中心"""

    def __init__(self):
        self.tools: Dict[str, Dict] = {}
    
    def register(self, func: Callable, name: str = None, description: str = None):
        """注册一个函数为AI工具"""
        tool_name = name or func.__name__
        
        # 自动解析函数签名
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        # 生成工具描述
        tool_info = {
            "function": func,
            "name": tool_name,
            "description": description or func.__doc__ or f"调用{tool_name}函数",
            "parameters": {},
            "required": []
        }
        
        # 解析参数
        for param_name, param in sig.parameters.items():
            param_type = type_hints.get(param_name, str)
            param_desc = self._get_param_description(param_type)
            
            tool_info["parameters"][param_name] = {
                "type": param_desc,
                "description": f"{param_name}参数"
            }
            
            # 判断是否必需参数
            if param.default == param.empty:
                tool_info["required"].append(param_name)
        
        self.tools[tool_name] = tool_info
        return func
    
    def _get_param_description(self, param_type: Any) -> str:
        """将Python类型转换为描述"""
        if param_type == str:
            return "字符串"
        elif param_type == int:
            return "整数"
        elif param_type == float:
            return "浮点数"
        elif param_type == bool:
            return "布尔值"
        elif param_type == list:
            return "列表"
        elif param_type == dict:
            return "字典"
        else:
            return "任意类型"
    
    def get_tools_description(self) -> str:
        """获取所有工具的描述"""
        if not self.tools:
            return "没有可用的工具"
        
        descriptions = []
        for tool_name, tool_info in self.tools.items():
            params = []
            for param_name, param_info in tool_info["parameters"].items():
                required = "必需" if param_name in tool_info["required"] else "可选"
                params.append(f"{param_name}({param_info['type']}, {required})")
            
            param_str = ", ".join(params) if params else "无参数"
            descriptions.append(f"- {tool_name}: {tool_info['description']} | 参数: {param_str}")
        
        return "\n".join(descriptions)
    
    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """调用指定的工具"""
        if tool_name not in self.tools:
            raise ValueError(f"工具 {tool_name} 不存在")
        
        tool_info = self.tools[tool_name]
        func = tool_info["function"]
        
        try:
            return func(**kwargs)
        except Exception as e:
            return f"工具调用失败: {e}"


# 全局工具注册中心
registry = AIToolRegistry()

def get_registry():
    return registry

def ai_tool(name: str = None, description: str = None):
    """装饰器：将函数注册为AI工具"""
    def decorator(func):
        registry.register(func, name, description)
        return func
    return decorator