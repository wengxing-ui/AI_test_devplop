# core/test_case_generator.py

# Allow running `python core/test_case_generator.py` directly.
# When executed as a script, the project root might not be on `sys.path`.
import os
import sys

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.model_generator import ModelGenerator
from core.swagger_parser import SwaggerParser
from core.config import config

class TestCaseGenerator:

    def __init__(self, swagger_file_path: str):
        self.model_generator = ModelGenerator(swagger_file_path)
        self.swagger_parser = SwaggerParser(swagger_file_path)

    def generate_test_cases(self, path: str, method: str) -> str: # 生成正常用例
        """
        根据 Swagger 接口生成 pytest 测试用例
        """
        import json

        method_lower = method.lower()

        op = self.swagger_parser.swagger_data["paths"][path][method]
        path_vars = set()
        for p in op.get("parameters", []) or []:
            if p.get("in") == "path" and p.get("name"):
                path_vars.add(p["name"])

        def test_name(p: str) -> str:
            return p.replace("/", "_").replace("{", "").replace("}", "")

        def default_value_code(
            prop_name: str,
            prop_schema: dict,
            var_names: set[str],
            use_unique_payload: bool,
        ) -> str:
            # 需要的 path 参数：直接引用变量（如 user_id）
            if prop_name in var_names:
                return prop_name

            # 针对当前项目的已知字段做一些更像真实数据的默认值
            if prop_name == "username":
                if use_unique_payload:
                    return 'f"test1_{unique}"'
                return json.dumps("test1", ensure_ascii=True)
            if prop_name == "password":
                return json.dumps("123456", ensure_ascii=True)
            if prop_name == "email":
                if use_unique_payload:
                    return 'f"test{unique}@test.com"'
                return json.dumps("test@test.com", ensure_ascii=True)

            # anyOf 里可能带 null：取第一个非 null 的 type
            prop_type = prop_schema.get("type")
            if not prop_type and isinstance(prop_schema.get("anyOf"), list):
                for opt in prop_schema["anyOf"]:
                    t = opt.get("type")
                    if t and t != "null":
                        prop_type = t
                        break

            if prop_type == "integer":
                return "1"
            if prop_type == "boolean":
                return "True"
            if prop_type == "array":
                return "[]"
            if prop_type == "object":
                return "{}"
            return json.dumps("test", ensure_ascii=True)

        def build_payload_literal(
            request_schema: dict,
            var_names: set[str],
            use_unique_payload: bool,
        ) -> str:  # 构建请求体字面量
            if not request_schema:
                return "{}"

            properties = request_schema.get("properties", {}) or {}
            required = request_schema.get("required", []) or []

            include_names = set(required)
            include_names.update([n for n in ["username", "password", "email"] if n in properties])
            include_names.update([n for n in var_names if n in properties])

            parts: list[str] = []
            for name, prop_schema in properties.items():
                if name not in include_names:
                    continue
                value_code = default_value_code(name, prop_schema or {}, var_names, use_unique_payload)
                parts.append(f"\"{name}\": {value_code}")
            return "{ " + ", ".join(parts) + " }"

        # requestBody schema（已支持 $ref 解析）
        request_schema = self.swagger_parser.get_request_schema(path, method)

        vars_for_payload = set(path_vars)
        request_required = request_schema.get("required", []) if isinstance(request_schema, dict) else []
        request_properties = request_schema.get("properties", {}) if isinstance(request_schema, dict) else {}

        needs_user_id_from_register = ("user_id" in request_required) or ("user_id" in (request_properties or {}))
        if needs_user_id_from_register:
            vars_for_payload.add("user_id")

        payload_literal_uses_unique = (path == "/user/register" and method_lower == "post")
        payload_literal = build_payload_literal(request_schema, vars_for_payload, payload_literal_uses_unique)

        # 对于需要 user_id 的接口：先注册拿到 user_id，避免 user_id 未定义/用户不存在
        needs_register = (
            (len(path_vars) > 0 or (method_lower == "put" and needs_user_id_from_register))
            and not (path == "/user/register" and method_lower == "post")
        )

        register_payload_literal = build_payload_literal(
            self.swagger_parser.get_request_schema("/user/register", "post"),
            set(),
            True,
        )

        register_block = ""
        user_assign_block = ""
        if needs_register:
            register_block = f"""
    register_url = f"{{base_url}}/user/register"
    register_payload = {register_payload_literal}
    register_res = requests.post(register_url, json=register_payload)
    assert register_res.status_code == 200
    assert register_res.json()["code"] == 0
"""
            # swagger 当前仅有 user_id 这一类用户标识
            if "user_id" in vars_for_payload:
                user_assign_block = '    user_id = register_res.json()["data"]["user_id"]\n'

        payload_block = ""
        call_block = ""
        if method_lower in ("post", "put"):
            payload_block = f"""
    payload = {payload_literal}
"""
            call_block = f"    res = requests.{method_lower}(url, json=payload)\n"
        else:
            call_block = f"    res = requests.{method_lower}(url)\n"

        unique_needed = payload_literal_uses_unique or needs_register
        unique_block = '    unique = str(int(time.time() * 1000))\n' if unique_needed else ""
        time_import = "import time\n" if unique_needed else ""

        test_case_code = f"""
import requests
import pytest
{time_import}from models.user_model import RegisterResponse

def test_{test_name(path)}(base_url):
{unique_block}{register_block}{user_assign_block}    url = f"{{base_url}}{path}"
{payload_block}{call_block}
    assert res.status_code == 200
    assert res.json()["code"] == 0
"""

        return test_case_code

    def _test_name_for_path(self, p: str) -> str:
        return p.replace("/", "_").replace("{", "").replace("}", "")

    def _build_api_info_for_ai(self, path: str, method: str) -> dict:
        op = self.swagger_parser.swagger_data["paths"][path][method]

        path_vars: list[str] = []
        for p in op.get("parameters", []) or []:
            if p.get("in") == "path" and p.get("name"):
                path_vars.append(p["name"])

        request_schema = self.swagger_parser.get_request_schema(path, method) or {}
        request_required = request_schema.get("required", []) if isinstance(request_schema, dict) else []
        request_properties = request_schema.get("properties", {}) if isinstance(request_schema, dict) else {}

        responses = op.get("responses", {}) or {}
        response_status_hints: list[int] = []
        for k in responses.keys():
            try:
                response_status_hints.append(int(k))
            except Exception:
                pass

        return {
            "path": path,
            "method": method,
            "path_vars": path_vars,
            "request_required": request_required,
            "request_properties": request_properties,
            "response_status_hints": response_status_hints,
            "endpoint_notes": op.get("summary") or "",
        }

    def generate_test_cases_with_ai_exceptions(
        self, path: str, method: str, test_file_path: str
    ) -> None:
        """
        生成正常用例并写入文件；若开启开关，则追加 AI 异常场景用例。

        说明：此方法负责“正常用例写入 + 异常用例追加”，以确保不会被 run.py 的覆盖逻辑破坏。
        """

        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

        test_fn_name = f"test_{self._test_name_for_path(path)}"
        test_case_code = self.generate_test_cases(path, method)

        existing_code = ""
        if os.path.exists(test_file_path):
            with open(test_file_path, "r", encoding="utf-8") as f:
                existing_code = f.read()

        # 写入正常用例（只在函数不存在时追加）
        if f"def {test_fn_name}(" not in existing_code:
            with open(test_file_path, "a", encoding="utf-8") as f:
                if existing_code and not existing_code.endswith("\n"):
                    f.write("\n")
                f.write(test_case_code)

        # 追加异常用例
        if not config.ENABLE_AI_EXCEPTIONS:
            return

        from core.ai_exception_generator import inject_exception_tests

        api_info = self._build_api_info_for_ai(path, method)
        inject_exception_tests(api_info, test_file_path)

if __name__ == "__main__":
    swagger_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "swagger.json"))
    generator = TestCaseGenerator(swagger_path)