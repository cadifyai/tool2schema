import re
from inspect import Parameter

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

        :param parameter: The parameter to create a schema for;
        :param docstring: The docstring for the function containing the parameter;
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

    def add_type(self, schema: dict):
        """
        Add the type of this parameter to the given schema.
        """
        raise NotImplementedError()

    def add_items(self, schema: dict):
        """
        Add the items property to the given schema.
        """
        pass

    def add_enum(self, schema: dict):
        """
        Add the enum property to the given schema.
        """
        pass

    def add_description(self, schema: dict):
        """
        Add the description of this parameter, extracted from the function docstring, to the given schema.
        """
        if self.docstring is None:
            return

        docstring = " ".join(
            [x.strip() for x in self.docstring.replace("\n", " ").split()]
        )
        params = re.findall(r":param (.*?): (.*?);", docstring)
        for name, desc in params:
            if name == self.parameter.name:
                schema["description"] = desc
                return

    def add_default(self, schema: dict):
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
        self.add_description(json)
        self.add_default(json)
        self.add_items(json)
        self.add_type(json)
        self.add_enum(json)
        return json


class ValueTypeSchema(ParameterSchema):
    """
    Parameter schema for value types.
    """

    @staticmethod
    def matches(parameter: Parameter) -> bool:
        return (
            parameter.annotation != Parameter.empty
            and parameter.annotation.__name__ in TYPE_MAP
        )

    def add_type(self, schema: dict):
        schema["type"] = TYPE_MAP[self.parameter.annotation.__name__]


class ListParameterSchema(ParameterSchema):
    """
    Parameter schema for list (array) types.
    """

    @staticmethod
    def matches(parameter: Parameter) -> bool:
        return (
            parameter.annotation != Parameter.empty
            and parameter.annotation.__name__ == "list"
        )

    def add_type(self, schema: dict):
        schema["type"] = TYPE_MAP["list"]

    def add_items(self, schema: dict):
        if inner_type := re.findall(r"list\[(.*?)\]", str(self.parameter.annotation)):
            sub_type = TYPE_MAP.get(inner_type[0], "object")
            schema["items"] = {"type": sub_type}


class TypingParameterSchema(ParameterSchema):
    """
    Base class for typing module parameter schemas (e.g., typing.List).
    """

    def get_sub_type(self):
        if "__args__" in dir(self.parameter.annotation):
            annotation_name = self.parameter.annotation.__args__[0].__name__
            return TYPE_MAP.get(annotation_name, "object")

        return None


class TypingListParameterSchema(TypingParameterSchema):
    """
    Parameter schema for typing.List types.
    """

    @staticmethod
    def matches(parameter: Parameter) -> bool:
        return (
            parameter.annotation != Parameter.empty
            and re.match(r"typing\.List.*", str(parameter.annotation)) is not None
        )

    def add_type(self, schema: dict):
        schema["type"] = TYPE_MAP["list"]

    def add_items(self, schema: dict):
        if sub_type := super().get_sub_type():
            schema["items"] = {"type": sub_type}


class TypingOptionalParameterSchema(TypingParameterSchema):
    """
    Parameter schema for typing.Optional types.
    """

    @staticmethod
    def matches(parameter: Parameter) -> bool:
        return (
            parameter.annotation != parameter.empty
            and re.match(r"typing\.Optional.*", str(parameter.annotation)) is not None
        )

    def add_type(self, schema: dict):
        if sub_type := super().get_sub_type():
            schema["type"] = sub_type


PARAMETER_SCHEMAS = [
    TypingListParameterSchema,
    TypingOptionalParameterSchema,
    ListParameterSchema,
    ValueTypeSchema,
]
