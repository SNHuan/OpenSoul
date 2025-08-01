"""
工具模块初始化 - 自动注册所有工具
"""

# 导入base模块，确保注册表可用
from .base import registry, ai_tool

# 自动导入所有工具模块，触发装饰器注册
import os
import importlib

# 获取当前目录下的所有.py文件
current_dir = os.path.dirname(__file__)
for filename in os.listdir(current_dir):
    if filename.endswith('.py') and filename not in ['__init__.py', 'base.py']:
        module_name = filename[:-3]  # 去掉.py后缀
        try:
            # 动态导入模块
            importlib.import_module(f'tools.{module_name}')
            print(f"✅ 自动注册工具模块: tools.{module_name}")
        except Exception as e:
            print(f"❌ 注册工具模块失败 {module_name}: {e}")

print(f"🎉 工具自动注册完成，共注册 {len(registry.tools)} 个工具")
