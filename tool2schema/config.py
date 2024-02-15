from __future__ import annotations

from typing import Optional


class Config:
    """
    Configuration class for tool2schema.
    """

    def __init__(self, parent: Optional[Config] = None, **settings):
        self.parent = parent
        self.settings = settings
        self.ignore_parameters: list[str] = self._get_setting(
            "ignore_parameters", ["self", "args", "kwargs"]
        )
        self.ignore_descriptions: bool = self._get_setting("ignore_descriptions", False)

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
