import json
from typing import Callable, Union

import pytest

from tests import functions
from tool2schema import LoadToolEnabled
from tool2schema.schema import ParseException

###############################################
#  Helper method to get function dictionaries #
###############################################


def get_function_dict(func: Callable, arguments: Union[str, dict]):
    """
    Get a dictionary representation of a function, with its name and the
    specified argument values converted to a JSON string.
    """
    if isinstance(arguments, dict):
        arguments = json.dumps(arguments)

    return {
        "name": func.__name__,
        "arguments": arguments,
    }


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
def test_load_function(function, arguments):

    # Add hallucinated argument
    hall_args = {**arguments, "hallucinated": 4}

    f_dict = get_function_dict(function, hall_args)

    f, args = LoadToolEnabled(functions, f_dict)

    assert f == function
    assert args == arguments  # Verify the hallucinated argument has been removed

    f(**args)  # Verify invoking the function does not throw an exception

    # Verify we can pass the arguments as a dictionary
    f, args = LoadToolEnabled(functions, {"name": function.__name__, "arguments": arguments})

    assert f == function
    assert args == arguments

    # Verify an exception is raised if hallucinations are not ignored
    with pytest.raises(ParseException):
        LoadToolEnabled(
            functions,
            f_dict,
            validate=True,
            ignore_hallucinations=False,
        )


def test_load_missing_function():
    with pytest.raises(ParseException):
        LoadToolEnabled(functions, get_function_dict(functions.function_not_enabled, "{}"))


def test_load_invalid_arguments_type():
    with pytest.raises(ParseException):
        LoadToolEnabled(
            functions,
            {
                "name": functions.function.__name__,
                "arguments": 23,
            },
        )


@pytest.mark.parametrize("arguments", ["", "{", "[]", "23", "null"])
def test_load_invalid_json_arguments(arguments):
    with pytest.raises(ParseException):
        LoadToolEnabled(functions, get_function_dict(functions.function, arguments))


def test_load_missing_name():
    with pytest.raises(ParseException):
        LoadToolEnabled(functions, {"arguments": "{}"})


def test_load_missing_arguments():
    with pytest.raises(ParseException):
        LoadToolEnabled(functions, {"name": "function"})


@pytest.mark.parametrize(
    "function, arguments",
    [
        (functions.function, {"a": 1}),  # Missing required argument b
        (functions.function, {"a": "x", "b": "test"}),  # Invalid value for a
        (functions.function, {"a": 1, "b": 0}),  # Invalid value for b
        (functions.function, {"a": 1, "b": "", "c": "x"}),  # Invalid value for c
        (functions.function, {"a": 1, "b": "", "c": True, "d": False}),  # Invalid value for d
        (functions.function, {"a": 1, "b": "", "c": True, "d": [1, "a"]}),  # Invalid array value
        (functions.function, {"a": 1, "e": 4}),  # Missing argument and hallucinated arg
        (functions.function_literal, {"a": 3}),  # Invalid value for a
        (functions.function_literal, {"a": 0, "b": "d"}),  # Invalid value for b
        (functions.function_enum, {"a": 1}),
        (functions.function_enum, {"a": "A"}),
        (functions.function_add_enum, {"a": "PERHAPS"}),
        (functions.function_add_enum, {"a": "PERHAPS", "b": "MAYBE"}),
        (functions.function_union, {"a": None, "b": False}),  # Invalid value for b
        (functions.function_union, {"a": "x", "b": 1}),  # Invalid value for a
    ],
)
def test_load_invalid_argument_values(function, arguments):
    f_obj = get_function_dict(function, arguments)

    with pytest.raises(ParseException):
        LoadToolEnabled(functions, f_obj)

    # Verify the function and the arguments are returned if validation is disabled
    f, args = LoadToolEnabled(functions, f_obj, validate=False)
    assert f == function
    assert args == arguments
