"""
复杂嵌套类测试 - 验证LLMChat能否返回深度嵌套的类对象
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from llm.chat import LLMChat


# 最底层的类
class Address(BaseModel):
    street: str = Field(description="街道地址")
    city: str = Field(description="城市")
    country: str = Field(default="中国", description="国家")
    zipcode: str = Field(description="邮编")


# 中间层的类
class Contact(BaseModel):
    phone: str = Field(description="电话号码")
    email: str = Field(description="邮箱地址")
    address: Address = Field(description="地址信息")


# 另一个中间层类
class Department(BaseModel):
    name: str = Field(description="部门名称")
    floor: int = Field(description="楼层")
    manager: str = Field(description="部门经理")


# 顶层复杂类
class Employee(BaseModel):
    name: str = Field(description="员工姓名")
    age: int = Field(description="年龄")
    position: str = Field(description="职位")
    salary: float = Field(description="薪资")
    contact: Contact = Field(description="联系方式")
    department: Department = Field(description="所属部门")
    skills: List[str] = Field(description="技能列表")


# 更复杂的嵌套：公司类
class Company(BaseModel):
    name: str = Field(description="公司名称")
    founded_year: int = Field(description="成立年份")
    headquarters: Address = Field(description="总部地址")
    employees: List[Employee] = Field(description="员工列表")
    departments: List[Department] = Field(description="部门列表")


def test_nested_class_level1():
    """测试一层嵌套：Employee包含Contact和Department"""
    print("=== 测试一层嵌套类 Employee ===")

    data = """
    张三，28岁，软件工程师，月薪15000元，
    电话13812345678，邮箱zhang@company.com，
    住址：北京市朝阳区建国路88号，邮编100020，
    所属技术部，在5楼，部门经理是李经理，
    技能包括Python、Java、React
    """

    result = LLMChat(data, "提取员工完整信息", Employee)

    print(f"输入: {data.strip()}")
    print(f"结果: {result}")
    print(f"类型: {type(result)}")

    if isinstance(result, Employee):
        print("✅ 成功返回Employee对象")
        print(f"  姓名: {result.name}")
        print(f"  年龄: {result.age}")
        print(f"  职位: {result.position}")
        print(f"  薪资: {result.salary}")

        # 检查嵌套的Contact对象
        if isinstance(result.contact, Contact):
            print("  ✅ Contact对象正确")
            print(f"    电话: {result.contact.phone}")
            print(f"    邮箱: {result.contact.email}")

            # 检查更深层的Address对象
            if isinstance(result.contact.address, Address):
                print("    ✅ Address对象正确")
                print(f"      地址: {result.contact.address.street}, {result.contact.address.city}")
            else:
                print(f"    ❌ Address对象错误: {type(result.contact.address)}")
        else:
            print(f"  ❌ Contact对象错误: {type(result.contact)}")

        # 检查Department对象
        if isinstance(result.department, Department):
            print("  ✅ Department对象正确")
            print(f"    部门: {result.department.name}")
            print(f"    楼层: {result.department.floor}")
        else:
            print(f"  ❌ Department对象错误: {type(result.department)}")

        return True
    else:
        print("❌ 未能返回Employee对象")
        return False


def test_nested_class_level2():
    """测试二层嵌套：Company包含Employee列表，Employee又包含Contact等"""
    print("\n=== 测试二层嵌套类 Company ===")

    data = """
    科技有限公司成立于2020年，总部位于上海市浦东新区张江路123号，邮编201203。
    公司有技术部和市场部两个部门。
    技术部在3楼，经理是王总；市场部在2楼，经理是刘总。

    员工信息：
    张三，25岁，程序员，月薪12000，电话13811111111，邮箱zhang@tech.com，
    住北京朝阳区，邮编100001，属于技术部，技能Python和Java；

    李四，30岁，市场专员，月薪10000，电话13822222222，邮箱li@market.com，
    住上海浦东，邮编200001，属于市场部，技能营销和策划。
    """

    result = LLMChat(data, "提取公司完整信息包括所有员工和部门", Company)

    print(f"输入: {data.strip()}")
    print(f"结果类型: {type(result)}")
    print(result)


def main():
    """运行所有嵌套类测试"""
    print("🧪 LLMChat 深度嵌套类型测试")
    print("=" * 60)

    test_nested_class_level2()

if __name__ == "__main__":
    main()
