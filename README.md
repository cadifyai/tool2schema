# tool2schema

[![Check Code](https://github.com/cadifyai/tool2schema/actions/workflows/python-package.yml/badge.svg?branch=main)](https://github.com/cadifyai/tool2schema/actions/workflows/python-package.yml)

A library to convert Python functions to schemas supported by the OpenAI API.

Inspired by [janekb04/py2gpt](https://github.com/janekb04/py2gpt) and [fastai/lm-hackers](https://github.com/fastai/lm-hackers).

## Why tool2schema?

The OpenAI API supports [function calling](https://platform.openai.com/docs/guides/function-calling). However, to tell GPT what functions it can call, you must send the functions [in a JSON format](https://platform.openai.com/docs/api-reference/chat/create#chat-create-tools). With `tool2schema`, functions can be automatically converted to the correct JSON schema!

## Installation

You can install `tool2schema` using `pip`.

```bash
pip3 install tool2schema
```

## Usage

On all functions that you would like to get JSON schema for, simply add the `GPTEnabled` decorator.

```python
# my_functions.py
from tool2schema import GPTEnabled

@GPTEnabled
def my_function1(a: int, b: str = "Hello"):
    """
    Example function description.

    :param a: First parameter;
    :param b: Second parameter;
    """
    # Function code here...

@GPTEnabled(tags=["tag1"])
def my_function2(a: int, b: str = "Hello"):
    """
    Example function description.

    :param a: First parameter;
    :param b: Second parameter;
    """
    # Function code here...
```

`tool2schema` provides some methods to easily retrieve your functions.

```python
import my_functions  # Module containing your functions
import tool2schema

# Return functions with GPTEnabled decorator
gpt_enable = tool2schema.FindGPTEnabled(my_functions)

# Return all function schemas
schemas = tool2schema.FindGPTEnabledSchemas(my_functions)

# Return function with given name
f = tool2schema.FindGPTEnabledByName(my_functions, "my_function1")

# Returns all functions with given tag
fs = tool2schema.FindGPTEnabledByTag(my_functions, "tag1")

# Saves function schemas to JSON file
json_path = # Path to JSON file
tool2schema.SaveGPTEnabled(my_functions, json_path)
```

## How it Works

`tool2schema` uses certain features of your function to correctly populate the schema.

- Parameter type hints
- Parameter default values
- Docstring with parameter descriptions

The docstring must be of a specific format. An example function is defined below that utilises all of the above features.

```python
def my_function(a: int, b: str = "Hello"):
    """
    Example function description.

    :param a: First parameter;
    :param b: Second parameter;
    """
```

**Note** the `;` at the end of each parameter description. This is used to indicate the end of the parameter description.

To get the schema for this function, simply use the `GPTEnabled` decorator. The decorator will return a class with some additional attributes but can still be called as a function.

The schema of the function be accessed using the `schema` attribute.

```python
my_function.schema.to_json()
```

This returns the function schema in JSON format.

### Supported Parameter Types

The following parameter types are supported:

- `int`
- `float`
- `str`
- `bool`
- `list`

Any other parameter types will be listed as `object` in the schema.

### Enumerations

If you want to limit the possible values of a parameter, you can use the `enum` keyword argument.

```python
@GPTEnabled
def my_function(a: int, b: str,):
    """
    Example function description.

    :param a: First parameter;
    :param b: Second parameter;
    """
    # Function code here...
my_function.schema.add_enum("b", ["yes", "no"])
```

The schema will then be updated to include the `enum` keyword.

### Tags

The `GPTEnabled` decorator also supports the `tags` keyword argument. This allows you to add tags to your function schema.

```python
@GPTEnabled(tags=["tag1", "tag2"])
def my_function(a: int, b: str = "Hello"):
    """
    Example function description.

    :param a: First parameter;
    :param b: Second parameter;
    """
    # Function code here...
```

The tags can then be accessed using the `tags` attribute.

```python
my_function.tags  # ["tag1", "tag2"]
```

You can check if a function has a certain tag using the `has_tag` method.

```python
my_function.has_tag("tag1")  # True
```
