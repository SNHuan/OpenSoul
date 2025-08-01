# 🤖 LLMCode - 通用AI工具系统

一个极简优雅的LLM工具系统，让AI能够自动调用工具完成复杂任务。

## ✨ 核心特性

### 🎯 **通用类型系统**
- **任意输入 → 任意输出**：支持从`str`到复杂嵌套对象的所有类型
- **自动类型推断**：基于Pydantic模型自动生成完美示例
- **智能解析**：自动将LLM输出解析为目标类型

### 🔧 **自动工具注册**
- **装饰器注册**：使用`@ai_tool`装饰器一键注册工具
- **自动发现**：导入`tools`包自动注册所有工具
- **类型安全**：自动解析函数签名和参数类型

### 🔄 **递归式工具调用**
- **智能链式调用**：AI自动决定工具调用顺序
- **上下文感知**：每次调用都基于前一步的结果
- **错误恢复**：工具调用失败时自动重试或调整策略

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基础用法

#### 1. 简单LLM调用

```python
from llm.chat import LLMChat

# 基础类型
result = LLMChat("苹果、香蕉、橙子", "提取水果名称", list)
print(result)  # ['苹果', '香蕉', '橙子']

# 复杂类型
from pydantic import BaseModel
from typing import List

class Person(BaseModel):
    name: str
    age: int
    skills: List[str]

result = LLMChat("张三28岁，会Python和Java", "提取人员信息", Person)
print(result.name)  # 张三
print(result.skills)  # ['Python', 'Java']
```

#### 2. 工具定义

```python
from tools.base import ai_tool

@ai_tool(description="获取当前时间")
def get_current_time() -> str:
    """获取当前时间"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@ai_tool(description="计算两个数的和")
def add_numbers(a: int, b: int) -> int:
    """计算两个数的和"""
    return a + b
```

#### 3. 带工具的AI调用

```python
from llm.toolchat import ToolChat

# 简单工具调用
result = ToolChat("", "现在几点了", str)
print(result)  # "现在是2025-08-01 15:30:25"

# 复杂任务（自动链式调用多个工具）
result = ToolChat(
    "我需要知道当前时间，然后创建一个文件记录这个时间", 
    "完成这个任务", 
    str
)
print(result)  # "已完成任务：获取了当前时间并创建了time_record.txt文件"
```

## 📁 项目结构

```
LLMCode/
├── llm/                    # LLM核心模块
│   ├── chat.py            # 通用LLM接口
│   └── toolchat.py        # 带工具的LLM接口
├── tools/                 # 工具系统
│   ├── __init__.py        # 自动工具注册
│   ├── base.py            # 工具注册中心
│   └── test.py            # 示例工具
├── test/                  # 测试脚本
│   └── test_ai_tools.py   # 工具系统测试
└── requirements.txt       # 依赖列表
```

## 🔧 API 参考

### LLMChat

```python
def LLMChat(data: Any, question: str, return_type: Any = str) -> Any:
    """
    通用LLM接口
    
    Args:
        data: 输入数据
        question: 处理要求
        return_type: 返回类型
    
    Returns:
        指定类型的结果
    """
```

### ToolChat

```python
def ToolChat(data: Any, question: str, return_type: Any = str, max_iterations: int = 5) -> Any:
    """
    带工具的LLM接口
    
    Args:
        data: 输入数据
        question: 处理要求
        return_type: 返回类型
        max_iterations: 最大工具调用轮次
    
    Returns:
        指定类型的结果
    """
```

### 工具装饰器

```python
@ai_tool(name: str = None, description: str = None)
def your_function(param1: type1, param2: type2) -> return_type:
    """工具函数"""
    pass
```

## 🎯 支持的类型

### 基础类型
- `str` - 字符串
- `int` - 整数  
- `float` - 浮点数
- `bool` - 布尔值
- `list` - 列表
- `dict` - 字典

### 泛型类型
- `List[str]` - 字符串列表
- `Dict[str, int]` - 字符串到整数的字典
- `Optional[str]` - 可选字符串

### 复杂类型
- **Pydantic模型** - 自动解析嵌套对象
- **自定义类** - 基于类型注解自动推断

## 🔄 工具调用流程

1. **分析任务** - AI分析用户需求，判断是否需要工具
2. **选择工具** - 基于可用工具列表选择合适的工具
3. **执行工具** - 调用工具并获取结果
4. **更新上下文** - 将工具结果加入对话上下文
5. **决定下一步** - 基于结果决定是否需要调用更多工具
6. **返回结果** - 完成任务后返回最终结果

## 🧪 测试

运行测试脚本：

```bash
python test/test_ai_tools.py
```

## ⚙️ 配置

### 环境变量

```bash
# OpenAI配置
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=your_base_url
OPENAI_MODEL_ID=gpt-3.5-turbo
OPENAI_LLM_TEMPERATURE=0.1

# 调试模式
DEBUG=true
```

## 🎨 设计理念

### 通用性优先
- **一套接口处理所有类型**：从简单字符串到复杂嵌套对象
- **统一的抽象层**：LLMChat和ToolChat使用相同的接口

### 简洁优雅
- **装饰器模式**：一行代码注册工具
- **自动发现**：无需手动导入工具模块
- **类型推断**：自动生成示例和描述

### 智能化
- **递归式调用**：AI自主决定工具调用策略
- **上下文感知**：每步都基于前一步的结果
- **错误恢复**：自动处理工具调用失败

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License
