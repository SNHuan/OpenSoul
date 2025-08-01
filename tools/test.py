from tools.base import ai_tool

# 示例工具定义
@ai_tool(description="获取当前时间")
def get_current_time() -> str:
    """获取当前时间"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@ai_tool(description="计算两个数的和")
def add_numbers(a: int, b: int) -> int:
    """计算两个数的和"""
    return a + b


@ai_tool(description="搜索文件内容")
def search_file(filename: str, keyword: str) -> str:
    """在文件中搜索关键词"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            if keyword in content:
                lines = content.split('\n')
                results = [f"第{i+1}行: {line}" for i, line in enumerate(lines) if keyword in line]
                return f"找到 {len(results)} 个匹配:\n" + "\n".join(results[:5])
            else:
                return f"在 {filename} 中未找到 '{keyword}'"
    except Exception as e:
        return f"搜索失败: {e}"


@ai_tool(description="创建文件")
def create_file(filename: str, content: str) -> str:
    """创建文件并写入内容"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"文件 {filename} 创建成功"
    except Exception as e:
        return f"文件创建失败: {e}"