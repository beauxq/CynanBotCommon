from json import JSONDecodeError
from typing import Any, Dict, Optional

from requests.models import Response

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.exceptions import \
        NetworkResponseIsClosedException
    from CynanBotCommon.network.networkClientType import NetworkClientType
    from CynanBotCommon.network.networkResponse import NetworkResponse
    from CynanBotCommon.timber.timber import Timber
except:
    import utils
    from network.exceptions import NetworkResponseIsClosedException
    from network.networkClientType import NetworkClientType
    from network.networkResponse import NetworkResponse
    from timber.timber import Timber


class RequestsResponse(NetworkResponse):

    def __init__(
        self,
        response: Response,
        url: str,
        timber: Timber
    ):
        if not isinstance(response, Response):
            raise ValueError(f'response argument is malformed: \"{response}\"')
        elif not utils.isValidStr(url):
            raise ValueError(f'url argument is malformed: \"{url}\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__response: Response = response
        self.__url: str = url
        self.__timber: Timber = timber

        self.__isClosed: bool = False

    async def close(self):
        if self.__isClosed:
            return

        self.__isClosed = True
        self.__response.close()

    def getNetworkClientType(self) -> NetworkClientType:
        return NetworkClientType.REQUESTS

    def getStatusCode(self) -> int:
        self.__requireNotClosed()
        return self.__response.status_code

    def getUrl(self) -> str:
        return self.__url

    def isClosed(self) -> bool:
        return self.__isClosed

    async def json(self) -> Optional[Dict[str, Any]]:
        self.__requireNotClosed()

        try:
            return self.__response.json()
        except JSONDecodeError as e:
            self.__timber.log('RequestsResponse', f'Unable to decode response into JSON for url \"{self.__url}\"', e)
            return None

    async def read(self) -> bytes:
        self.__requireNotClosed()
        return self.__response.content

    def __requireNotClosed(self):
        if self.isClosed():
            raise NetworkResponseIsClosedException(f'This response has already been closed! ({self.getNetworkClientType()})')
