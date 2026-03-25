# run.py

import os
import pytest
from core.swagger_parser import SwaggerParser
from core.model_generator import ModelGenerator
from core.test_case_generator import TestCaseGenerator

def generate_test_cases(swagger_file_path: str):
    """
    生成 pytest 测试用例
    """
    # 初始化解析器和生成器
    test_case_generator = TestCaseGenerator(swagger_file_path)

    # 解析 swagger 文件，获取所有接口路径和方法
    parser = SwaggerParser(swagger_file_path)
    paths = parser.get_paths()

    # 遍历每个接口路径和方法，生成对应的 pytest 测试用例
    for path, methods in paths.items():
        for method, details in methods.items():
            print(f"Generating {method.upper()} test case, path: {path}")
            test_case_code = test_case_generator.generate_test_cases(path, method)

            # 保存生成的测试用例文件
            file_name = f'testcases/test_{path.replace("/", "_").replace("{", "").replace("}", "")}.py'
            os.makedirs(os.path.dirname(file_name), exist_ok=True)

            with open(file_name, 'w') as f:
                f.write(test_case_code)

            print(f"Testcases generated: {file_name}")

def run_tests():
    """
    运行 pytest 测试
    """
    # 执行所有测试用例
    print("Running pytest test cases...")
    result = pytest.main(["testcases/"])
    return result

def main():
    """
    主函数，执行 Swagger 解析、用例生成、pytest 执行
    """
    swagger_file_path = './swagger.json'  # Swagger 文件路径

    # 1. 生成测试用例
    generate_test_cases(swagger_file_path)

    # 2. 运行测试用例
    result = run_tests()

    if result == 0:
        print("All tests passed")
    else:
        print("Some tests failed")

if __name__ == '__main__':
    main()