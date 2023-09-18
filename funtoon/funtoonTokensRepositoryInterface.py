from abc import abstractmethod
from typing import Optional

try:
    from CynanBotCommon.clearable import Clearable
except:
    from clearable import Clearable


class FuntoonTokensRepositoryInterface(Clearable):

    @abstractmethod
    async def getToken(self, twitchChannel: str) -> Optional[str]:
        pass

    @abstractmethod
    async def requireToken(self, twitchChannel: str) -> str:
        pass

    @abstractmethod
    async def setToken(self, token: Optional[str], twitchChannel: str):
        pass
