from typing import List, Optional

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
    assert functions.function_no_params.schema.to_json() in FindGPTEnabledSchemas(
        functions
    )


def test_FindGPTEnabledSchemas_API():
    # Check that the function is found
    assert len(FindGPTEnabledSchemas(functions, schema_type=SchemaType.API)) == 3
    assert functions.function.schema.to_json(SchemaType.API) in FindGPTEnabledSchemas(
        functions, schema_type=SchemaType.API
    )
    assert functions.function_tags.schema.to_json(
        SchemaType.API
    ) in FindGPTEnabledSchemas(functions, schema_type=SchemaType.API)
    assert functions.function_no_params.schema.to_json(
        SchemaType.API
    ) in FindGPTEnabledSchemas(functions, schema_type=SchemaType.API)


def test_FindGPTEnabledSchemas_TUNE():
    # Check that the function is found
    assert len(FindGPTEnabledSchemas(functions, schema_type=SchemaType.TUNE)) == 3
    assert functions.function.schema.to_json(SchemaType.TUNE) in FindGPTEnabledSchemas(
        functions, schema_type=SchemaType.TUNE
    )
    assert functions.function_tags.schema.to_json(
        SchemaType.TUNE
    ) in FindGPTEnabledSchemas(functions, schema_type=SchemaType.TUNE)
    assert functions.function_no_params.schema.to_json(
        SchemaType.TUNE
    ) in FindGPTEnabledSchemas(functions, schema_type=SchemaType.TUNE)


###############################
#  Test FindGPTEnabledByName  #
###############################


def test_FindGPTEnabledByName():
    # Check that the function is found
    assert FindGPTEnabledByName(functions, "function") == functions.function
    assert FindGPTEnabledByName(functions, "function_tags") == functions.function_tags
    assert (
        FindGPTEnabledByName(functions, "function_no_params")
        == functions.function_no_params
    )
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


###########################################
#  Example function to test with no tags  #
###########################################


@GPTEnabled
def function(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    """
    This is a test function.

    :param a: This is a parameter;
    :param b: This is another parameter;
    :param c: This is a boolean parameter;
    :param d: This is a list parameter;
    """
    return a, b, c, d


def test_function():
    # Check schema
    expected_schema = {
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
    assert function.schema.to_json() == expected_schema
    assert function.tags == []


def test_function_tune():
    # Check schema
    expected_schema = {
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
    }
    assert function.schema.to_json(SchemaType.TUNE) == expected_schema
    assert function.tags == []


########################################
#  Example function to test with tags  #
########################################


@GPTEnabled(tags=["test"])
def function_tags(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    """
    This is a test function.

    :param a: This is a parameter;
    :param b: This is another parameter;
    :param c: This is a boolean parameter;
    :param d: This is a list parameter;
    """
    return a, b, c, d


def test_function_tags():
    # Check schema
    expected_schema = {
        "type": "function",
        "function": {
            "name": "function_tags",
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
    assert function_tags.schema.to_json() == expected_schema
    assert function_tags.tags == ["test"]


def test_function_tags_tune():
    # Check schema
    expected_schema = {
        "name": "function_tags",
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
    }
    assert function_tags.schema.to_json(SchemaType.TUNE) == expected_schema
    assert function_tags.tags == ["test"]


########################################
#  Example function to test with enum  #
########################################


@GPTEnabled
def function_enum(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    """
    This is a test function.

    :param a: This is a parameter;
    :param b: This is another parameter;
    :param c: This is a boolean parameter;
    :param d: This is a list parameter;
    """
    return a, b, c, d


function_enum.schema.add_enum("a", [1, 2, 3])  # noqa


def test_function_enum():
    # Check schema
    expected_schema = {
        "type": "function",
        "function": {
            "name": "function_enum",
            "description": "This is a test function.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer",
                        "description": "This is a parameter",
                        "enum": [1, 2, 3],
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
    assert function_enum.schema.to_json() == expected_schema
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
    # Check schema
    expected_schema = {
        "type": "function",
        "function": {
            "name": "function_no_params",
            "description": "This is a test function.",
        },
    }
    assert function_no_params.schema.to_json() == expected_schema
    assert function_no_params.tags == []


def test_function_no_params_tune():
    # Check schema
    expected_schema = {
        "name": "function_no_params",
        "description": "This is a test function.",
        "parameters": {"type": "object", "properties": {}},
    }
    assert function_no_params.schema.to_json(SchemaType.TUNE) == expected_schema
    assert function_no_params.tags == []


##########################################
#  Example function with no description  #
##########################################


@GPTEnabled
def function_no_description(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    """
    :param a: This is a parameter;
    :param b: This is another parameter;
    :param c: This is a boolean parameter;
    :param d: This is a list parameter;
    """
    return a, b, c, d


def test_function_no_description():
    # Check schema
    expected_schema = {
        "type": "function",
        "function": {
            "name": "function_no_description",
            "description": "",
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
    assert function_no_description.schema.to_json() == expected_schema
    assert function_no_description.tags == []


###################################################
#  Example function with no parameter docstrings  #
###################################################


@GPTEnabled
def function_no_param_docstrings(
    a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]
):
    """
    This is a test function.
    """
    return a, b, c, d


def test_function_no_param_docstrings():
    # Check schema
    expected_schema = {
        "type": "function",
        "function": {
            "name": "function_no_param_docstrings",
            "description": "This is a test function.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer",
                    },
                    "b": {
                        "type": "string",
                    },
                    "c": {
                        "type": "boolean",
                        "default": False,
                    },
                    "d": {
                        "type": "array",
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
    assert function_no_param_docstrings.schema.to_json() == expected_schema
    assert function_no_param_docstrings.tags == []


#####################################################
#  Example function with no parameter descriptions  #
#####################################################


@GPTEnabled
def function_no_param_descriptions(
    a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]
):
    """
    This is a test function.

    :param a:
    :param b:
    :param c:
    :param d:
    """
    return a, b, c, d


def test_function_no_param_descriptions():
    # Check schema
    expected_schema = {
        "type": "function",
        "function": {
            "name": "function_no_param_descriptions",
            "description": "This is a test function.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer",
                    },
                    "b": {
                        "type": "string",
                    },
                    "c": {
                        "type": "boolean",
                        "default": False,
                    },
                    "d": {
                        "type": "array",
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
    assert function_no_param_descriptions.schema.to_json() == expected_schema
    assert function_no_param_descriptions.tags == []


########################################
#  Example function with no docstring  #
########################################


@GPTEnabled
def function_no_docstring(a: int, b: str, c: bool = False, d: list[int] = [1, 2, 3]):
    return a, b, c, d


def test_function_no_docstring():
    # Check schema
    expected_schema = {
        "type": "function",
        "function": {
            "name": "function_no_docstring",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer",
                    },
                    "b": {
                        "type": "string",
                    },
                    "c": {
                        "type": "boolean",
                        "default": False,
                    },
                    "d": {
                        "type": "array",
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
    assert function_no_docstring.schema.to_json() == expected_schema
    assert function_no_docstring.tags == []


#######################################################
#  Example function with list annotation but no type  #
#######################################################


@GPTEnabled
def function_list_no_type(a: int, b: str, c: bool = False, d: list = [1, 2, 3]):
    """
    This is a test function.

    :param a: This is a parameter;
    :param b: This is another parameter;
    :param c: This is a boolean parameter;
    :param d: This is a list parameter;
    """
    return a, b, c, d


def test_function_list_no_type():
    # Check schema
    expected_schema = {
        "type": "function",
        "function": {
            "name": "function_list_no_type",
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
                        "default": [1, 2, 3],
                    },
                },
                "required": ["a", "b"],
            },
        },
    }
    assert function_list_no_type.schema.to_json() == expected_schema
    assert function_list_no_type.tags == []


####################################################
#  Example function with Optional type annotation  #
####################################################


@GPTEnabled
def function_optional(a: int, b: str, c: bool = False, d: Optional[int] = None):
    """
    This is a test function.

    :param a: This is a parameter;
    :param b: This is another parameter;
    :param c: This is a boolean parameter;
    :param d: This is an optional parameter;
    """
    return a, b, c, d


def test_function_optional():
    # Check schema
    expected_schema = {
        "type": "function",
        "function": {
            "name": "function_optional",
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
                        "type": "integer",
                        "description": "This is an optional parameter",
                        "default": None,
                    },
                },
                "required": ["a", "b"],
            },
        },
    }
    assert function_optional.schema.to_json() == expected_schema
    assert function_optional.tags == []


##################################################
#  Example function with typing.List annotation  #
##################################################


@GPTEnabled
def function_typing_list(a: int, b: str, c: bool = False, d: List[int] = [1, 2, 3]):
    """
    This is a test function.

    :param a: This is a parameter;
    :param b: This is another parameter;
    :param c: This is a boolean parameter;
    :param d: This is a list parameter;
    """
    return a, b, c, d


def test_function_typing_list():
    # Check schema
    expected_schema = {
        "type": "function",
        "function": {
            "name": "function_typing_list",
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
    assert function_typing_list.schema.to_json() == expected_schema
    assert function_typing_list.tags == []


##############################################################
#  Example function with typing.List annotation but no type  #
##############################################################


@GPTEnabled
def function_typing_list_no_type(a: int, b: str, c: bool = False, d: List = [1, 2, 3]):
    """
    This is a test function.

    :param a: This is a parameter;
    :param b: This is another parameter;
    :param c: This is a boolean parameter;
    :param d: This is a list parameter;
    """
    return a, b, c, d


def test_function_typing_list_no_type():
    # Check schema
    expected_schema = {
        "type": "function",
        "function": {
            "name": "function_typing_list_no_type",
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
                        "default": [1, 2, 3],
                    },
                },
                "required": ["a", "b"],
            },
        },
    }
    assert function_typing_list_no_type.schema.to_json() == expected_schema
    assert function_typing_list_no_type.tags == []
