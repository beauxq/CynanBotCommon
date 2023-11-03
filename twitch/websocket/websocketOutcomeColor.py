from enum import Enum, auto

try:
    import CynanBotCommon.utils as utils
except:
    import utils
    

class WebsocketOutcomeColor(Enum):

    BLUE = auto()
    PINK = auto()

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = text.lower

        if text == 'blue':
            return WebsocketOutcomeColor.BLUE
        elif text == 'pink':
            return WebsocketOutcomeColor.PINK
        else:
            raise ValueError(f'unknown WebsocketOutcomeColor: \"{text}\"')
