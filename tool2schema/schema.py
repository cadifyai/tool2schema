import functools
import inspect
import json
import re
from enum import Enum
from inspect import Parameter
from types import ModuleType
from typing import Callable, Optional

from tool2schema.parameter_schema import PARAMETER_SCHEMAS, ParameterSchema


class SchemaType(Enum):
    """Enum for schema types."""

    API = 0
    TUNE = 1


def FindGPTEnabled(module: ModuleType) -> list[Callable]:
    """
    Find all functions with the GPTEnabled decorator.

    :param module: Module to search for GPTEnabled functions
    """
    return [x for x in module.__dict__.values() if hasattr(x, "gpt_enabled")]


def FindGPTEnabledSchemas(
    module: ModuleType, schema_type: SchemaType = SchemaType.API
) -> list[dict]:
    """
    Find all function schemas with the GPTEnabled decorator.

    :param module: Module to search for GPTEnabled functions
    :param schema_type: Type of schema to return
    """
    return [x.schema.to_json(schema_type) for x in FindGPTEnabled(module)]


def FindGPTEnabledByName(module: ModuleType, name: str) -> Optional[Callable]:
    """
    Find a function with the GPTEnabled decorator by name.

    :param module: Module to search for GPTEnabled functions
    :param name: Name of the function to find
    """
    for func in FindGPTEnabled(module):
        if func.__name__ == name:
            return func
    return None


def FindGPTEnabledByTag(module: ModuleType, tag: str) -> list[Callable]:
    """
    Find all functions with the GPTEnabled decorator by tag.

    :param module: Module to search for GPTEnabled functions
    :param tag: Tag to search for
    """
    return [x for x in FindGPTEnabled(module) if x.has(tag)]


def SaveGPTEnabled(
    module: ModuleType, path: str, schema_type: SchemaType = SchemaType.API
):
    """
    Save all function schemas with the GPTEnabled decorator to a file.

    :param module: Module to search for GPTEnabled functions
    :param path: Path to save the schemas to
    :param schema_type: Type of schema to return
    """
    schemas = FindGPTEnabledSchemas(module, schema_type)
    json.dump(schemas, open(path, "w"))


class _GPTEnabled:
    def __init__(self, func, **kwargs) -> None:
        self.func = func
        self.schema = FunctionSchema(func)
        self.tags = kwargs.get("tags", [])
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):

        for key in kwargs:
            if key in self.schema.parameter_schemas:
                # Convert the JSON value to the type expected by the method
                kwargs[key] = self.schema.parameter_schemas[key].parse_value(
                    kwargs[key]
                )

        return self.func(*args, **kwargs)

    def gpt_enabled(self) -> bool:
        return True

    def has(self, tag: str) -> bool:
        return tag in self.tags


def GPTEnabled(func=None, **kwargs):
    """Decorator to generate a function schema for OpenAI."""
    if func:
        return _GPTEnabled(func, **kwargs)
    else:

        def wrapper(function):
            return _GPTEnabled(function, **kwargs)

        return wrapper


class FunctionSchema:
    """Automatically create a function schema for OpenAI."""

    def __init__(self, f: Callable, schema_type: SchemaType = SchemaType.API):
        """
        Initialize FunctionSchema for the given function.

        :param f: The function to create a schema for;
        :param schema_type: Type of schema;
        """
        self.f = f
        self.schema_type: SchemaType = schema_type
        self.schema: dict = {}
        self.parameter_schemas: dict[str, ParameterSchema] = {}
        self._populate_schema()

    def to_json(self, schema_type: SchemaType = SchemaType.API) -> dict:
        """
        Convert schema to JSON.
        :param schema_type: Type of schema to return
        """
        if schema_type == SchemaType.TUNE:
            return FunctionSchema(self.f, schema_type).to_json()["function"]
        return self.schema

    def add_enum(self, n: str, enum: list) -> "FunctionSchema":
        """
        Add enum property to a particular function parameter.

        :param n: The name of the parameter with the enum values
        :param enum: The list of values for the enum parameter
        """
        self.schema["function"]["parameters"]["properties"][n]["enum"] = enum
        return self

    def _populate_schema(self) -> None:
        """
        Populate the schema dictionary.
        """
        self.schema["type"] = "function"
        self.schema["function"] = {"name": self.f.__name__}

        description = self._extract_description()

        # Add the function description even if it is an empty string
        if description is not None:
            self.schema["function"]["description"] = description

        self._populate_parameter_schema()

    def _extract_description(self) -> Optional[str]:
        """
        Extract the function description, if present.

        :return: The function description, or None if not present
        """
        if docstring := self.f.__doc__:  # Check if docstring exists
            docstring = " ".join(
                [x.strip() for x in docstring.replace("\n", " ").split()]
            )
            if desc := re.findall(r"(.*?):param", docstring):
                return desc[0].strip()

            return docstring.strip()

        return None

    def _populate_parameter_schema(self) -> None:
        """
        Populate the parameters' dictionary.
        """
        json_schema = dict()

        for n, o in inspect.signature(self.f).parameters.items():
            if n == "kwargs":
                continue  # Skip kwargs

            for Param in PARAMETER_SCHEMAS:
                if Param.matches(o):
                    p = Param(o, self.f.__doc__)
                    json_schema[n] = p.to_json()
                    self.parameter_schemas[n] = p
                    break

        if self.parameter_schemas or self.schema_type == SchemaType.TUNE:
            self.schema["function"]["parameters"] = {"type": "object", "properties": {}}

        if self.parameter_schemas:
            self.schema["function"]["parameters"]["properties"] = json_schema
            self._populate_required_parameters()

    def _populate_required_parameters(self) -> None:
        """
        Populate the list of required parameters.
        """
        req_params = []
        for n, o in inspect.signature(self.f).parameters.items():
            if n == "kwargs":
                continue  # Skip kwargs
            if o.default == Parameter.empty:
                req_params.append(n)

        if req_params:
            self.schema["function"]["parameters"]["required"] = req_params
