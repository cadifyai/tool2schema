import json

import pytest

from tests import functions
from tool2schema import ParseSchema
from tool2schema.schema import ParseException

########################################
#  Function class for testing purposes #
########################################


class Function:
    """
    Emulate openai.types.chat.chat_completion_message_tool_call.Function class.
    """

    def __init__(self, name: str, arguments: str):
        self.name = name
        self.arguments = arguments


######################################################
#  Test function parsing with the 'functions' module #
######################################################


@pytest.mark.parametrize(
    "function, arguments",
    [
        (functions.function, {"a": 1, "b": "test", "c": True, "d": [4, 5]}),
        (functions.function, {"a": 1, "b": "test", "c": True, "d": []}),
        (functions.function, {"a": 1, "b": "test"}),  # Omit args with default values
        (functions.function, {"a": 1, "b": "test", "d": [4, 5]}),  # Omit c only
        (functions.function_no_params, {}),
        (functions.function_literal, {"a": 1}),  # Omit b
        (functions.function_literal, {"a": 1, "b": "b"}),
        (functions.function_enum, {"a": functions.CustomEnum.Y.name}),
        (functions.function_add_enum, {"a": "MAYBE"}),
        (functions.function_union, {"a": True, "b": "x"}),
        (functions.function_union, {"a": None, "b": 1}),
    ],
)
def test_parse_schema(function, arguments):
    assert ParseSchema(functions, Function(function.__name__, json.dumps(arguments))) == function

    # Add hallucinated argument and verify parsing fails
    arguments["hallucinated"] = 4
    with pytest.raises(ParseException):
        ParseSchema(functions, Function(function.__name__, json.dumps(arguments)))


def test_parse_schema_missing_function():
    assert ParseSchema(functions, Function(functions.function_not_enabled.__name__, "{}")) is None


@pytest.mark.parametrize("arguments", ["", "{", "[]", "23", "null"])
def test_parse_invalid_json_arguments(arguments):
    with pytest.raises(ParseException):
        ParseSchema(functions, Function(functions.function.__name__, arguments))


@pytest.mark.parametrize(
    "function, arguments",
    [
        (functions.function, {"a": 1}),  # Missing required argument b
        (functions.function, {"a": "x", "b": "test"}),  # Invalid value for a
        (functions.function, {"a": 1, "b": 0}),  # Invalid value for b
        (functions.function, {"a": 1, "b": "", "c": "x"}),  # Invalid value for c
        (functions.function, {"a": 1, "b": "", "c": True, "d": False}),  # Invalid value for d
        (functions.function, {"a": 1, "b": "", "c": True, "d": [1, "a"]}),  # Invalid array value
        (functions.function, {"a": 1, "b": "", "c": True, "d": [1], "e": 4}),  # Hallucinated arg
        (functions.function_literal, {"a": 3}),  # Invalid value for a
        (functions.function_literal, {"a": 0, "b": "d"}),  # Invalid value for b
        (functions.function_enum, {"a": 1}),
        (functions.function_enum, {"a": "A"}),
        (functions.function_add_enum, {"a": "PERHAPS"}),
        (functions.function_add_enum, {"a": "MAYBE", "b": "MAYBE"}),  # Hallucinated arg
        (functions.function_union, {"a": None, "b": False}),  # Invalid value for b
        (functions.function_union, {"a": "x", "b": 1}),  # Invalid value for a
    ],
)
def test_parse_invalid_argument_values(function, arguments):
    f_obj = Function(function.__name__, json.dumps(arguments))

    with pytest.raises(ParseException):
        ParseSchema(functions, f_obj)

    # Verify the function is returned if validation is disabled
    assert ParseSchema(functions, f_obj, validate=False) == function
