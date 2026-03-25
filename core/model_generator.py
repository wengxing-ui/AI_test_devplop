# core/model_generator.py

# Allow running `python core/model_generator.py` directly.
import os
import sys

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Any, Dict

from core.swagger_parser import SwaggerParser


class ModelGenerator:
    def __init__(self, swagger_file_path: str):
        self.swagger_parser = SwaggerParser(swagger_file_path)

    def generate_model(self, path: str, method: str) -> str:
        """根据 Swagger 的请求/响应 schema 生成 Pydantic 模型代码（字符串）"""
        request_schema = self.swagger_parser.get_request_schema(path, method)
        response_schema = self.swagger_parser.get_response_schema(path, method)

        model_code = self._generate_pydantic_model(request_schema, "Request") + "\n\n"
        model_code += self._generate_pydantic_model(response_schema, "Response")
        return model_code

    def _generate_pydantic_model(self, schema: Dict[str, Any], model_name: str) -> str:
        """生成单个 Pydantic 模型的代码字符串"""
        if not schema:
            return ""

        properties = schema.get("properties", {})
        required_fields = schema.get("required", [])

        model_code = f"class {model_name}(BaseModel):\n"
        for prop, details in properties.items():
            prop_type = details.get("type", "string")
            is_required = prop in required_fields

            # 注意：这里生成的是“代码字符串”，当前测试生成逻辑不会直接执行该字符串
            default_expr = "..." if is_required else "None"
            model_code += (
                f"    {prop}: {self._map_type(prop_type)} = Field({default_expr}, "
                f"description='{details.get('description', '')}')\n"
            )
        return model_code

    def _map_type(self, swagger_type: str) -> str:
        """将 Swagger 类型映射为尽量不依赖额外 imports 的 Python 类型"""
        mapping = {
            "string": "str",
            "integer": "int",
            "boolean": "bool",
            "array": "list",
            "object": "dict",
        }
        return mapping.get(swagger_type, "str")