# core/swagger_parser.py

import json
from typing import Any, Dict


class SwaggerParser:
    def __init__(self, swagger_file_path: str):
        with open(swagger_file_path, "r", encoding="utf-8") as file:
            self.swagger_data = json.load(file)

    def _resolve_ref(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """解析 Swagger 的 $ref 到 components/schemas 里的真实 schema。"""
        if not schema or not isinstance(schema, dict):
            return schema
        ref = schema.get("$ref")
        if not ref or not isinstance(ref, str):
            return schema
        if ref.startswith("#/components/schemas/"):
            name = ref.split("/")[-1]
            return (
                self.swagger_data.get("components", {})
                .get("schemas", {})
                .get(name, {})
            )
        return schema

    def get_paths(self) -> Dict[str, Any]:
        """获取 Swagger 的 endpoints：路径 -> 方法 -> 详情"""
        return self.swagger_data.get("paths", {})

    def get_request_schema(self, path: str, method: str) -> Dict[str, Any]:
        """获取 requestBody/application/json 的 schema"""
        schema = (
            self.swagger_data["paths"][path][method]
            .get("requestBody", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema", {})
        )
        return self._resolve_ref(schema)

    def get_response_schema(self, path: str, method: str) -> Dict[str, Any]:
        """获取 responses/200/application/json 的 schema"""
        schema = (
            self.swagger_data["paths"][path][method]
            .get("responses", {})
            .get("200", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema", {})
        )
        return self._resolve_ref(schema)