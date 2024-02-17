import copy
from enum import Enum
from typing import Callable, List, Literal, Optional

from tool2schema import (
    FindGPTEnabled,
    FindGPTEnabledByName,
    FindGPTEnabledByTag,
    FindGPTEnabledSchemas,
    GPTEnabled,
    SchemaType,
)

from . import functions

#########################
#  Test FindGPTEnabled  #
#########################


def test_FindGPTEnabled():
    # Check that the function is found
    assert len(FindGPTEnabled(functions)) == 3
    assert functions.function in FindGPTEnabled(functions)
    assert functions.function_tags in FindGPTEnabled(functions)
    assert functions.function_no_params in FindGPTEnabled(functions)
    # Check that the function is not found
    assert functions.function_not_enabled not in FindGPTEnabled(functions)


################################
#  Test FindGPTEnabledSchemas  #
################################


def test_FindGPTEnabledSchemas():
    # Check that the function is found
    assert len(FindGPTEnabledSchemas(functions)) == 3
    assert functions.function.schema.to_json() in FindGPTEnabledSchemas(functions)
    assert functions.function_tags.schema.to_json() in FindGPTEnabledSchemas(functions)
    assert functions.function_no_params.schema.to_json() in FindGPTEnabledSchemas(functions)


def test_FindGPTEnabledSchemas_API():
    # Check that the function is found
    assert len(FindGPTEnabledSchemas(functions, schema_type=SchemaType.API)) == 3
    assert functions.function.schema.to_json(SchemaType.API) in FindGPTEnabledSchemas(
        functions, schema_type=SchemaType.API
    )
    assert functions.function_tags.schema.to_json(SchemaType.API) in FindGPTEnabledSchemas(
        functions, schema_type=SchemaType.API
    )
    assert functions.function_no_params.schema.to_json(SchemaType.API) in FindGPTEnabledSchemas(
        functions, schema_type=SchemaType.API
    )


def test_FindGPTEnabledSchemas_TUNE():
    # Check that the function is found
    assert len(FindGPTEnabledSchemas(functions, schema_type=SchemaType.TUNE)) == 3
    assert functions.function.schema.to_json(SchemaType.TUNE) in FindGPTEnabledSchemas(
        functions, schema_type=SchemaType.TUNE
    )
    assert functions.function_tags.schema.to_json(SchemaType.TUNE) in FindGPTEnabledSchemas(
        functions, schema_type=SchemaType.TUNE
    )
    assert functions.function_no_params.schema.to_json(SchemaType.TUNE) in FindGPTEnabledSchemas(
        functions, schema_type=SchemaType.TUNE
    )


###############################
#  Test FindGPTEnabledByName  #
###############################


def test_FindGPTEnabledByName():
    # Check that the function is found
    assert FindGPTEnabledByName(functions, "function") == functions.function
    assert FindGPTEnabledByName(functions, "function_tags") == functions.function_tags
    assert FindGPTEnabledByName(functions, "function_no_params") == functions.function_no_params
    # Check that the function is not found
    assert FindGPTEnabledByName(functions, "function_not_enabled") is None


##############################
#  Test FindGPTEnabledByTag  #
##############################


def test_FindGPTEnabledByTag():
    # Check that the function is found
    assert functions.function_tags in FindGPTEnabledByTag(functions, "test")
    # Check that the function is not found
    assert functions.function not in FindGPTEnabledByTag(functions, "test")


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
        self.schema["function"]["name"] = f.__name__

    @property
    def tune_schema(self):
        """
        :return: The tune version of the schema.
        """
        return self.schema["function"]

    def remove_param(self, param: str) -> None:
        """
        Remove a parameter from the schema.

        :param param: Name of the parameter to remove
        """
        self.schema["function"]["parameters"]["properties"].pop(param)

        if (required := self.get_required_parameters()) and param in required:
            required.remove(param)

    def get_param(self, param: str) -> dict:
        """
        Get a parameter dictionary from the schema.

        :param param: Name of the parameter
        :return: The parameter dictionary
        """
        return self.schema["function"]["parameters"]["properties"][param]

    def set_param(self, param, value: dict) -> None:
        """
        Set a parameter dictionary.

        :param param: Name of the parameter
        :param value: The new parameter dictionary
        """
        self.schema["function"]["parameters"]["properties"][param] = value

    def get_required_parameters(self) -> Optional[list[str]]:
        """
        Get the list of required parameters, or none if not present.
        """
        return self.schema["function"]["parameters"].get("required")


###########################################
#  Example function to test with no tags  #
###########################################


@GPTEnabled
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
    assert function.schema.to_json() == rf.schema
    assert function.tags == []


def test_function_tune():
    rf = ReferenceSchema(function)
    assert function.schema.to_json(SchemaType.TUNE) == rf.tune_schema
    assert function.tags == []


########################################
#  Example function to test with tags  #
########################################


@GPTEnabled(tags=["test"])
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
    assert function_tags.schema.to_json() == rf.schema
    assert function_tags.tags == ["test"]


def test_function_tags_tune():
    rf = ReferenceSchema(function_tags)
    assert function_tags.schema.to_json(SchemaType.TUNE) == rf.tune_schema
    assert function_tags.tags == ["test"]


#########################################################
#  Example function to test with enum (using add_enum)  #
#########################################################


@GPTEnabled
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
    assert function_enum.schema.to_json() == rf.schema
    assert function_enum.schema.to_json(SchemaType.TUNE) == rf.tune_schema
    assert function_enum.tags == []


#########################################
#  Example function with no parameters  #
#########################################


@GPTEnabled
def function_no_params():
    """
    This is a test function.
    """
    return


def test_function_no_params():
    rf = ReferenceSchema(function_no_params)
    rf.schema["function"].pop("parameters")
    assert function_no_params.schema.to_json() == rf.schema
    assert function_no_params.tags == []


def test_function_no_params_tune():
    rf = ReferenceSchema(function_no_params)
    rf.schema["function"]["parameters"].pop("required")
    rf.schema["function"]["parameters"]["properties"] = {}
    assert function_no_params.schema.to_json(SchemaType.TUNE) == rf.tune_schema
    assert function_no_params.tags == []


##########################################
#  Example function with no description  #
##########################################


@GPTEnabled
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
    rf.schema["function"]["description"] = ""
    assert function_no_description.schema.to_json() == rf.schema
    assert function_no_description.tags == []


###################################################
#  Example function with no parameter docstrings  #
###################################################


@GPTEnabled
def function_no_param_docstrings(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    """
    This is a test function.
    """
    return a, b, c, d


def test_function_no_param_docstrings():
    rf = ReferenceSchema(function_no_param_docstrings)

    for p in rf.schema["function"]["parameters"]["properties"]:
        rf.get_param(p).pop("description")

    assert function_no_param_docstrings.schema.to_json() == rf.schema
    assert function_no_param_docstrings.tags == []


#####################################################
#  Example function with no parameter descriptions  #
#####################################################


@GPTEnabled
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

    for p in rf.schema["function"]["parameters"]["properties"]:
        rf.get_param(p).pop("description")

    assert function_no_param_descriptions.schema.to_json() == rf.schema
    assert function_no_param_descriptions.tags == []


########################################
#  Example function with no docstring  #
########################################


@GPTEnabled
def function_no_docstring(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    return a, b, c, d


def test_function_no_docstring():
    rf = ReferenceSchema(function_no_docstring)
    rf.schema["function"].pop("description")

    for p in rf.schema["function"]["parameters"]["properties"]:
        rf.get_param(p).pop("description")

    assert function_no_docstring.schema.to_json() == rf.schema
    assert function_no_docstring.tags == []


#######################################################
#  Example function with list annotation but no type  #
#######################################################


@GPTEnabled
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
    assert function_list_no_type.schema.to_json() == rf.schema
    assert function_list_no_type.tags == []


####################################################
#  Example function with Optional type annotation  #
####################################################


@GPTEnabled
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
            "type": "integer",
            "default": None,
        },
    )
    assert function_optional.schema.to_json() == rf.schema
    assert function_optional.tags == []


##################################################
#  Example function with typing.List annotation  #
##################################################


@GPTEnabled
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
    assert function_typing_list.schema.to_json() == rf.schema
    assert function_typing_list.tags == []


##############################################################
#  Example function with typing.List annotation but no type  #
##############################################################


@GPTEnabled
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
    assert function_typing_list_no_type.schema.to_json() == rf.schema
    assert function_typing_list_no_type.tags == []


##########################################
#  Example function with long docstring  #
##########################################


# Docstring adapted from https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html
@GPTEnabled
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

    rf.schema["function"]["description"] = (
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

    assert function_docstring.schema.to_json() == rf.schema
    assert function_docstring.tags == []


######################################################
#  Example functions with typing.Literal annotation  #
######################################################


@GPTEnabled
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
    assert function_typing_literal_int.schema.to_json() == rf.schema
    assert function_typing_literal_int.tags == []


@GPTEnabled
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
    assert function_typing_literal_string.schema.to_json() == rf.schema
    assert function_typing_literal_string.tags == []


#################################################
#  Example functions with enum.Enum annotation  #
#################################################


class CustomEnum(Enum):
    A = 1
    B = 2
    C = 3


@GPTEnabled
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
    assert function_custom_enum.schema.to_json() == rf.schema
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


@GPTEnabled
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
    assert function_custom_enum_default_value.schema.to_json() == rf.schema
    assert function_custom_enum_default_value.tags == []
