from __future__ import annotations

import copy
import functools
import inspect
import json
import re
import sys
from inspect import Parameter
from types import ModuleType
from typing import Any, Callable, Generic, Literal, Optional, TypeVar, Union, overload

import tool2schema
from tool2schema.config import Config, SchemaType
from tool2schema.parameter_schema import ParameterSchema

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec


def FindToolEnabled(module: ModuleType) -> list[ToolEnabled]:
    """
    Find all functions with the EnableTool decorator.

    :param module: Module to search for ToolEnabled functions
    """
    return [x for x in module.__dict__.values() if hasattr(x, "tool_enabled")]


def FindToolEnabledSchemas(
    module: ModuleType, schema_type: Optional[SchemaType] = None
) -> list[dict]:
    """
    Find all function schemas with the EnableTool decorator.

    :param module: Module to search for ToolEnabled functions
    :param schema_type: Type of schema to return (None indicates default)
    """
    return [x.to_json(schema_type) for x in FindToolEnabled(module)]


def FindToolEnabledByName(module: ModuleType, name: str) -> Optional[ToolEnabled]:
    """
    Find a function with the EnableTool decorator by name.

    :param module: Module to search for ToolEnabled functions
    :param name: Name of the function to find
    """
    func: ToolEnabled
    for func in FindToolEnabled(module):
        if func.__name__ == name:
            return func
    return None


def FindToolEnabledByNameSchema(
    module: ModuleType, name: str, schema_type: Optional[SchemaType] = None
) -> Optional[dict]:
    """
    Find a function schema with the EnableTool decorator by name.

    :param module: Module to search for ToolEnabled functions
    :param name: Name of the function to find
    :param schema_type: Type of schema to return (None indicates default)
    """
    if (func := FindToolEnabledByName(module, name)) is None:
        return None
    return func.to_json(schema_type)


def FindToolEnabledByTag(module: ModuleType, tag: str) -> list[ToolEnabled]:
    """
    Find all functions with the EnableTool decorator by tag.

    :param module: Module to search for ToolEnabled functions
    :param tag: Tag to search for
    """
    return [x for x in FindToolEnabled(module) if x.has(tag)]


def FindToolEnabledByTagSchemas(
    module: ModuleType, tag: str, schema_type: Optional[SchemaType] = None
) -> list[dict]:
    """
    Find all function schemas with the EnableTool decorator by tag.

    :param module: Module to search for ToolEnabled functions
    :param tag: Tag to search for
    :param schema_type: Type of schema to return (None indicates default)
    """
    return [x.to_json(schema_type) for x in FindToolEnabledByTag(module, tag)]


def SaveToolEnabled(module: ModuleType, path: str, schema_type: Optional[SchemaType] = None):
    """
    Save all function schemas with the EnableTool decorator to a file.

    :param module: Module to search for ToolEnabled functions
    :param path: Path to save the schemas to
    :param schema_type: Type of schema to return (None indicates default)
    """
    schemas = FindToolEnabledSchemas(module, schema_type)
    json.dump(schemas, open(path, "w"))


class ParseException(Exception):
    """Exception for schema parsing errors."""
    pass


def LoadToolEnabled(
    module: ModuleType,
    function: dict,
    validate: bool = True,
    ignore_hallucinations: bool = True,
) -> tuple[Callable, dict[str, Any]]:
    """
    Given a function dictionary containing the name of a function and the arguments to pass to it,
    retrieve the corresponding function among those with the `EnableTool` decorator defined in
    `module`. When `validate` is true, validate the arguments and raise `ParseException` if the
    arguments are not valid (see more information below).

    :param module: The module where the function is defined
    :param function: A dictionary with keys `name` and `arguments`, where `name` is the name of
        the function to find, and `arguments` is either a dictionary of argument values or a JSON
        string that can be parsed to a dictionary of argument values.
    :param validate: Whether to validate the function arguments
    :param ignore_hallucinations: When true, any hallucinated arguments are ignored; when false,
        an exception is raised if any hallucinated arguments are found. `validate` must be true.
    :return: A tuple consisting of the function and a dictionary of argument values
    :raises ParseException: Thrown when any of the following conditions is met:
        - Function isn't defined in the given module, or is not decorated with `EnableTool`
        - The arguments are given as string and the string is not valid, meaning it is:
            - Not parsable as JSON, or;
            - Is not parsed into a dictionary of argument values
        - A required argument is missing and `validate` is true
        - An argument has a value that is not of the expected type and `validate` is true
        - The dictionary contains an argument that is not expected by the function, `validate` is
          true and `ignore_hallucinations` is false
    """

    if not (name := function.get("name", None)):
        raise ParseException("'name' key is missing from the dictionary")

    if (arguments := function.get("arguments", None)) is None:
        raise ParseException("'arguments' key is missing from the dictionary")

    if isinstance(arguments, dict):
        # Avoid altering the original dictionary
        arguments = copy.deepcopy(arguments)

    elif isinstance(arguments, str):
        # Parse the JSON string
        try:
            arguments = json.loads(arguments)

        except json.decoder.JSONDecodeError:
            raise ParseException("Arguments are not in valid JSON format")

        if type(arguments) is not dict:
            raise ParseException("Arguments are not in the form of a dictionary")

    else:
        # Invalid type
        raise ParseException(f"Arguments cannot be of type {type(arguments)}")

    f = FindToolEnabledByName(module, name)

    if not f:
        # A function with the given name was not found
        raise ParseException(
            f"Function with name '{name}' is not defined in given module "
            f"'{module.__name__}' or is missing 'EnableTool' decorator"
        )

    if validate:
        arguments = _validate_arguments(f, arguments, ignore_hallucinations)

    return f, arguments


def _validate_arguments(f: ToolEnabled, arguments: dict, ignore_hallucinations: bool) -> dict:
    """
    Verify that all required arguments are present, and the arguments are of the expected type.
    Raise an exception if any of these conditions is not met, or if there are any hallucinated
    arguments and `ignore_hallucinations` is false.

    :param f: A EnableTool-decorated function
    :param arguments: Arguments to validate
    :param ignore_hallucinations: Whether to ignore hallucinated arguments or throw an exception
        if any are present
    :return: A dictionary of validated arguments
    """
    validated = {}

    for key, param in f.schema.parameter_schemas.items():
        value = arguments.pop(key, Parameter.empty)

        if value == Parameter.empty:
            # The parameter is missing from the arguments
            if param.parameter.default == Parameter.empty:
                # The parameter does not have a default value
                raise ParseException(f"Required argument '{key}' is missing")
        else:
            if not param.type_schema.validate(value):
                raise ParseException(f"Argument '{key}' cannot accept value '{value}'")

            validated[key] = value

    if not ignore_hallucinations and arguments:
        raise ParseException(f"Hallucinated argument(s): {', '.join(arguments.keys())}")

    return validated


P = ParamSpec("P")  # User-provided function parameters type
T = TypeVar("T")  # User-provided function return type


class ToolEnabled(Generic[P, T]):
    def __init__(self, func: Callable[P, T], **kwargs) -> None:
        self.func = func
        self.tags = kwargs.pop("tags", [])
        self.config = Config(tool2schema.CONFIG, **kwargs)
        self.schema = FunctionSchema(func, self.config)
        self.__name__ = func.__name__
        functools.update_wrapper(self, func)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:

        args_list = list(args)  # Tuple is immutable, thus convert to list

        for i, arg in enumerate(args_list):
            for p in self.schema.parameter_schemas.values():
                if p.index == i:
                    # Convert the JSON value to the type expected by the method
                    args_list[i] = p.type_schema.decode(arg)

        for key in kwargs:
            if key in self.schema.parameter_schemas:
                # Convert the JSON value to the type expected by the method
                kwargs[key] = self.schema.parameter_schemas[key].type_schema.decode(kwargs[key])

        return self.func(*args_list, **kwargs)  # type: ignore

    def tool_enabled(self) -> bool:
        return True

    def to_json(self, schema_type: Optional[SchemaType] = None) -> dict:
        """
        Return JSON schema for the function.

        :param schema_type: None indicates default schema type
        :return: JSON schema
        """
        return self.schema.to_json(schema_type)

    def has(self, tag: str) -> bool:
        return tag in self.tags


@overload
def EnableTool(func: Callable[P, T], **kwargs) -> ToolEnabled[P, T]: ...


@overload
def EnableTool(func: Literal[None] = None, **kwargs) -> Callable[[Callable[P, T]], ToolEnabled[P, T]]: ...


def EnableTool(func: Optional[Callable[P, T]] = None, **kwargs) -> Union[ToolEnabled[P, T], Callable[[Callable[P, T]], ToolEnabled[P, T]]]:
    """Decorator to generate a function schema for OpenAI."""
    if func is not None:
        return ToolEnabled(func, **kwargs)
    else:

        def wrapper(function: Callable[P, T]) -> ToolEnabled[P, T]:
            return ToolEnabled(function, **kwargs)

        return wrapper


class FunctionSchema:
    """Automatically create a function schema for OpenAI."""

    def __init__(self, f: Callable, config: Config):
        """
        Initialize FunctionSchema for the given function.

        :param f: The function to create a schema for
        :param config: Configuration settings
        """
        self.f = f
        self.config = config
        self._all_parameter_schemas: dict[str, ParameterSchema] = self._get_all_parameter_schemas()

    def to_json(self, schema_type: Optional[SchemaType] = None) -> dict:
        """
        Convert schema to JSON.
        :param schema_type: Type of schema to return
        """
        schema_type = schema_type or self.config.schema_type
        if schema_type == SchemaType.OPENAI_TUNE:
            return self._get_function_schema(schema_type)
        elif schema_type == SchemaType.ANTHROPIC_CLAUDE:
            return self._get_function_schema(schema_type)

        return self._get_schema()

    def add_enum(self, n: str, enum: list) -> FunctionSchema:
        """
        Add enum property to a particular function parameter.

        :param n: The name of the parameter with the enum values
        :param enum: The list of values for the enum parameter
        :return: This function schema
        """
        self._all_parameter_schemas[n].add_enum(enum)
        return self

    def _get_schema(self) -> dict:
        """
        Get the complete schema dictionary.
        """
        # This dictionary is only used with the API schema type
        return {"type": "function", "function": self._get_function_schema(SchemaType.OPENAI_API)}

    def _get_function_schema(self, schema_type: SchemaType) -> dict:
        """
        Get the function schema dictionary.
        """
        schema: dict[str, Any] = {"name": self.f.__name__}

        need_empty_param = schema_type in [
            SchemaType.OPENAI_TUNE,
            SchemaType.ANTHROPIC_CLAUDE]
        if self.parameter_schemas or need_empty_param:
            # If the schema type is tune, add the dictionary even if there are no parameters
            if schema_type == SchemaType.ANTHROPIC_CLAUDE:
                schema["input_schema"] = self._get_parameters_schema()
            else:
                schema["parameters"] = self._get_parameters_schema()

        if (description := self._get_description()) is not None:
            # Add the function description even if it is an empty string
            schema["description"] = description

        return schema

    def _get_parameters_schema(self) -> dict:
        """
        Get the parameters schema dictionary.
        """
        schema = {"type": "object", "properties": self._get_parameter_properties_schema()}

        if required := self._get_required_parameters():
            schema["required"] = required

        return schema

    def _get_parameter_properties_schema(self) -> dict:
        """
        Get the properties schema for the function.
        """
        schema = dict()

        for n, p in self.parameter_schemas.items():
            schema[n] = p.to_json()

        return schema

    def _get_all_parameter_schemas(self) -> dict[str, ParameterSchema]:
        """
        Get a dictionary of all parameter schemas for the function
        (including ignored parameters).

        :return: A dictionary with parameter names as keys and
            parameter schemas as values
        """
        parameters = dict()

        for i, (n, o) in enumerate(inspect.signature(self.f).parameters.items()):
            if schema := ParameterSchema.create(o, i, self.config, self.f.__doc__):
                parameters[n] = schema

        return parameters

    def _get_description(self) -> Optional[str]:
        """
        Extract the function description, if present.

        :return: The function description, or None if not present
        """
        if not (docstring := self.f.__doc__) or self.config.ignore_function_description:
            return None

        docstring = " ".join([x.strip() for x in docstring.replace("\n", " ").split()])
        if desc := re.findall(r"(.*?):param", docstring):
            return desc[0].strip()

        return docstring.strip()

    def _get_required_parameters(self) -> list[str]:
        """
        Get the list of required parameters.

        :return: The list of parameters without a default value
        """
        req_params = []
        for n, p in self.parameter_schemas.items():
            if p.parameter.default == Parameter.empty:
                req_params.append(n)

        return req_params

    @property
    def parameter_schemas(self) -> dict[str, ParameterSchema]:
        """
        Return a dictionary of parameter schemas, where keys are parameter names
        and values are instances of `ParameterSchema`. Ignored parameters are not
        included in the dictionary.

        :return: A dictionary of parameter schemas
        """
        return (
            {}
            if self.config.ignore_all_parameters
            else {
                k: v
                for k, v in self._all_parameter_schemas.items()
                if k not in self.config.ignore_parameters
            }
        )
