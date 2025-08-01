"""
最通用的LLM类型系统 - 一切皆可描述，一切皆可示例
核心思想：任何类型都可以用"自然语言描述+完美示例"来表达
"""
import os
import json
import re
from typing import Any, get_origin, get_args
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

load_dotenv()


def LLMChat(data: Any, question: str, return_type: Any = str) -> Any:
    """
    最通用的LLM接口 - 一个函数处理任意类型
    
    核心原理：
    1. 将任何类型转换为自然语言描述
    2. 生成该类型的完美示例
    3. 用统一的万能提示词
    4. 用统一的万能解析器
    """
    try:
        # 1. 通用类型描述器
        description = describe_type(return_type)
        example = generate_example(return_type)
        
        # 2. 万能提示词 - 真正通用版本
        prompt = f"""从输入中提取信息并转换为JSON格式。

输入: {str(data)}
任务: {question}

输出类型: {description}
输出格式:
{json.dumps(example, ensure_ascii=False, indent=2)}

重要: 严格按照上述格式返回，所有嵌套对象都必须保持完整的对象结构。

输出:"""
        
        # 3. LLM调用
        llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL_ID", "gpt-3.5-turbo"),
            temperature=float(os.getenv("OPENAI_LLM_TEMPERATURE", 0.1)),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_BASE_URL")
        )
        response = llm.invoke([HumanMessage(content=prompt)])

        if os.getenv("DEBUG", "false").lower() == "true":
            print(f"响应:\n{response.content}")
        
        # 4. 万能解析器
        return parse_to_type(response.content.strip(), return_type)
        
    except Exception as e:
        print(f"LLMChat错误: {e}")
        return get_default_value(return_type)


def describe_type(t: Any) -> str:
    """将任意类型转换为自然语言描述"""
    # 基础类型
    if t == str or t == "string":
        return "字符串文本"
    elif t == int or t == "number":
        return "整数数字"
    elif t == float:
        return "浮点数字"
    elif t == bool or t == "boolean":
        return "布尔值(true/false)"
    elif t == list or t == "list":
        return "数组列表"
    elif t == dict or t == "json":
        return "JSON对象"
    
    # 泛型类型
    origin = get_origin(t)
    if origin is list:
        args = get_args(t)
        if args:
            element_desc = describe_type(args[0])
            return f"包含{element_desc}的数组"
        return "数组列表"
    elif origin is dict:
        return "字典对象"
    
    # Pydantic模型
    if hasattr(t, 'model_fields'):
        fields = []
        for name, field in t.model_fields.items():
            field_desc = describe_type(field.annotation)
            desc = getattr(field, 'description', '')
            if desc:
                fields.append(f"{name}({field_desc}, {desc})")
            else:
                fields.append(f"{name}({field_desc})")
        
        class_name = t.__name__
        return f"{class_name}对象，包含字段: {', '.join(fields)}"
    
    # 普通类
    if hasattr(t, '__name__'):
        return f"{t.__name__}类型的对象"
    
    return "未知类型"


def generate_example(t: Any) -> Any:
    """为任意类型生成完美示例"""
    # 基础类型
    if t == str or t == "string":
        return "示例文本"
    elif t == int or t == "number":
        return 123
    elif t == float:
        return 123.45
    elif t == bool or t == "boolean":
        return True
    elif t == list or t == "list":
        return ["项目1", "项目2"]
    elif t == dict or t == "json":
        return {"键": "值"}
    
    # 泛型类型
    origin = get_origin(t)
    if origin is list:
        args = get_args(t)
        if args:
            element_example = generate_example(args[0])
            return [element_example]
        return ["示例项目"]
    elif origin is dict:
        return {"键": "值"}
    
    # Pydantic模型 - 使用JSON Schema
    if hasattr(t, 'model_json_schema'):
        try:
            schema = t.model_json_schema()
            return schema_to_example(schema)
        except:
            pass
    
    # 普通类 - 通过字段推断
    if hasattr(t, '__annotations__'):
        example = {}
        for field, field_type in t.__annotations__.items():
            example[field] = generate_example(field_type)
        return example
    
    return "示例值"


def schema_to_example(schema: dict, definitions: dict = None) -> Any:
    """从JSON Schema生成示例 - 支持引用解析"""
    if definitions is None:
        definitions = schema.get('$defs', {})
    
    # 处理引用
    if '$ref' in schema:
        ref_path = schema['$ref']
        if ref_path.startswith('#/$defs/'):
            ref_name = ref_path.split('/')[-1]
            if ref_name in definitions:
                return schema_to_example(definitions[ref_name], definitions)
        return "引用对象"
    
    schema_type = schema.get('type')
    
    if schema_type == 'object':
        example = {}
        properties = schema.get('properties', {})
        for prop_name, prop_schema in properties.items():
            example[prop_name] = schema_to_example(prop_schema, definitions)
        return example
    
    elif schema_type == 'array':
        items_schema = schema.get('items', {})
        return [schema_to_example(items_schema, definitions)]
    
    elif schema_type == 'string':
        return "示例文本"
    elif schema_type == 'integer':
        return 123
    elif schema_type == 'number':
        return 123.45
    elif schema_type == 'boolean':
        return True
    else:
        return "示例值"


def parse_to_type(result: str, target_type: Any) -> Any:
    """万能解析器 - 将字符串解析为任意类型"""
    # 基础类型解析
    if target_type == str or target_type == "string":
        return result
    
    elif target_type == bool or target_type == "boolean":
        return any(word in result.lower() for word in ["true", "是", "正确", "对", "yes", "1"])
    
    elif target_type == int or target_type == "number":
        numbers = re.findall(r'-?\d+', result)
        return int(numbers[0]) if numbers else 0
    
    elif target_type == float:
        numbers = re.findall(r'-?\d+\.?\d*', result)
        return float(numbers[0]) if numbers else 0.0
    
    elif target_type == list or target_type == "list":
        return parse_list(result)
    
    elif target_type == dict or target_type == "json":
        return parse_json(result)
    
    # 复杂类型解析
    try:
        data = json.loads(result)
        return create_typed_object(data, target_type)
    except:
        return result


def parse_list(text: str) -> list:
    """解析列表"""
    try:
        if text.strip().startswith('['):
            return json.loads(text)
        # 按逗号分割
        return [item.strip() for item in text.split(',') if item.strip()]
    except:
        return [text]


def parse_json(text: str) -> dict:
    """解析JSON"""
    try:
        return json.loads(text)
    except:
        return {}


def create_typed_object(data: Any, target_type: Any) -> Any:
    """创建指定类型的对象"""
    # 处理泛型类型
    origin = get_origin(target_type)
    if origin is list:
        if isinstance(data, list):
            args = get_args(target_type)
            if args:
                element_type = args[0]
                return [create_typed_object(item, element_type) for item in data]
        return data
    
    # 处理Pydantic模型
    if hasattr(target_type, 'model_validate'):
        try:
            return target_type.model_validate(data)
        except Exception as e:
            print(f"Pydantic验证失败: {e}")
            return data
    
    # 处理普通类
    if hasattr(target_type, '__init__') and isinstance(data, dict):
        try:
            return target_type(**data)
        except Exception as e:
            print(f"对象创建失败: {e}")
            return data
    
    return data


def get_default_value(target_type: Any) -> Any:
    """获取类型的默认值"""
    if target_type == str:
        return ""
    elif target_type == int or target_type == float:
        return 0
    elif target_type == bool:
        return False
    elif target_type == list:
        return []
    elif target_type == dict:
        return {}
    else:
        return None
