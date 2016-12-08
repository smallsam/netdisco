"""Discover MyAir devices."""
from . import BaseDiscoverable


class Discoverable(BaseDiscoverable):
    """Add support for discovering a MyAir device."""

    def __init__(self, netdis):
        """Initialize the MyAir discovery."""
        self._netdis = netdis

    def get_entries(self):
        """Get all the MyAir details."""
        return self._netdis.myair.entries
