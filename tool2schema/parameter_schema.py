import re
import typing
from enum import Enum
from inspect import Parameter, isclass

TYPE_MAP = {
    "int": "integer",
    "float": "number",
    "str": "string",
    "bool": "boolean",
    "list": "array",
}


class ParameterSchema:
    """
    Automatically create a parameter schema given an instance of
    inspect.Parameter and a function documentation string.
    """

    def __init__(self, parameter: Parameter, docstring: str = None):
        """
        Create a new parameter schema.

        :param parameter: The parameter to create a schema for
        :param docstring: The docstring for the function containing the parameter
        """
        self.parameter = parameter
        self.docstring = docstring

    @staticmethod
    def matches(parameter: Parameter) -> bool:
        """
        Determine if this schema can be used for the given parameter.

        :return: True if this schema can be used to parse the given parameter;
        """
        raise NotImplementedError()

    def _add_type(self, schema: dict):
        """
        Add the type of this parameter to the given schema.
        """
        raise NotImplementedError()

    def _add_items(self, schema: dict):
        """
        Add the items property to the given schema.
        """
        pass

    def _add_enum(self, schema: dict):
        """
        Add the enum property to the given schema.
        """
        pass

    def _add_description(self, schema: dict):
        """
        Add the description of this parameter, extracted from the function docstring, to the given
        schema.
        """
        if self.docstring is None:
            return

        docstring = " ".join([x.strip() for x in self.docstring.replace("\n", " ").split()])
        params = re.findall(r":param ([^:]*): (.*?)(?=:param|:type|:return|:rtype|$)", docstring)
        for name, desc in params:
            if name == self.parameter.name and desc:
                schema["description"] = desc.strip()
                return

    def _add_default(self, schema: dict):
        """
        Add the default value, when present, to the given schema.
        """
        if self.parameter.default == Parameter.empty:
            return

        schema["default"] = self.parameter.default

    def to_json(self) -> dict:
        """
        Return the json schema for this parameter.
        """
        json = {}
        self._add_description(json)
        self._add_default(json)
        self._add_items(json)
        self._add_type(json)
        self._add_enum(json)
        return json

    def parse_value(self, value):
        """
        Convert the given value from the JSON representation to an instance
        that can be passed to the original method as a parameter. Overriding
        methods should check whether the value needs to be converted, and return
        it as is if no conversion is necessary.

        :param value: The value to be converted
        :return: An instance of the type required by the original method
        """
        return value


class ValueTypeSchema(ParameterSchema):
    """
    Parameter schema for value types.
    """

    @staticmethod
    def matches(parameter: Parameter) -> bool:
        return parameter.annotation != Parameter.empty and parameter.annotation.__name__ in TYPE_MAP

    def _add_type(self, schema: dict):
        schema["type"] = TYPE_MAP[self.parameter.annotation.__name__]


class GenericParameterSchema(ParameterSchema):
    """
    Base class for generic parameter types supporting subscription.
    """

    def _get_sub_type(self):
        if args := typing.get_args(self.parameter.annotation):
            return TYPE_MAP.get(args[0].__name__, "object")

        return None


class ListParameterSchema(GenericParameterSchema):
    """
    Parameter schema for list (array) types.
    """

    @staticmethod
    def matches(parameter: Parameter) -> bool:
        return parameter.annotation != Parameter.empty and (
            parameter.annotation is list or typing.get_origin(parameter.annotation) is list
        )

    def _add_type(self, schema: dict):
        schema["type"] = TYPE_MAP["list"]

    def _add_items(self, schema: dict):
        if sub_type := super()._get_sub_type():
            schema["items"] = {"type": sub_type}


class OptionalParameterSchema(GenericParameterSchema):
    """
    Parameter schema for typing.Optional types.
    """

    @staticmethod
    def matches(parameter: Parameter) -> bool:
        args = typing.get_args(parameter.annotation)
        return (
            parameter.annotation != parameter.empty
            and typing.get_origin(parameter.annotation) is typing.Union
            and len(args) == 2
            and type(None) in args
        )

    def _add_type(self, schema: dict):
        if sub_type := super()._get_sub_type():
            schema["type"] = sub_type


class EnumParameterSchema(ParameterSchema):
    """
    Parameter schema for Enum types.
    """

    def __init__(self, parameter: Parameter, docstring: str = None):
        super().__init__(parameter, docstring)
        self.enum_names = [e.name for e in parameter.annotation]

    @staticmethod
    def matches(parameter: Parameter) -> bool:
        return (
            parameter.annotation != parameter.empty
            and isclass(parameter.annotation)
            and issubclass(parameter.annotation, Enum)
        )

    def _add_type(self, schema: dict):
        schema["type"] = TYPE_MAP["str"]

    def _add_enum(self, schema: dict):
        schema["enum"] = self.enum_names

    def parse_value(self, value):
        """
        Convert an enum name to an instance of the enum type.

        :param value: The enum name to be converted
        """
        if value in self.enum_names:
            # Convert to an enum instance
            return self.parameter.annotation[value]

        # The user is invoking the method directly
        return value


class LiteralParameterSchema(ParameterSchema):
    """
    Parameter schema for typing.Literal types.
    """

    def __init__(self, parameter: Parameter, docstring: str = None):
        super().__init__(parameter, docstring)
        self.enum_values = list(typing.get_args(parameter.annotation))

    @staticmethod
    def matches(parameter: Parameter) -> bool:
        return (
            parameter.annotation != parameter.empty
            and typing.get_origin(parameter.annotation) is typing.Literal
        )

    def _add_type(self, schema: dict):
        schema["type"] = TYPE_MAP.get(type(self.enum_values[0]).__name__, "object")

    def _add_enum(self, schema: dict):
        schema["enum"] = self.enum_values


# Order matters: specific classes should appear before more generic ones;
# for example, ListParameterSchema must precede ValueTypeSchema,
# as they both match list types
PARAMETER_SCHEMAS = [
    OptionalParameterSchema,
    LiteralParameterSchema,
    EnumParameterSchema,
    ListParameterSchema,
    ValueTypeSchema,
]
