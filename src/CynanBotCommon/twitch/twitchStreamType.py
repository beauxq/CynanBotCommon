from enum import Enum, auto
from typing import Optional

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TwitchStreamType(Enum):

    LIVE = auto()
    UNKNOWN = auto()

    @classmethod
    def fromStr(ctls, text: Optional[str]):
        if not utils.isValidStr(text):
            return TwitchStreamType.UNKNOWN

        text = text.lower()

        if text == 'live':
            return TwitchStreamType.LIVE
        else:
            return TwitchStreamType.UNKNOWN
