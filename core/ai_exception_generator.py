import json
import os
import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from core.config import config


class ExceptionScenario(BaseModel):
    """
    LLM 产出的“异常测试场景”。

    注意：对通用 swagger 来说，HTTP 层面通常可通过 `expected_http_status` 断言；
    业务层 `expected_business_code` 在某些框架（如 FastAPI 默认 422）可能不存在，因此允许为 None。
    """

    scenario_key: str = Field(
        description="稳定唯一键，用于去重（同一 swagger 重跑不应重复生成）。"
    )
    description: str = Field(description="场景描述，用于测试可读性。")
    http_status: int = Field(description="期望 HTTP 状态码。")
    expected_business_code: Optional[int] = Field(
        default=None, description="期望业务 code；如响应体不包含 code，可为 null。"
    )

    # path 参数：用于填充 URL 中的 {xxx} 变量（按字段名对齐）。
    path_params: Dict[str, Any] = Field(
        default_factory=dict, description="path 变量取值（可能是非法类型/值）。"
    )

    # 请求体：仅适用于 post/put/patch；可包含缺失字段/非法类型/超长/非法枚举等。
    request_json: Optional[Dict[str, Any]] = Field(
        default=None,
        description="请求 JSON body（可故意缺少 required 字段或填入非法值）。",
    )


class ExceptionScenarioList(BaseModel):
    scenarios: List[ExceptionScenario]


def _sanitize_identifier(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[^0-9a-zA-Z_]+", "_", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_")


def _api_test_base_name(api_info: Dict[str, Any]) -> str:
    # 去掉 f-string 占位符里的 { }，用于构造 python 函数名。
    path = api_info.get("path", "")
    path_name = path.replace("/", "_").replace("{", "").replace("}", "")
    method = (api_info.get("method", "") or "").lower()
    return f"{path_name}__{method}" if method else path_name


def _exception_test_func_name(scenario: ExceptionScenario, api_info: Dict[str, Any]) -> str:
    base = _api_test_base_name(api_info)
    return f"test_{base}__ai_exc_{_sanitize_identifier(scenario.scenario_key)}"


def _build_api_prompt_payload(api_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    提供给 LLM 的最小化结构化信息，避免直接把整份 swagger dump 贴进去。
    """

    # 避免把不可序列化对象传给 prompt。
    payload: Dict[str, Any] = {
        "path": api_info.get("path"),
        "method": api_info.get("method"),
        "path_vars": api_info.get("path_vars", []),
        "request_required": api_info.get("request_required", []),
        "request_properties": api_info.get("request_properties", {}),
        "response_status_hints": api_info.get("response_status_hints", []),
        "endpoint_notes": api_info.get("endpoint_notes", ""),
    }
    return payload


def generate_exception_scenarios(api_info: Dict[str, Any]) -> ExceptionScenarioList:
    """
    调用 LangChain（deepseek）生成异常场景列表。
    """

    from langchain_openai import ChatOpenAI
    from langchain_core.output_parsers import PydanticOutputParser
    from langchain_core.prompts import ChatPromptTemplate

    if not config.deepseek_API_KEY:
        # 开关开启但缺少 key：不应阻断主流程生成正常用例。
        return ExceptionScenarioList(scenarios=[])

    parser = PydanticOutputParser(pydantic_object=ExceptionScenarioList)

    api_payload = _build_api_prompt_payload(api_info)
    format_instructions = parser.get_format_instructions()

    system = (
        "你是一个接口测试工程师专家。你的任务是：针对给定的 OpenAPI/Swagger 接口，"
        "生成可复现的异常测试场景。输出必须严格符合给定 Pydantic JSON Schema。"
    )
    human_base = (
        "请生成 5-8 个异常场景，覆盖但不限于：\n"
        "1) 缺失必填字段（missing required）\n"
        "2) 类型错误（type error，如整数传字符串、数组传对象等）\n"
        "3) 超长（超长字符串/数组长度）\n"
        "4) 非法枚举（invalid enum；如果 schema 没有 enum，就跳过该类）\n"
        "5) 业务异常（如 user_id 不存在等；如果 schema 未提供业务约束，使用通用做法：用大数/负数触发“资源不存在”类错误）\n\n"
        "要求：\n"
        "- 根据 method 判断是否应该构造 request_json。\n"
        "- 对于 422 这类校验失败，后端响应可能不包含业务 code。此时请将 expected_business_code 设置为 null。\n"
        "- 给每个场景提供稳定的 scenario_key（同一接口重复生成不应重复）。\n\n"
        "强制约束（避免输出非法 JSON）：\n"
        "- request_json 必须是严格的 JSON 字面量对象，只包含字符串/数字/布尔/null/数组/对象；\n"
        "- 不允许出现任何编程表达式，例如不要写 'a'.repeat(1000)、len(...)、'a' * 1000 之类；\n"
        "- 如果需要超长，请在 JSON 里直接给出最终的超长字符串内容（例如长度约 1000 的字符串），不要用 repeat 表达式。\n\n"
        "接口信息（JSON）：\n"
        "{api_payload}\n\n"
        "{format_instructions}"
    )

    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human_base)])

    # DeepSeek OpenAI-compatible 接口。
    llm = ChatOpenAI(
        api_key=config.deepseek_API_KEY,
        base_url="https://api.deepseek.com/v1",
        model=config.AI_MODEL,
        temperature=0.2,
    )

    chain = prompt | llm | parser
    invoke_payload = {
        "api_payload": json.dumps(api_payload, ensure_ascii=False),
        "format_instructions": format_instructions,
    }

    # 解析失败时做一次重试（LLM 偶发输出非法 JSON/表达式）。
    from langchain_core.exceptions import OutputParserException

    for attempt in range(2):
        try:
            result = chain.invoke(invoke_payload)
            if isinstance(result, ExceptionScenarioList):
                return result
        except OutputParserException:
            if attempt == 1:
                return ExceptionScenarioList(scenarios=[])

            # 更严格的重试提示：仅允许“纯 JSON 数据”，不允许任何表达式。
            stricter_system = system + " 你必须只输出严格符合 JSON Schema 的纯 JSON，不要输出任何表达式/代码。"
            retry_prompt = ChatPromptTemplate.from_messages(
                [("system", stricter_system), ("human", human_base)]
            )
            chain = retry_prompt | llm | parser

    return ExceptionScenarioList(scenarios=[])


def _python_literal(v: Any) -> str:
    # 使用 repr 来得到 Python 可读的字面量（对 bool/None 会映射成 True/False/None）。
    return repr(v)


def render_exception_test(scenario: ExceptionScenario, api_info: Dict[str, Any]) -> str:
    """
    将场景转换为 pytest 测试函数代码。
    """

    test_fn_name = _exception_test_func_name(scenario, api_info)
    method_lower = (api_info.get("method") or "").lower()
    path = api_info.get("path") or ""

    path_vars = api_info.get("path_vars", []) or []
    payload_vars_needed = method_lower in ("post", "put", "patch")

    # URL 中的 f-string 占位符变量必须先定义。
    path_assign_lines: List[str] = []
    for var_name in path_vars:
        if var_name in (scenario.path_params or {}):
            path_assign_lines.append(f"    {var_name} = {_python_literal(scenario.path_params[var_name])}")
        else:
            # 没指定则用一个“看似合法”的默认值（整数默认 1）。
            path_assign_lines.append(f"    {var_name} = 1")
    path_assign_block = "\n".join(path_assign_lines)

    # 请求体（仅 post/put/patch）。
    payload_block = ""
    if payload_vars_needed:
        # request_json 可能故意缺失 required 字段（这就是异常测试）。
        payload_json = scenario.request_json if scenario.request_json is not None else {}
        payload_block = f"    payload = {_python_literal(payload_json)}\n"

    # 发送请求。
    if payload_vars_needed:
        call_line = f"    res = requests.{method_lower}(url, json=payload)"
    else:
        call_line = f"    res = requests.{method_lower}(url)"

    # Pydantic 校验（尽量兼容响应里缺少 code 字段的情况）。
    expected_code_block = ""
    if scenario.expected_business_code is not None:
        expected_code_block = (
            f"    if _validated.code is None:\n"
            f"        raise AssertionError('响应缺少 code 字段，无法断言 expected_business_code')\n"
            f"    assert _validated.code == {_python_literal(scenario.expected_business_code)}\n"
        )
    else:
        # 对于 expected_business_code = null 的场景，仅保证响应可被 Pydantic 校验通过。
        expected_code_block = "    # expected_business_code 为 null：不对 code 做精确断言\n"

    return (
        f"def {test_fn_name}(base_url):\n"
        f"    # {scenario.description}\n"
        f"{path_assign_block + chr(10) if path_assign_block else ''}"
        f'    url = f"{{base_url}}{path}"\n'
        f"{payload_block}"
        f"{call_line}\n\n"
        f"    assert res.status_code == {_python_literal(scenario.http_status)}\n"
        f"    from typing import Any\n"
        f"    from pydantic import BaseModel\n"
        f"\n"
        f"    class _ApiResponse(BaseModel):\n"
        f"        code: int | None = None\n"
        f"        msg: str | None = None\n"
        f"        data: Any = None\n"
        f"        detail: Any = None\n"
        f"\n"
        f"    resp_json = res.json()\n"
        f"    _validated = _ApiResponse.model_validate(resp_json)\n"
        f"{expected_code_block}"
    )


def inject_exception_tests(api_info: Dict[str, Any], test_file_path: str) -> None:
    """
    将生成的异常测试代码追加到指定测试文件，避免重复。
    """

    existing_code = ""
    if os.path.exists(test_file_path):
        with open(test_file_path, "r", encoding="utf-8") as f:
            existing_code = f.read()

    # 接口级幂等：如果该接口（path+method）已经生成过 AI 异常测试，
    # 则避免重复追加（LLM 可能会生成新的 scenario_key，导致函数名不同）。
    ai_base = _api_test_base_name(api_info)
    ai_prefix = f"def test_{ai_base}__ai_exc_"
    if ai_prefix in existing_code:
        return

    scenarios = generate_exception_scenarios(api_info)
    if not scenarios.scenarios:
        return

    # 逐个追加，确保单场景解析失败时不影响其它场景。
    appended = False
    with open(test_file_path, "a", encoding="utf-8") as f:
        for scenario in scenarios.scenarios:
            fn_name = _exception_test_func_name(scenario, api_info)
            # 直接字符串包含判断更稳，不依赖复杂正则转义。
            if f"def {fn_name}(" in existing_code:
                continue
            f.write("\n\n")
            f.write(render_exception_test(scenario, api_info))
            appended = True
            existing_code += f"\n\ndef {fn_name}("

    if appended:
        # 保证文件末尾换行更符合格式。
        with open(test_file_path, "a", encoding="utf-8") as f:
            f.write("\n")

