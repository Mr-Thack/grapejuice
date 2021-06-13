import logging
from abc import ABC, abstractmethod

LOG = logging.getLogger(__name__)


class IDBusConnection(ABC):
    @property
    def connected(self):
        return False

    @abstractmethod
    def launch_studio(self):
        pass

    @abstractmethod
    def play_game(self, uri):
        pass

    @abstractmethod
    def edit_local_game(self, place_path):
        pass

    @abstractmethod
    def edit_cloud_game(self, uri):
        pass

    @abstractmethod
    def install_roblox(self):
        pass

    @abstractmethod
    def version(self):
        pass

    @abstractmethod
    def extract_fast_flags(self):
        pass
