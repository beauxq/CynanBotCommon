from abc import ABC, abstractmethod
from typing import Optional

try:
    from CynanBotCommon.tts.ttsEvent import TtsEvent
except:
    from tts.ttsEvent import TtsEvent


class TtsCommandBuilderInterface(ABC):

    @abstractmethod
    async def buildAndCleanEvent(self, event: Optional[TtsEvent]) -> Optional[str]:
        pass

    @abstractmethod
    async def buildAndCleanMessage(self, message: Optional[str]) -> Optional[str]:
        pass
