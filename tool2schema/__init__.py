# flake8: noqa
__version__ = "v0.6.0"

from .config import Config
from .schema import (
    FindGPTEnabled,
    FindGPTEnabledByName,
    FindGPTEnabledByTag,
    FindGPTEnabledSchemas,
    GPTEnabled,
    SaveGPTEnabled,
    SchemaType,
)

# Default global configuration
CONFIG = Config()


def _reset_config():
    """
    Reset the configuration to the default settings.
    """
    global CONFIG
    CONFIG = Config()
