from abc import ABC, abstractmethod
from typing import Optional


class FuntoonTokensRepositoryInterface(ABC):

    @abstractmethod
    async def clearCaches(self):
        pass

    @abstractmethod
    async def getToken(self, twitchChannel: str) -> Optional[str]:
        pass

    @abstractmethod
    async def requireToken(self, twitchChannel: str) -> str:
        pass

    @abstractmethod
    async def setToken(self, token: Optional[str], twitchChannel: str):
        pass
