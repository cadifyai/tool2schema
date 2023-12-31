import functools
import inspect
import re
from inspect import Parameter
from typing import Any, Callable, TypeAlias

# Type aliases
ToolSchema: TypeAlias = dict[str, Any]


class _GPTEnabled:
    """A decorator for AI enabled functions."""

    def __init__(self, func, **kwargs) -> None:
        self.func = func
        self.schema = FSchema(func)
        self.tags = kwargs.get("tags", [])
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def ai_enabled(self) -> bool:
        return True

    def has(self, tag: str) -> bool:
        return tag in self.tags


# wrap _Cache to allow for deferred calling
def GPTEnabled(func=None, **kwargs):
    if func:
        return _GPTEnabled(func, **kwargs)
    else:

        def wrapper(function):
            return _GPTEnabled(function, **kwargs)

        return wrapper


class FSchema:
    """Automatically create a function schema."""

    TYPE_MAP = {
        "int": "integer",
        "float": "number",
        "str": "string",
        "list": "array",
        "bool": "boolean",
    }

    def __init__(self, f: Callable):
        self.f = f
        self.schema = FSchema.schema(f)

    def to_json(self):
        """Convert to JSON"""
        return self.schema

    def add_enum(self, n: str, enum: list) -> "FSchema":
        """
        Add enum property to a particular function parameter.

        :param schema: The schema to modify;
        :param n: The name of the parameter with the enum values;
        :param enum: The list of values for the enum parameter;
        """
        self.schema["function"]["parameters"]["properties"][n]["enum"] = enum
        return self

    @staticmethod
    def schema(f: Callable):
        """
        Construct a function schema for OpenAI .

        :param f: Function for which to construct the schema;
        """
        return {
            "type": "function",
            "function": {
                "name": f.__name__,
                "description": FSchema.function_description(f).strip(),
                "parameters": {
                    "type": "object",
                    "properties": FSchema.param_schema(f),
                    "required": FSchema.required_params(f),
                },
            },
        }

    @staticmethod
    def param_schema(f: Callable):
        """
        Construct the parameter schema for a function.

        :param f: Function to extra parameter schema from;
        """
        parameters = dict()
        for n, o in inspect.signature(f).parameters.items():
            if n == "kwargs":
                continue  # Skip kwargs
            parameters[n] = {}
            if o.annotation != Parameter.empty:
                parameters[n]["type"] = FSchema.param_type(o)
                if parameters[n]["type"] == "array":
                    parameters[n]["items"] = {"type": FSchema.array_type(o)}

            if o.default != Parameter.empty:
                parameters[n]["default"] = o.default
            if desc := FSchema.param_description(f, n):
                parameters[n]["description"] = desc
        return parameters

    @staticmethod
    def required_params(f: Callable):
        """Get the list of required parameters for a function."""
        req_params = []
        for n, o in inspect.signature(f).parameters.items():
            if n == "kwargs":
                continue  # Skip kwargs
            if o.default == Parameter.empty:
                req_params.append(n)
        return req_params

    @staticmethod
    def array_type(o: Parameter) -> str:
        """
        Get the primitive type name contained within an array.

        :param o: Array-parameter to get the name from;
        """
        # Note interesting behaviour from o.annotation:
        # (o.annotation, o.annotation.__name__) = ("bool", <class 'bool')
        # (o.annotation, o.annotation.__name__) = (list[int], "list")
        assert (
            o.annotation.__name__ == "list"
        ), f"Cannot extract inner type from non-list parameter '{str(o.annotation)}'"
        inner_type = str(o.annotation)[
            len("list[") : -len("]")
        ]  # Extract 'int' from 'list[int]'
        if inner_type in FSchema.TYPE_MAP:
            return FSchema.TYPE_MAP[inner_type]
        return "object"

    @staticmethod
    def param_type(o: Parameter) -> str:
        """
        Get the appropriate parameter type name.

        :param o: Parameter to get the name from;
        """
        if o.annotation.__name__ == "Optional":
            if o.annotation.__args__:  # Check if Optional has a type
                return FSchema.TYPE_MAP[o.annotation.__args__[0].__name__]
        if o.annotation.__name__ in FSchema.TYPE_MAP:
            return FSchema.TYPE_MAP[o.annotation.__name__]
        return "object"

    @staticmethod
    def function_description(f: Callable):
        """
        Extract the function description.

        :param f: Function from which to extract description;
        """
        docstring = " ".join([x.strip() for x in f.__doc__.replace("\n", " ").split()])
        if desc := re.findall(r"(.*?):param", docstring):
            return desc[0]
        return docstring

    @staticmethod
    def param_description(f: Callable, n: str) -> str:
        """
        Extract the parameter description.

        :param f: Function the parameter is located in;
        :param n: Name of the parameter;
        """
        docstring = " ".join([x.strip() for x in f.__doc__.replace("\n", " ").split()])
        params = re.findall(r":param (.*?): (.*?);", docstring)
        for name, desc in params:
            if name == n:
                return desc
        return ""
