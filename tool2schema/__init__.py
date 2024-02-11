# flake8: noqa
__version__ = "v0.6.0"

from .schema import (
    FindGPTEnabled,
    FindGPTEnabledByName,
    FindGPTEnabledByTag,
    FindGPTEnabledSchemas,
    GPTEnabled,
    SaveGPTEnabled,
    SchemaType,
)

from .config import Config

# Default global configuration
CONFIG = Config()


def _reset_config():
    """
    Reset the configuration to the default settings.
    """
    global CONFIG
    CONFIG = Config()
