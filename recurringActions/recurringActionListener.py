from abc import ABC, abstractmethod

try:
    from CynanBotCommon.recurringActions.recurringAction import RecurringAction
except:
    from recurringActions.recurringAction import RecurringAction


class RecurringActionListener(ABC):

    @abstractmethod
    async def onNewRecurringAction(self, action: RecurringAction):
        pass