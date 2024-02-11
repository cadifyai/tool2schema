from __future__ import annotations
from typing import Optional


class Config:
    """
    Configuration class for tool2schema.
    """

    def __init__(self, parent: Optional[Config] = None, **settings):
        self.parent = parent
        self.settings = settings
        self.tags: list[str] = self._get_setting("tags", [])
        self.ignored_parameters: list[str] = self._get_setting(
            "ignored_parameters", ["self", "args", "kwargs"]
        )

    def _get_setting(self, name: str, default):
        """
        Get a setting value from the settings dictionary or the parent configuration.
        If not found, return the default value.

        :param name: Name of the setting
        :param default: Default value, used when the setting is not found in
            the settings dictionary and this configuration has no parent
        :return: The requested setting value
        """
        if not self.parent:
            return self.settings.pop(name, default)

        return self.settings.pop(name, getattr(self.parent, name))
