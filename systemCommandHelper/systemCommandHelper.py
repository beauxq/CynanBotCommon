import asyncio
import traceback
from asyncio.subprocess import Process
from typing import Any, ByteString, Optional, Tuple

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backgroundTaskHelper import BackgroundTaskHelper
    from CynanBotCommon.systemCommandHelper.systemCommandHelperInterface import \
        SystemCommandHelperInterface
    from CynanBotCommon.timber.timberInterface import TimberInterface
except:
    import utils
    from backgroundTaskHelper import BackgroundTaskHelper
    from systemCommandHelper.systemCommandHelperInterface import \
        SystemCommandHelperInterface
    from timber.timberInterface import TimberInterface


class SystemCommandHelper(SystemCommandHelperInterface):

    def __init__(
        self,
        backgroundTaskHelper: BackgroundTaskHelper,
        timber: TimberInterface
    ):
        if not isinstance(backgroundTaskHelper, BackgroundTaskHelper):
            raise ValueError(f'backgroundTaskHelper argument is malformed: \"{backgroundTaskHelper}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__backgroundTaskHelper: BackgroundTaskHelper = backgroundTaskHelper
        self.__timber: TimberInterface = timber

    async def executeCommand(self, command: str, timeoutSeconds: float = 10):
        if not utils.isValidStr(command):
            self.__timber.log('SystemCommandHelper', f'Received malformed command argument: \"{command}\"')
            return
        elif not utils.isValidNum(timeoutSeconds):
            raise ValueError(f'timeoutSeconds argument is malformed: \"{timeoutSeconds}\"')
        elif timeoutSeconds < 3 or timeoutSeconds > utils.getIntMaxSafeSize():
            raise ValueError(f'timeoutSeconds argument is out of bounds: {timeoutSeconds}')

        process: Optional[Process] = None
        outputTuple: Optional[Tuple[ByteString]] = None
        exception: Optional[Exception] = None

        try:
            process = await asyncio.create_subprocess_shell(
                cmd = command,
                stdout = asyncio.subprocess.PIPE,
                stderr = asyncio.subprocess.PIPE,
                loop = self.__backgroundTaskHelper.getEventLoop()
            )

            outputTuple = await asyncio.wait_for(
                fut = process.communicate(),
                timeout = timeoutSeconds,
                loop = self.__backgroundTaskHelper.getEventLoop()
            )
        except TimeoutError as e:
            if process is not None:
                self.__timber.log('SystemCommandHelper', f'Process for command ({command}) has run too long ({timeoutSeconds=}) and will be killed')
                process.kill()

            exception = e
        except Exception as e:
            exception = e

        process = None

        if exception is not None and not isinstance(exception, TimeoutError):
            self.__timber.log('SystemCommandHelper', f'Encountered exception when attempting to run system command ({command}): {exception}', exception, traceback.format_exc())
            return

        outputString: Optional[str] = None

        if outputTuple is not None and len(outputTuple) >= 2:
            outputString = outputTuple[1].decode('utf-8').strip()

        if utils.isValidStr(outputString):
            self.__timber.log('SystemCommandHelper', f'Ran system command ({command}): \"{outputString}\"')
        else:
            self.__timber.log('SystemCommandHelper', f'Ran system command ({command})')
