import copy
from enum import Enum
from typing import Callable, List, Literal, Optional

import pytest

import tool2schema
from tool2schema import (
    EnableTool,
    FindToolEnabled,
    FindToolEnabledByName,
    FindToolEnabledByNameSchema,
    FindToolEnabledByTag,
    FindToolEnabledByTagSchemas,
    FindToolEnabledSchemas,
    SchemaType,
)

from . import functions

##################################
#  Test FindToolEnabled/Schemas  #
##################################


def test_FindToolEnabled():
    tools = FindToolEnabled(functions)
    # Check that the function is found
    assert len(tools) == 7
    assert functions.function in tools
    assert functions.function_tags in tools
    assert functions.function_no_params in tools
    assert functions.function_no_params in tools
    assert functions.function_no_params in tools
    assert functions.function_literal in tools
    assert functions.function_add_enum in tools
    assert functions.function_enum in tools
    assert functions.function_union in tools
    # Check that the function is not found
    assert functions.function_not_enabled not in tools


def test_FindToolEnabledSchemas():
    tool_schemas = FindToolEnabledSchemas(functions)
    # Check that the function is found
    assert len(tool_schemas) == 7
    assert functions.function.to_json() in tool_schemas
    assert functions.function_tags.to_json() in tool_schemas
    assert functions.function_no_params.to_json() in tool_schemas
    assert functions.function_literal.to_json() in tool_schemas
    assert functions.function_add_enum.to_json() in tool_schemas
    assert functions.function_enum.to_json() in tool_schemas
    assert functions.function_union.to_json() in tool_schemas


@pytest.mark.parametrize("schema_type", [schema for schema in SchemaType])
def test_FindToolEnabledSchemas_with_type(schema_type):
    # Check that the function is found
    tool_schemas = FindToolEnabledSchemas(functions, schema_type=schema_type)
    assert len(tool_schemas) == 7
    assert functions.function.to_json(schema_type) in tool_schemas
    assert functions.function_tags.to_json(schema_type) in tool_schemas
    assert functions.function_no_params.to_json(schema_type) in tool_schemas
    assert functions.function_literal.to_json(schema_type) in tool_schemas
    assert functions.function_add_enum.to_json(schema_type) in tool_schemas
    assert functions.function_enum.to_json(schema_type) in tool_schemas
    assert functions.function_union.to_json(schema_type) in tool_schemas


#######################################
#  Test FindToolEnabledByName/Schema  #
#######################################


def test_FindToolEnabledByName():
    # Check that the function is found
    assert FindToolEnabledByName(functions, "function") == functions.function
    assert FindToolEnabledByName(functions, "function_tags") == functions.function_tags
    assert FindToolEnabledByName(functions, "function_no_params") == functions.function_no_params
    # Check that the function is not found
    assert FindToolEnabledByName(functions, "function_not_enabled") is None


def test_FindToolEnabledByNameSchemas():
    # Check that the function is found
    assert FindToolEnabledByNameSchema(functions, "function") == functions.function.to_json()
    assert FindToolEnabledByNameSchema(functions, "function_tags") == functions.function_tags.to_json()
    assert FindToolEnabledByNameSchema(functions, "function_no_params") == functions.function_no_params.to_json()
    # Check that the function is not found
    assert FindToolEnabledByName(functions, "function_not_enabled") is None


@pytest.mark.parametrize("schema_type", [schema for schema in SchemaType])
def test_FindToolEnabledByNameSchemas_with_type(schema_type):
    # Check that the function is found
    assert FindToolEnabledByNameSchema(functions, "function", schema_type=schema_type) == functions.function.to_json(schema_type)
    assert FindToolEnabledByNameSchema(functions, "function_tags", schema_type=schema_type) == functions.function_tags.to_json(schema_type)
    assert FindToolEnabledByNameSchema(functions, "function_no_params", schema_type=schema_type) == functions.function_no_params.to_json(schema_type)
    # Check that the function is not found
    assert FindToolEnabledByNameSchema(functions, "function_not_enabled", schema_type=schema_type) is None


######################################
#  Test FindToolEnabledByTag/Schema  #
######################################


def test_FindToolEnabledByTag():
    # Check that the function is found
    assert functions.function_tags in FindToolEnabledByTag(functions, "test")
    # Check that the function is not found
    assert functions.function not in FindToolEnabledByTag(functions, "test")


def test_FindToolEnabledByTagSchemas():
    # Check that the function is found
    assert FindToolEnabledByTagSchemas(functions, "test") == [functions.function_tags.to_json()]
    # Check that the function is not found
    assert functions.function.to_json() not in FindToolEnabledByTagSchemas(functions, "test")


@pytest.mark.parametrize("schema_type", [schema for schema in SchemaType])
def test_FindToolEnabledByTagSchemas_with_type(schema_type):
    # Check that the function is found
    assert FindToolEnabledByTagSchemas(functions, "test", schema_type=schema_type) == [functions.function_tags.to_json(schema_type)]
    # Check that the function is not found
    assert functions.function.to_json(schema_type) not in FindToolEnabledByTagSchemas(functions, "test", schema_type=schema_type)


############################################
#  Custom enum class for testing purposes  #
############################################


class CustomEnum(Enum):
    A = 1
    B = 2
    C = 3


##################################
#  ReferenceSchema helper class  #
##################################


# Expected JSON schema for 'function' defined below
DEFAULT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "function",
        "description": "This is a test function.",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "integer",
                    "description": "This is a parameter",
                },
                "b": {
                    "type": "string",
                    "description": "This is another parameter",
                },
                "c": {
                    "type": "boolean",
                    "description": "This is a boolean parameter",
                    "default": False,
                },
                "d": {
                    "type": "array",
                    "description": "This is a list parameter",
                    "items": {
                        "type": "integer",
                    },
                    "default": [1, 2, 3],
                },
            },
            "required": ["a", "b"],
        },
    },
}


class ReferenceSchema:
    """
    Helper class to create and edit JSON function schema dictionaries.
    """

    def __init__(self, f: Callable, reference_schema: Optional[dict] = None):
        """
        Initialize the schema.
        :param f: The function to create the schema for
        :param reference_schema: The schema to start with, defaults to DEFAULT_SCHEMA
        """
        self.schema = copy.deepcopy(reference_schema or DEFAULT_SCHEMA)
        self.get_function()["name"] = f.__name__

    @property
    def tune_schema(self):
        """
        :return: The tune version of the schema.
        """
        return self.get_function()

    @property
    def anthropic_schema(self):
        """
        :return: The anthropic version of the schema.
        """
        function_schema = self.get_function()
        function_schema["input_schema"] = function_schema.pop("parameters")
        return function_schema

    def remove_param(self, param: str) -> None:
        """
        Remove a parameter from the schema.

        :param param: Name of the parameter to remove
        """
        self.get_parameters()["properties"].pop(param)

        if (required := self.get_required_parameters()) and param in required:
            required.remove(param)

    def get_param(self, param: str) -> dict:
        """
        Get a parameter dictionary from the schema.

        :param param: Name of the parameter
        :return: The parameter dictionary
        """
        return self.get_parameters()["properties"][param]

    def set_param(self, param, value: dict) -> None:
        """
        Set a parameter dictionary.

        :param param: Name of the parameter
        :param value: The new parameter dictionary
        """
        self.get_parameters()["properties"][param] = value

    def get_required_parameters(self) -> Optional[list[str]]:
        """
        Get the list of required parameters, or none if not present.
        """
        return self.get_parameters().get("required")

    def get_function(self) -> dict:
        """
        Get the function dictionary.
        """
        return self.schema["function"]

    def get_parameters(self) -> dict:
        """
        Get the parameters' dictionary.
        """
        return self.get_function()["parameters"]

    def remove_parameter_descriptions(self) -> None:
        """
        Remove all descriptions from the schema.
        """
        # Remove all parameter descriptions
        for p in self.get_parameters()["properties"]:
            self.get_param(p).pop("description", None)


###########################################
#  Example function to test with no tags  #
###########################################


@EnableTool
def function(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is a list parameter
    """
    return a, b, c, d


def test_function():
    rf = ReferenceSchema(function)
    assert function.to_json() == rf.schema
    assert function.tags == []


def test_function_tune():
    rf = ReferenceSchema(function)
    assert function.to_json(SchemaType.OPENAI_TUNE) == rf.tune_schema
    assert function.to_json(SchemaType.ANTHROPIC_CLAUDE) == rf.anthropic_schema
    assert function.tags == []


########################################
#  Example function to test with tags  #
########################################


@EnableTool(tags=["test"])
def function_tags(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is a list parameter
    """
    return a, b, c, d


def test_function_tags():
    rf = ReferenceSchema(function_tags)
    assert function_tags.to_json() == rf.schema
    assert function_tags.tags == ["test"]


def test_function_tags_tune():
    rf = ReferenceSchema(function_tags)
    assert function_tags.to_json(SchemaType.OPENAI_TUNE) == rf.tune_schema
    assert function_tags.to_json(SchemaType.ANTHROPIC_CLAUDE) == rf.anthropic_schema
    assert function_tags.tags == ["test"]


#########################################################
#  Example function to test with enum (using add_enum)  #
#########################################################


@EnableTool
def function_enum(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is a list parameter
    """
    return a, b, c, d


function_enum.schema.add_enum("a", [1, 2, 3])  # noqa


def test_function_enum():
    rf = ReferenceSchema(function_enum)
    rf.get_param("a")["enum"] = [1, 2, 3]
    assert function_enum.to_json() == rf.schema
    assert function_enum.to_json(SchemaType.OPENAI_TUNE) == rf.tune_schema
    assert function_enum.to_json(SchemaType.ANTHROPIC_CLAUDE) == rf.anthropic_schema
    assert function_enum.tags == []


#########################################
#  Example function with no parameters  #
#########################################


@EnableTool
def function_no_params():
    """
    This is a test function.
    """
    return


def test_function_no_params():
    rf = ReferenceSchema(function_no_params)
    rf.get_function().pop("parameters")
    assert function_no_params.to_json() == rf.schema
    assert function_no_params.tags == []


def test_function_no_params_tune():
    rf = ReferenceSchema(function_no_params)
    rf.get_parameters().pop("required")
    rf.get_parameters()["properties"] = {}
    assert function_no_params.to_json(SchemaType.OPENAI_TUNE) == rf.tune_schema
    assert function_no_params.to_json(SchemaType.ANTHROPIC_CLAUDE) == rf.anthropic_schema
    assert function_no_params.tags == []


##########################################
#  Example function with no description  #
##########################################


@EnableTool
def function_no_description(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    """
    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is a list parameter
    """
    return a, b, c, d


def test_function_no_description():
    rf = ReferenceSchema(function_no_description)
    rf.get_function()["description"] = ""
    assert function_no_description.to_json() == rf.schema
    assert function_no_description.tags == []


###################################################
#  Example function with no parameter docstrings  #
###################################################


@EnableTool
def function_no_param_docstrings(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    """
    This is a test function.
    """
    return a, b, c, d


def test_function_no_param_docstrings():
    rf = ReferenceSchema(function_no_param_docstrings)

    for p in rf.get_parameters()["properties"]:
        rf.get_param(p).pop("description")

    assert function_no_param_docstrings.to_json() == rf.schema
    assert function_no_param_docstrings.tags == []


#####################################################
#  Example function with no parameter descriptions  #
#####################################################


@EnableTool
def function_no_param_descriptions(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    """
    This is a test function.

    :param a:
    :param b:
    :param c:
    :param d:
    """
    return a, b, c, d


def test_function_no_param_descriptions():
    rf = ReferenceSchema(function_no_param_descriptions)

    for p in rf.get_parameters()["properties"]:
        rf.get_param(p).pop("description")

    assert function_no_param_descriptions.to_json() == rf.schema
    assert function_no_param_descriptions.tags == []


########################################
#  Example function with no docstring  #
########################################


@EnableTool
def function_no_docstring(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    return a, b, c, d


def test_function_no_docstring():
    rf = ReferenceSchema(function_no_docstring)
    rf.get_function().pop("description")

    for p in rf.get_parameters()["properties"]:
        rf.get_param(p).pop("description")

    assert function_no_docstring.to_json() == rf.schema
    assert function_no_docstring.tags == []


#######################################################
#  Example function with list annotation but no type  #
#######################################################


@EnableTool
def function_list_no_type(a: int, b: str, c: bool = False, d: list = [1, 2, 3]):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is a list parameter
    """
    return a, b, c, d


def test_function_list_no_type():
    rf = ReferenceSchema(function_list_no_type)
    rf.get_param("d").pop("items")
    assert function_list_no_type.to_json() == rf.schema
    assert function_list_no_type.tags == []


####################################################
#  Example function with Optional type annotation  #
####################################################


@EnableTool
def function_optional(a: int, b: str, c: bool = False, d: Optional[int] = None):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is an optional parameter
    """
    return a, b, c, d


def test_function_optional():
    rf = ReferenceSchema(function_optional)
    rf.set_param(
        "d",
        {
            "description": "This is an optional parameter",
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": None,
        },
    )
    assert function_optional.to_json() == rf.schema
    assert function_optional.tags == []


@EnableTool
def function_optional_enum(a: int, b: str, c: bool = False, d: Optional[CustomEnum] = None):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is an optional parameter
    """
    return a, b, c, d


def test_function_optional_enum():
    rf = ReferenceSchema(function_optional_enum)
    rf.set_param(
        "d",
        {
            "description": "This is an optional parameter",
            "default": None,
            "anyOf": [{"enum": ["A", "B", "C"], "type": "string"}, {"type": "null"}],
        },
    )

    assert function_optional_enum.to_json() == rf.schema
    assert function_optional_enum.tags == []

    # Verify it is possible to invoke the function with the parsed value
    _, _, _, d = function_optional_enum(1, "", False, "A")
    assert d == CustomEnum.A

    _, _, _, d = function_optional_enum(1, "", False, d="A")
    assert d == CustomEnum.A

    # Verify it is possible to invoke the function with the Enum instance
    _, _, _, d = function_optional_enum(1, "", False, CustomEnum.A)
    assert d == CustomEnum.A

    _, _, _, d = function_optional_enum(1, "", False, d=CustomEnum.A)
    assert d == CustomEnum.A

    # Verify it is possible to invoke the function with None
    _, _, _, d = function_optional_enum(1, "", False, d=None)
    assert d is None


##################################################
#  Example function with typing.List annotation  #
##################################################


@EnableTool
def function_typing_list(a: int, b: str, c: bool = False, d: List[int] = [1, 2, 3]):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is a list parameter
    """
    return a, b, c, d


def test_function_typing_list():
    rf = ReferenceSchema(function_typing_list)
    assert function_typing_list.to_json() == rf.schema
    assert function_typing_list.tags == []


##############################################################
#  Example function with typing.List annotation but no type  #
##############################################################


@EnableTool
def function_typing_list_no_type(a: int, b: str, c: bool = False, d: List = [1, 2, 3]):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is a list parameter
    """
    return a, b, c, d


def test_function_typing_list_no_type():
    rf = ReferenceSchema(function_typing_list_no_type)
    rf.get_param("d").pop("items")
    assert function_typing_list_no_type.to_json() == rf.schema
    assert function_typing_list_no_type.tags == []


##########################################
#  Example function with long docstring  #
##########################################


# Docstring adapted from https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html
@EnableTool
def function_docstring(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    """Returns a list containing :class:`bluepy.btle.Characteristic`
    objects for the peripheral. If no arguments are given, will return all
    characteristics. If startHnd and/or endHnd are given, the list is
    restricted to characteristics whose handles are within the given range.

    :param a: Received Signal Strength Indication for the last received
        broadcast from the device. This is an integer value measured in dB,
        where 0 dB is the maximum (theoretical) signal strength, and more
        negative numbers indicate a weaker signal, defaults to 0
    :type a: int, optional
    :param b: A function handle of the form
        ``callback(client, characteristic, data)``, where ``client`` is a
        handle to the :class:`simpleble.SimpleBleClient` that invoked the
        callback, ``characteristic`` is the notified
        :class:`bluepy.blte.Characteristic` object and data is a
        `bytearray` containing the updated value. Defaults to None
    :type b: int, optional
    :param c: End index, defaults to 0xFFFF
    :type c: int, optional
    :param d: A list of UUID strings, defaults to None
    :type d: list, optional
    :return: List of returned :class:`bluepy.btle.Characteristic` objects
    :rtype: list
    """
    return a, b, c, d


def test_function_docstring():
    rf = ReferenceSchema(function_docstring)

    rf.get_function()["description"] = (
        "Returns a list containing :class:`bluepy.btle.Characteristic` "
        "objects for the peripheral. If no arguments are given, will return all "
        "characteristics. If startHnd and/or endHnd are given, the list is "
        "restricted to characteristics whose handles are within the given range."
    )

    rf.get_param("a")["description"] = (
        "Received Signal Strength Indication for the last received "
        "broadcast from the device. This is an integer value measured in dB, "
        "where 0 dB is the maximum (theoretical) signal strength, and more "
        "negative numbers indicate a weaker signal, defaults to 0"
    )

    rf.get_param("b")["description"] = (
        "A function handle of the form "
        "``callback(client, characteristic, data)``, where ``client`` is a "
        "handle to the :class:`simpleble.SimpleBleClient` that invoked the "
        "callback, ``characteristic`` is the notified "
        ":class:`bluepy.blte.Characteristic` object and data is a "
        "`bytearray` containing the updated value. Defaults to None"
    )

    rf.get_param("c")["description"] = "End index, defaults to 0xFFFF"
    rf.get_param("d")["description"] = "A list of UUID strings, defaults to None"

    assert function_docstring.to_json() == rf.schema
    assert function_docstring.tags == []


######################################################
#  Example functions with typing.Literal annotation  #
######################################################


@EnableTool
def function_typing_literal_int(
    a: Literal[1, 2, 3], b: str, c: bool = False, d: list[int] = [1, 2, 3]
):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is a list parameter
    """
    return a, b, c, d


def test_function_typing_literal_int():
    # Check schema
    rf = ReferenceSchema(function_typing_literal_int)
    rf.get_param("a")["enum"] = [1, 2, 3]
    assert function_typing_literal_int.to_json() == rf.schema
    assert function_typing_literal_int.tags == []


@EnableTool
def function_typing_literal_string(
    a: Literal["a", "b", "c"], b: str, c: bool = False, d: list[int] = [1, 2, 3]
):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is a list parameter
    """
    return a, b, c, d


def test_function_typing_literal_string():
    # Check schema
    rf = ReferenceSchema(function_typing_literal_string)
    rf.get_param("a")["enum"] = ["a", "b", "c"]
    rf.get_param("a")["type"] = "string"
    assert function_typing_literal_string.to_json() == rf.schema
    assert function_typing_literal_string.tags == []


#################################################
#  Example functions with enum.Enum annotation  #
#################################################


@EnableTool
def function_custom_enum(a: CustomEnum, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is a list parameter
    """
    return a, b, c, d


def test_function_custom_enum():
    rf = ReferenceSchema(function_custom_enum)
    a = rf.get_param("a")
    a["type"] = "string"
    a["enum"] = [x.name for x in CustomEnum]
    assert function_custom_enum.to_json() == rf.schema
    assert function_custom_enum.tags == []

    # Try invoking the function to verify that "A" is converted to CustomEnum.A,
    # passing the value as a positional argument
    a, _, _, _ = function_custom_enum(CustomEnum.A.name, b="", c=False, d=[])
    assert a == CustomEnum.A

    # Same as above but passing the value as a keyword argument
    a, _, _, _ = function_custom_enum(a=CustomEnum.A.name, b="", c=False, d=[])
    assert a == CustomEnum.A

    # Verify it is possible to invoke the function with the Enum instance
    a, _, _, _ = function_custom_enum(a=CustomEnum.A, b="", c=False, d=[])
    assert a == CustomEnum.A

    # Verify it is possible to invoke the function with positional args
    a, _, _, _ = function_custom_enum(CustomEnum.A, "", False, [])
    assert a == CustomEnum.A


@EnableTool
def function_custom_enum_default_value(
    a: int, b: CustomEnum = CustomEnum.B, c: bool = False, d: list[int] = [1, 2, 3]
):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is a list parameter
    """
    return a, b, c, d


def test_function_custom_enum_default_value():
    rf = ReferenceSchema(function_custom_enum_default_value)
    rf.get_required_parameters().remove("b")
    b = rf.get_param("b")
    b["type"] = "string"
    b["default"] = "B"
    b["enum"] = [x.name for x in CustomEnum]
    assert function_custom_enum_default_value.to_json() == rf.schema
    assert function_custom_enum_default_value.tags == []


@EnableTool
def function_custom_enum_list(
    a: int,
    b: str,
    c: bool = False,
    d: list[CustomEnum] = [CustomEnum.A, CustomEnum.B],
):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is a list parameter
    """
    return a, b, c, d


def test_function_custom_enum_list():
    rf = ReferenceSchema(function_custom_enum_list)
    b = rf.get_param("d")
    b["default"] = ["A", "B"]
    b["items"] = {"type": "string", "enum": ["A", "B", "C"]}

    assert function_custom_enum_list.to_json() == rf.schema
    assert function_custom_enum_list.tags == []

    # Verify we can invoke the function providing the encoded enum value
    _, _, _, d = function_custom_enum_list(1, "", False, ["A"])
    assert d == [CustomEnum.A]

    # Verify it works with keyword arguments as well
    _, _, _, d = function_custom_enum_list(1, "", False, d=["A"])
    assert d == [CustomEnum.A]

    # Verify we can invoke the function providing the enum instance
    _, _, _, d = function_custom_enum_list(1, "", False, [CustomEnum.A])
    assert d == [CustomEnum.A]

    # Verify it works with keyword arguments as well
    _, _, _, d = function_custom_enum_list(1, "", False, d=[CustomEnum.A])
    assert d == [CustomEnum.A]

    # Verify it works with keyword an empty list
    _, _, _, d = function_custom_enum_list(1, "", False, d=[])
    assert d == []


###########################
#  Test ignore_parameters #
###########################


@EnableTool(ignore_parameters=["a", "d"])
def function_ignore_parameters(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is a list parameter
    """
    return a, b, c, d


def test_function_ignore_parameters():
    rf = ReferenceSchema(function_ignore_parameters)
    rf.remove_param("a")
    rf.remove_param("d")
    assert function_ignore_parameters.to_json() == rf.schema
    assert function_ignore_parameters.to_json(SchemaType.OPENAI_TUNE) == rf.tune_schema
    assert function_ignore_parameters.to_json(SchemaType.ANTHROPIC_CLAUDE) == rf.anthropic_schema
    assert function_ignore_parameters.tags == []


#######################################
#  Test ignore_parameter_descriptions #
#######################################


@EnableTool(ignore_parameter_descriptions=True)
def function_ignore_parameter_descriptions(
    a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]
):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is a list parameter
    """
    return a, b, c, d


def test_function_ignore_parameter_descriptions():
    rf = ReferenceSchema(function_ignore_parameter_descriptions)
    rf.remove_parameter_descriptions()
    assert function_ignore_parameter_descriptions.to_json() == rf.schema
    assert function_ignore_parameter_descriptions.to_json(SchemaType.OPENAI_TUNE) == rf.tune_schema
    assert function_ignore_parameter_descriptions.to_json(SchemaType.ANTHROPIC_CLAUDE) == rf.anthropic_schema
    assert function_ignore_parameter_descriptions.tags == []


#####################################
#  Test ignore_function_description #
#####################################


@EnableTool(ignore_function_description=True)
def function_ignore_function_description(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is a list parameter
    """
    return a, b, c, d


def test_function_ignore_function_description():
    rf = ReferenceSchema(function_ignore_function_description)
    rf.get_function().pop("description")
    assert function_ignore_function_description.to_json() == rf.schema
    assert function_ignore_function_description.to_json(SchemaType.OPENAI_TUNE) == rf.tune_schema
    assert function_ignore_function_description.to_json(SchemaType.ANTHROPIC_CLAUDE) == rf.anthropic_schema
    assert function_ignore_function_description.tags == []


###############################
#  Test ignore_all_parameters #
###############################


@EnableTool(ignore_all_parameters=True)
def function_ignore_all_parameters(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is a list parameter
    """
    return a, b, c, d


def test_function_ignore_all_parameters():
    rf = ReferenceSchema(function_ignore_all_parameters)
    rf.get_function().pop("parameters")
    assert function_ignore_all_parameters.to_json() == rf.schema


def test_function_ignore_all_parameters_tune():
    rf = ReferenceSchema(function_ignore_all_parameters)
    rf.get_parameters().pop("required")
    rf.get_parameters()["properties"] = {}
    assert function_ignore_all_parameters.to_json(SchemaType.OPENAI_TUNE) == rf.tune_schema
    assert function_ignore_all_parameters.to_json(SchemaType.ANTHROPIC_CLAUDE) == rf.anthropic_schema
    assert function_ignore_all_parameters.tags == []


###############################
#  Test global configuration  #
###############################


@pytest.fixture
def global_config() -> tool2schema.config.Config:
    yield tool2schema.CONFIG

    # Ensure the global configuration is reset to the default after the test
    tool2schema.CONFIG.reset_default()


def test_global_configuration_ignore_parameters(global_config):
    # Change the global configuration
    global_config.ignore_parameters = ["b", "c"]

    rf = ReferenceSchema(function)
    rf.remove_param("b")
    rf.remove_param("c")
    assert function.to_json() == rf.schema
    assert function.to_json(SchemaType.OPENAI_TUNE) == rf.tune_schema
    assert function.to_json(SchemaType.ANTHROPIC_CLAUDE) == rf.anthropic_schema
    assert function.tags == []


def test_global_configuration_ignore_parameter_descriptions(global_config):
    # Change the global configuration
    tool2schema.CONFIG.ignore_parameter_descriptions = True

    rf = ReferenceSchema(function)
    rf.remove_parameter_descriptions()

    assert function.to_json() == rf.schema
    assert function.to_json(SchemaType.OPENAI_TUNE) == rf.tune_schema
    assert function.to_json(SchemaType.ANTHROPIC_CLAUDE) == rf.anthropic_schema
    assert function.tags == []


def test_global_configuration_ignore_function_description(global_config):
    # Change the global configuration
    tool2schema.CONFIG.ignore_function_description = True

    rf = ReferenceSchema(function)
    rf.get_function().pop("description")

    assert function.to_json() == rf.schema
    assert function.to_json(SchemaType.OPENAI_TUNE) == rf.tune_schema
    assert function.to_json(SchemaType.ANTHROPIC_CLAUDE) == rf.anthropic_schema
    assert function.tags == []


def test_global_configuration_ignore_all_parameters(global_config):
    # Change the global configuration
    tool2schema.CONFIG.ignore_all_parameters = True

    rf = ReferenceSchema(function)
    rf.get_function().pop("parameters")

    assert function.to_json() == rf.schema
    assert function.tags == []


def test_global_configuration_ignore_all_parameters_tune(global_config):
    # Change the global configuration
    tool2schema.CONFIG.ignore_all_parameters = True

    rf = ReferenceSchema(function)
    rf.get_parameters().pop("required")
    rf.get_parameters()["properties"] = {}

    assert function.to_json(SchemaType.OPENAI_TUNE) == rf.tune_schema
    assert function.to_json(SchemaType.ANTHROPIC_CLAUDE) == rf.anthropic_schema
    assert function.tags == []


def test_global_configuration_schema_type(global_config):
    # Change the global configuration
    tool2schema.CONFIG.schema_type = SchemaType.OPENAI_TUNE

    rf = ReferenceSchema(function)
    assert function.to_json() == rf.tune_schema
    assert function.tags == []


########################################
#  Test global configuration override  #
########################################


@EnableTool(ignore_all_parameters=False)
def function_ignore_all_parameters_override(
    a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]
):
    """
    This is a test function.

    :param a: This is a parameter
    :param b: This is another parameter
    :param c: This is a boolean parameter
    :param d: This is a list parameter
    """
    return a, b, c, d


def test_function_ignore_all_parameters_override(global_config):
    # Verify that the function schema is not affected by the global configuration
    global_config.ignore_all_parameters = True
    rf = ReferenceSchema(function_ignore_all_parameters_override)
    assert function_ignore_all_parameters_override.to_json() == rf.schema
