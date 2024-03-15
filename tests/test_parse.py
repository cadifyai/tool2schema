import pytest

from tests import functions
from tool2schema import ParseSchema
from tool2schema.schema import ParseException

####################################################
#  Test schema parsing with the 'functions' module #
####################################################


@pytest.mark.parametrize(
    "function",
    [functions.function, functions.function_no_params, functions.function_tags],
)
def test_parse_schema(function):
    assert ParseSchema(functions, function.schema.to_json()) == function


def test_parse_schema_missing_function():
    with pytest.raises(ParseException):
        ParseSchema(functions, {})


def test_parse_schema_missing_name():
    with pytest.raises(ParseException):
        ParseSchema(functions, {"function": {}})


def test_parse_schema_missing_parameter():
    invalid_schema = functions.function.schema.to_json()
    invalid_schema["function"]["parameters"]["properties"].pop("a")

    with pytest.raises(ParseException):
        ParseSchema(functions, invalid_schema)


def test_parse_schema_missing_parameter_type():
    invalid_schema = functions.function.schema.to_json()
    invalid_schema["function"]["parameters"]["properties"]["a"].pop("type")

    with pytest.raises(ParseException):
        ParseSchema(functions, invalid_schema)


def test_parse_schema_wrong_parameter_type():
    invalid_schema = functions.function.schema.to_json()
    invalid_schema["function"]["parameters"]["properties"]["a"]["type"] = "boolean"

    with pytest.raises(ParseException):
        ParseSchema(functions, invalid_schema)
