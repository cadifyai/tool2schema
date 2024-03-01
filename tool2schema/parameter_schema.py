from __future__ import annotations

import re
from inspect import Parameter
from typing import Any, Optional, Union

from tool2schema import Config
from tool2schema.type_schema import EnumTypeSchema, TypeSchema


class ParameterSchema:
    """
    Automatically create a parameter schema given an instance of inspect.Parameter
    and a function documentation string.
    """

    def __init__(
        self,
        type_schema: TypeSchema,
        parameter: Parameter,
        index: int,
        config: Config,
        docstring: Optional[str] = None,
    ):
        """
        Create a new parameter schema.

        :param type_schema: The type schema for the parameter (use `TypeSchema.create`)
        :param parameter: The parameter to create a schema for
        :param index: The index of the parameter in the function signature
        :param config: Configuration settings to use when creating the schema
        :param docstring: The docstring for the function containing the parameter
        """
        self.type_schema = type_schema
        self.parameter = parameter
        self.index = index
        self.config = config
        self.docstring = docstring

    @staticmethod
    def create(
        parameter: Parameter, index: int, config: Config, docstring: Optional[str] = None
    ) -> Optional[ParameterSchema]:
        """
        Create a new parameter schema for the specified parameter.

        :param parameter: The parameter to create a schema for
        :param index: The index of the parameter in the function signature
        :param config: Configuration settings to use when creating the schema
        :param docstring: The docstring for the function containing the parameter
        :return: An instance of `ParameterSchema`, or None if the parameter type is not supported.
        """
        if type_schema := TypeSchema.create(parameter.annotation):
            return ParameterSchema(type_schema, parameter, index, config, docstring)

    def _get_description(self) -> Union[str, Parameter.empty]:
        """
        Get the description of this parameter, extracted from the function docstring,
        to be added to the JSON schema. Return `Parameter.empty` to omit the description
        from the schema.
        """
        if self.docstring is None or self.config.ignore_parameter_descriptions:
            return Parameter.empty

        docstring = " ".join([x.strip() for x in self.docstring.replace("\n", " ").split()])
        params = re.findall(r":param ([^:]*): (.*?)(?=:param|:type|:return|:rtype|$)", docstring)
        for name, desc in params:
            if name == self.parameter.name and desc:
                return desc.strip()

        return Parameter.empty

    def _get_default(self) -> Any:
        """
        Get the default value for this parameter, when present, to be added to the JSON schema.
        Return `Parameter.empty` to omit the default value from the schema.
        """
        if self.parameter.default != Parameter.empty:
            return self.type_schema.encode(self.parameter.default)

        # Not that the default value may be present but None, we use
        # Parameter.empty to indicate that the default value is not present
        return Parameter.empty

    def add_enum(self, values: list) -> None:
        """
        Convert this parameter to an enumeration type.

        :param values: List of unique enumeration values.
        """
        self.type_schema = EnumTypeSchema(values)

    def to_json(self) -> dict:
        """
        Return the json schema for this parameter.
        """
        fields = {
            "description": self._get_description(),
            "default": self._get_default(),
            **self.type_schema.to_json(),
        }

        json = {f: v for f, v in fields.items() if v != Parameter.empty}

        return json
