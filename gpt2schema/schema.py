import functools
import inspect
import re
from inspect import Parameter
from typing import Callable, Optional


class _GPTEnabled:
    def __init__(self, func, **kwargs) -> None:
        self.func = func
        self.schema = FunctionSchema(func)
        self.tags = kwargs.get("tags", [])
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
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
    """Automatically create a function schema."""

    TYPE_MAP = {
        "int": "integer",
        "float": "number",
        "str": "string",
        "bool": "boolean",
        "list": "array",
    }

    def __init__(self, f: Callable):
        self.f = f
        self.schema = FunctionSchema.schema(f)

    def to_json(self):
        """Convert schema to JSON."""
        return self.schema

    def add_enum(self, n: str, enum: list) -> "FunctionSchema":
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
        Construct a function schema for OpenAI.

        :param f: Function for which to construct the schema;
        """
        fschema = {"type": "function", "function": {"name": f.__name__}}
        fschema = FunctionSchema._function_description(f, fschema)
        fschema = FunctionSchema._param_schema(f, fschema)
        return fschema

    @staticmethod
    def _function_description(f: Callable, fschema: dict) -> dict:
        """
        Extract the function description.

        :param f: Function from which to extract description;
        """
        if docstring := f.__doc__:  # Check if docstring exists
            docstring = " ".join(
                [x.strip() for x in docstring.replace("\n", " ").split()]
            )
            if desc := re.findall(r"(.*?):param", docstring):
                fschema["function"]["description"] = desc[0].strip()
                return fschema
            fschema["function"]["description"] = docstring.strip()
        return fschema

    @staticmethod
    def _param_schema(f: Callable, fschema: dict) -> dict:
        """
        Construct the parameter schema for a function.

        :param f: Function to extra parameter schema from;
        """
        param_schema = {"type": "object", "properties": {}}
        if params := FunctionSchema._param_properties(f):
            param_schema["properties"] = params
            if required_params := FunctionSchema._param_required(f):
                param_schema["required"] = required_params
            fschema["function"]["parameters"] = param_schema
        return fschema

    @staticmethod
    def _param_properties(f: Callable) -> dict:
        """
        Construct the parameter properties for a function.

        :param f: Function to extra parameter properties from;
        """
        pschema = dict()
        for n, o in inspect.signature(f).parameters.items():
            if n == "kwargs":
                continue  # Skip kwargs
            pschema[n] = {}
            pschema[n] = FunctionSchema._param_type(o, pschema[n])
            pschema[n] = FunctionSchema._param_description(f, n, pschema[n])
            pschema[n] = FunctionSchema._param_default(o, pschema[n])
        return pschema

    @staticmethod
    def _param_required(f: Callable) -> dict:
        """
        Get the list of required parameters for a function.

        :param f: Function to extract required parameters from;
        """
        req_params = []
        for n, o in inspect.signature(f).parameters.items():
            if n == "kwargs":
                continue  # Skip kwargs
            if o.default == Parameter.empty:
                req_params.append(n)
        return req_params

    @staticmethod
    def _param_type(o: Parameter, pschema: dict) -> dict:
        """
        Get the appropriate parameter schema.

        :param o: Parameter to get the name from;
        :param pschema: Parameter schema to update;
        """
        if o.annotation != Parameter.empty:
            if o.annotation.__name__ == "Optional":
                if (sub_type := FunctionSchema._sub_type(o)) is not None:
                    pschema["type"] = sub_type
            elif o.annotation.__name__.lower() == "list":
                pschema["type"] = FunctionSchema.TYPE_MAP["list"]
                if (sub_type := FunctionSchema._sub_type(o)) is not None:
                    pschema["items"] = {"type": sub_type}
            elif o.annotation.__name__ in FunctionSchema.TYPE_MAP:
                pschema["type"] = FunctionSchema.TYPE_MAP.get(
                    o.annotation.__name__, "object"
                )
        return pschema

    @staticmethod
    def _sub_type(o: Parameter) -> Optional[dict]:
        """
        Get the type from the Optional or list annotation.

        :param o: Parameter to get the name from;
        """
        if o.annotation.__name__ == "Optional":
            if o.annotation.__args__:
                annotation_name = o.annotation.__args__[0].__name__
                return FunctionSchema.TYPE_MAP.get(annotation_name, "object")
        elif o.annotation.__name__.lower() == "list":
            if inner_type := re.findall(r"[Ll]ist\[(.*?)\]", str(o.annotation)):
                return FunctionSchema.TYPE_MAP.get(inner_type[0], "object")
        return None

    @staticmethod
    def _param_description(f: Callable, n: str, pschema: dict) -> dict:
        """
        Extract the parameter description.

        :param f: Function the parameter is located in;
        :param n: Name of the parameter;
        """
        if f.__doc__ is not None:
            docstring = " ".join(
                [x.strip() for x in f.__doc__.replace("\n", " ").split()]
            )
            params = re.findall(r":param (.*?): (.*?);", docstring)
            for name, desc in params:
                if name == n:
                    pschema["description"] = desc
                    return pschema
        return pschema

    @staticmethod
    def _param_default(o: Parameter, pschema: dict) -> dict:
        """
        Extract the parameter default value.

        :param o: Parameter to extract default value from;
        """
        if o.default != Parameter.empty:
            pschema["default"] = o.default
        return pschema
