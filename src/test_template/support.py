"""Small case records and positive assertions shared across test layers."""

import ast
import json
import tomllib
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

TEMPLATE_ROOT = Path(__file__).parents[2]


@dataclass(frozen=True)
class ModuleCase:
    inputs: dict[str, Any] = field(default_factory=dict)
    answers: dict[str, Any] = field(default_factory=dict)
    expected: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VariableCase:
    answers: dict[str, Any] = field(default_factory=dict)
    expected: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RenderCase:
    context: dict[str, Any] = field(default_factory=dict)
    contains: tuple[str, ...] = ()
    parse: Callable[[str], Any] | None = None
    expected: Any = None
    macro: str | None = None


@dataclass(frozen=True)
class TemplateCase:
    answers: dict[str, str]
    expected: dict[str, tuple[str, ...]]


ModuleCheck = Callable[[str, ModuleCase], None]
VariablesCheck = Callable[[VariableCase], None]
TemplateCheck = Callable[[str, RenderCase], None]


def assert_expected(actual: Any, expected: Any) -> None:
    """Check selected mapping fields and list members, or an exact scalar value."""
    if isinstance(expected, dict):
        assert isinstance(actual, dict), f'Expected a mapping, got {actual!r}'
        for key, value in expected.items():
            assert key in actual, f'Missing key: {key}'
            assert_expected(actual[key], value)
    elif isinstance(expected, list):
        assert isinstance(actual, list), f'Expected a list, got {actual!r}'
        if not expected:
            assert not actual, f'Expected an empty list, got {actual!r}'
        for value in expected:
            assert value in actual, f'Missing list member: {value!r}'
    else:
        assert actual == expected, f'Expected {expected!r}, got {actual!r}'


def module_context(module: str, **variables: Any) -> dict[str, Any]:
    """Supply explicit module variables and empty extension points for a render."""
    return {
        module: {'vars': variables, 'files': []},
        'contributions': [],
        'module_paths': {path.name: f'modules/{path.name}' for path in (TEMPLATE_ROOT / 'modules').iterdir() if path.is_dir()},
    }


def json_members(source: str) -> Any:
    """Parse a fragment containing JSON object members."""
    return json.loads('{' + source + '}')


def json_items(source: str) -> Any:
    """Parse a fragment containing JSON array items."""
    return json.loads('[' + source + ']')


def toml_items(source: str) -> Any:
    """Parse a fragment containing TOML array items."""
    return tomllib.loads('items = [' + source + ']')['items']


def python_assignments(source: str) -> dict[str, Any]:
    """Parse Python syntax and return its literal top-level assignments."""
    result = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign):
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                continue
            for target in node.targets:
                if isinstance(target, ast.Name):
                    result[target.id] = value
    return result
