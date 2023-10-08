from abc import ABC, abstractmethod
from typing import Optional

try:
    from CynanBotCommon.recurringActions.recurringActionEventListener import \
        RecurringActionEventListener
except:
    from recurringActions.recurringActionEventListener import \
        RecurringActionEventListener


class RecurringActionsMachineInterface(ABC):

    @abstractmethod
    def setEventListener(self, listener: Optional[RecurringActionEventListener]):
        pass

    @abstractmethod
    def startMachine(self):
        pass
