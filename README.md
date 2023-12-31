# gpt2schema

A library to convert Python functions to schemas supported by the OpenAI API.

Inspired by [janekb04/py2gpt](https://github.com/janekb04/py2gpt) and [fastai/lm-hackers](https://github.com/fastai/lm-hackers).

## Why gpt2schema?

The OpenAI API supports [function calling](https://platform.openai.com/docs/guides/function-calling). However, to tell GPT what functions it can call, you must send the functions [in a JSON format](https://platform.openai.com/docs/api-reference/chat/create#chat-create-tool_choice). With `gpt2schema`, functions can be automatically converted to the correct JSON schema!

## Usage

`gpt2schema` uses certain features of your function to correctly populate the schema.

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

To get the schema for this function, simply use the `GPTEnabled` decorator.

```python
from gpt2schema import GPTEnabled

@GPTEnabled
def my_function(a: int, b: str = "Hello"):
    """
    Example function description.

    :param a: First parameter;
    :param b: Second parameter;
    """
    # Function code here...
```

The schema can then be accessed using the `schema` attribute.

```python
my_function.schema
```

This returns the function schema in JSON format.

```yaml
{
  'type': 'function',
  'function': {
    'name': 'my_function',
    'description': 'Example function description.',
    'parameters': {
      'type': 'object',
      'properties': {
        'a': {
          'type': 'int',
          'description': "First parameter",
        #   'enum': ['cube', 'screwdriver']
        },
        'b': {
          'type': 'str',
          'default': 'Hello',
          'description': 'Second parameter'
        }
      },
      'required': ['name']
    }
  }
}
```

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

```yaml
{
  'type': 'function',
  'function': {
    'name': 'my_function',
    'description': 'Example function description.',
    'parameters': {
      'type': 'object',
      'properties': {
        'a': {
          'type': 'int',
          'description': "First parameter",
        },
        'b': {
          'type': 'str',
          'default': 'Hello',
          'description': 'Second parameter'
          'enum': ['yes', 'no']
        }
      },
      'required': ['name']
    }
  }
}

```

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
