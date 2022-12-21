import math
from typing import Any, Dict, List, Optional

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TestUtils():

    def test_areAllStrsInts_withEmptyList(self):
        result: bool = None
        exception: Exception = None

        try:
            result = utils.areAllStrsInts(list())
        except Exception as e:
            exception = e

        assert result is None
        assert exception is not None
        assert isinstance(exception, Exception)

    def test_areAllStrsInts_withIntList(self):
        result = utils.areAllStrsInts([ '1', '10', '100', '1000' ])
        assert result is True

    def test_areAllStrsInts_withMixedList(self):
        result = utils.areAllStrsInts([ '1', '10', '100', 'hello', '1000', 'world' ])
        assert result is False

    def test_areAllStrsInts_withNone(self):
        result: bool = None
        exception: Exception = None

        try:
            result = utils.areAllStrsInts(None)
        except Exception as e:
            exception = e

        assert result is None
        assert exception is not None
        assert isinstance(exception, Exception)

    def test_areAllStrsInts_withWordList(self):
        result = utils.areAllStrsInts([ 'hello', 'world' ])
        assert result is False

    def test_areValidBools_withEmptyList(self):
        result = utils.areValidBools(list())
        assert result is False

    def test_areValidBools_withEmptyStringList(self):
        result = utils.areValidBools([ '', '\n', 'hello', 'world', '' ])
        assert result is False

    def test_areValidBools_withIntList(self):
        result = utils.areValidBools([ 100, 200 ])
        assert result is False

    def test_areValidBools_withMixedTypeList(self):
        result = utils.areValidBools([ True, 'hello', 1, False ])
        assert result is False

    def test_areValidBools_withNone(self):
        result = utils.areValidBools(None)
        assert result is False

    def test_areValidBools_withValidList(self):
        result = utils.areValidBools([ True, False, False, True ])
        assert result is True

    def test_areValidStrs_withEmptyList(self):
        result = utils.areValidStrs(list())
        assert result is False

    def test_areValidStrs_withEmptyStringList(self):
        result = utils.areValidStrs([ '', '\n', 'hello', 'world', '' ])
        assert result is False

    def test_areValidStrs_withIntList(self):
        result = utils.areValidStrs([ 100, 200 ])
        assert result is False

    def test_areValidStrs_withMixedTypeList(self):
        result = utils.areValidStrs([ True, 'hello', 1, False ])
        assert result is False

    def test_areValidStrs_withNone(self):
        result = utils.areValidStrs(None)
        assert result is False

    def test_areValidStrs_withValidList(self):
        result = utils.areValidStrs([ 'hello', 'world' ])
        assert result is True

    def test_containsUrl_withEmptyString(self):
        result = utils.containsUrl('')
        assert result is False

    def test_containsUrl_withGoogle(self):
        result = utils.containsUrl('https://www.google.com/')
        assert result is True

    def test_containsUrl_withGoogleSentence(self):
        result = utils.containsUrl('There\'s a URL here: https://www.google.com/ in this sentence.')
        assert result is True

    def test_containsUrl_withNone(self):
        result = utils.containsUrl(None)
        assert result is False

    def test_containsUrl_withRandomNoise1(self):
        result = utils.containsUrl('Qd19u(KAyCuZ~qNQkd-iy\\%\\E|KxRc')
        assert result is False

    def test_containsUrl_withRandomNoise2(self):
        result = utils.containsUrl('.s*&Sxwa}RZ\\\'AIkvD6:&OkVT#_YA`')
        assert result is False

    def test_copyList_withEmptyList(self):
        original: List = list()
        result: List = utils.copyList(original)
        assert result is not None
        assert len(result) == 0
        assert result is not original

    def test_copyList_withIntList(self):
        original: List[int] = [ 1, 2, 3, 4 ]
        result: List = utils.copyList(original)
        assert result is not None
        assert len(result) == 4
        assert result is not original
        assert result == original

    def test_copyList_withNone(self):
        result: List = utils.copyList(None)
        assert result is not None
        assert len(result) == 0

    def test_copyList_withStrList(self):
        original: List[str] = [ '1', '2', '3', '4' ]
        result: List = utils.copyList(original)
        assert result is not None
        assert len(result) == 4
        assert result is not original
        assert result == original

    def test_getBoolFromDict_withEmptyDict(self):
        d: Dict[str, Any] = dict()
        value: Optional[bool] = None
        exception: Optional[Exception] = None

        try:
            value = utils.getBoolFromDict(d = d, key = "hello")
        except Exception as e:
            exception = e

        assert value is None
        assert exception is not None

    def test_getBoolFromDict_withEmptyDictAndNoneFallback(self):
        d: Dict[str, Any] = dict()
        value: Optional[bool] = None
        exception: Optional[Exception] = None

        try:
            value = utils.getBoolFromDict(d = d, key = "hello")
        except Exception as e:
            exception = e

        assert value is None
        assert exception is not None

    def test_getBoolFromDict_withNoneDict(self):
        d: Optional[Dict[str, Any]] = None
        value: Optional[bool] = None
        exception: Optional[Exception] = None

        try:
            value = utils.getBoolFromDict(d = d, key = "hello", fallback = True)
        except Exception as e:
            exception = e

        assert value is True
        assert exception is None

    def test_getBoolFromDict_withNoneDictAndNoneFallback(self):
        d: Optional[Dict[str, Any]] = None
        value: Optional[bool] = None
        exception: Optional[Exception] = None

        try:
            value = utils.getBoolFromDict(d = d, key = "hello")
        except Exception as e:
            exception = e

        assert value is None
        assert exception is not None

    def test_getCleanedSplits_withEmptyString(self):
        original: str = ''
        result: List[str] = utils.getCleanedSplits(original)
        assert result is not None
        assert len(result) == 0

    def test_getCleanedSplits_withHelloWorld(self):
        original: str = 'Hello, World!'
        result: List[str] = utils.getCleanedSplits(original)
        assert result is not None
        assert len(result) == 2
        assert result[0] == 'Hello,'
        assert result[1] == 'World!'

    def test_getCleanedSplits_withNone(self):
        original: str = None
        result: List[str] = utils.getCleanedSplits(original)
        assert result is not None
        assert len(result) == 0

    def test_getCleanedSplits_withWhitespaceString(self):
        original: str = ' '
        result: List[str] = utils.getCleanedSplits(original)
        assert result is not None
        assert len(result) == 0

    def test_getFloatFromDict_withEmptyDict(self):
        d: Dict[str, Any] = dict()
        value: Optional[float] = None
        exception: Optional[Exception] = None

        try:
            value = utils.getFloatFromDict(d = d, key = "hello", fallback = 3.14)
        except Exception as e:
            exception = e

        assert value == 3.14
        assert exception is None

    def test_getFloatFromDict_withEmptyDictAndNoneFallback(self):
        d: Dict[str, Any] = dict()
        value: Optional[float] = None
        exception: Optional[Exception] = None

        try:
            value = utils.getFloatFromDict(d = d, key = "hello")
        except Exception as e:
            exception = e

        assert value is None
        assert exception is not None

    def test_getFloatFromDict_withNoneDict(self):
        d: Optional[Dict[str, Any]] = None
        value: Optional[float] = None
        exception: Optional[Exception] = None

        try:
            value = utils.getFloatFromDict(d = d, key = "hello", fallback = 1.1)
        except Exception as e:
            exception = e

        assert value == 1.1
        assert exception is None

    def test_getFloatFromDict_withNoneDictAndNoneFallback(self):
        d: Optional[Dict[str, Any]] = None
        value: Optional[float] = None
        exception: Optional[Exception] = None

        try:
            value = utils.getFloatFromDict(d = d, key = "hello")
        except Exception as e:
            exception = e

        assert value is None
        assert exception is not None

    def test_getIntFromDict_withEmptyDict(self):
        d: Dict[str, Any] = dict()
        value: Optional[int] = None
        exception: Optional[Exception] = None

        try:
            value = utils.getIntFromDict(d = d, key = "hello", fallback = 64)
        except Exception as e:
            exception = e

        assert value == 64
        assert exception is None

    def test_getIntFromDict_withEmptyDictAndNoneFallback(self):
        d: Dict[str, Any] = dict()
        value: Optional[int] = None
        exception: Optional[Exception] = None

        try:
            value = utils.getIntFromDict(d = d, key = "hello")
        except Exception as e:
            exception = e

        assert value is None
        assert exception is not None

    def test_getIntFromDict_withNoneDict(self):
        d: Optional[Dict[str, Any]] = None
        value: Optional[int] = None
        exception: Optional[Exception] = None

        try:
            value = utils.getIntFromDict(d = d, key = "hello", fallback = 2000)
        except Exception as e:
            exception = e

        assert value == 2000
        assert exception is None

    def test_getIntFromDict_withNoneDictAndNoneFallback(self):
        d: Optional[Dict[str, Any]] = None
        value: Optional[int] = None
        exception: Optional[Exception] = None

        try:
            value = utils.getIntFromDict(d = d, key = "hello")
        except Exception as e:
            exception = e

        assert value is None
        assert exception is not None

    def test_isValidBool_withFalse(self):
        result: bool = utils.isValidBool(False)
        assert result is True

    def test_isValidBool_withNone(self):
        result: bool = utils.isValidBool(None)
        assert result is False

    def test_isValidBool_withTrue(self):
        result: bool = utils.isValidBool(True)
        assert result is True

    def test_isValidInt_withNan(self):
        result: bool = utils.isValidInt(math.nan)
        assert result is False

    def test_isValidInt_withNegativeOne(self):
        result: bool = utils.isValidInt(-1)
        assert result is True

    def test_isValidInt_withNone(self):
        result: bool = utils.isValidInt(None)
        assert result is False

    def test_isValidInt_withOne(self):
        result: bool = utils.isValidInt(1)
        assert result is True

    def test_isValidInt_withPi(self):
        result: bool = utils.isValidInt(math.pi)
        assert result is False

    def test_isValidInt_withTwo(self):
        result: bool = utils.isValidInt(2)
        assert result is True

    def test_isValidInt_withZero(self):
        result: bool = utils.isValidInt(0)
        assert result is True

    def test_isValidNum_withFloat(self):
        result: bool = utils.isValidNum(3.33)
        assert result is True

    def test_isValidNum_withInt(self):
        result: bool = utils.isValidNum(100)
        assert result is True

    def test_isValidNum_withNan(self):
        result: bool = utils.isValidNum(math.nan)
        assert result is False

    def test_isValidNum_withNone(self):
        result: bool = utils.isValidNum(None)
        assert result is False

    def test_isValidNum_withPi(self):
        result: bool = utils.isValidNum(math.pi)
        assert result is True

    def test_isValidStr_withEmptyString(self):
        result: bool = utils.isValidStr('')
        assert result is False

    def test_isValidStr_withHelloWorldString(self):
        result: bool = utils.isValidStr('Hello, World!')
        assert result is True

    def test_isValidStr_withNewLineString(self):
        result: bool = utils.isValidStr('\n')
        assert result is False

    def test_isValidStr_withNone(self):
        result: bool = utils.isValidStr(None)
        assert result is False

    def test_isValidStr_withWhitespaceString(self):
        result: bool = utils.isValidStr(' ')
        assert result is False

    def test_isValidUrl_withEmptyString(self):
        result = utils.isValidUrl('')
        assert result is False

    def test_isValidUrl_withGoogle(self):
        result = utils.isValidUrl('https://www.google.com/')
        assert result is True

        result = utils.isValidUrl('http://google.com')
        assert result is True

        result = utils.isValidUrl('https://google.com:8080/')
        assert result is True

    def test_isValidUrl_withNone(self):
        result = utils.isValidUrl(None)
        assert result is False

    def test_isValidUrl_withRandomNoise1(self):
        result = utils.isValidUrl('J)R+ALY,m`g9r>lO`+RMeb$XL.OF8np')
        assert result is False

    def test_isValidUrl_withRandomNoise2(self):
        result = utils.isValidUrl('rpt\\\'%TmN$lx!T.Gg2le)QVO4\\_UqMA8dA{=\\\'\\\"')
        assert result is False

    def test_isValidUrl_withWhitespaceString(self):
        result = utils.isValidUrl(' ')
        assert result is False

    def test_numToBool_withInf(self):
        result: Optional[bool] = None
        exception: Optional[Exception] = None

        try:
            result = utils.numToBool(math.inf)
        except Exception as e:
            exception = e

        assert result is None
        assert exception is not None

    def test_numToBool_withNan(self):
        result: Optional[bool] = None
        exception: Optional[Exception] = None

        try:
            result = utils.numToBool(math.nan)
        except Exception as e:
            exception = e

        assert result is None
        assert exception is not None

    def test_numToBool_withNegativeOne(self):
        result = utils.numToBool(-1)
        assert result is True

    def test_numToBool_withNegativeTwo(self):
        result = utils.numToBool(-2)
        assert result is True

    def test_numToBool_withNone(self):
        result: Optional[bool] = None
        exception: Optional[Exception] = None

        try:
            result = utils.numToBool(None)
        except Exception as e:
            exception = e

        assert result is None
        assert exception is not None

    def test_numToBool_withOne(self):
        result = utils.numToBool(1)
        assert result is True

    def test_numToBool_withTen(self):
        result = utils.numToBool(10)
        assert result is True

    def test_numToBool_withTwo(self):
        result = utils.numToBool(2)
        assert result is True

    def test_numToBool_withZero(self):
        result = utils.numToBool(0)
        assert result is False

    def test_removePreceedingAt_withAtCharlesString(self):
        result = utils.removePreceedingAt('@charles')
        assert result == 'charles'

    def test_removePreceedingAt_withCharlesString(self):
        result = utils.removePreceedingAt('charles')
        assert result == 'charles'

    def test_removePreceedingAt_withEmptyString(self):
        result = utils.removePreceedingAt('')
        assert result == ''

    def test_removePreceedingAt_withNone(self):
        result = utils.removePreceedingAt(None)
        assert result is None

    def test_removePreceedingAt_withWhitespaceString(self):
        result = utils.removePreceedingAt(' ')
        assert result == ' '

    def test_splitLongStringIntoMessages_withEmptyMessage(self):
        result = utils.splitLongStringIntoMessages(
            maxMessages = 50,
            perMessageMaxSize = 50,
            message = ''
        )

        assert result is not None
        assert len(result) == 0

    def test_splitLongStringIntoMessages_withNoneMessage(self):
        result = utils.splitLongStringIntoMessages(
            maxMessages = 50,
            perMessageMaxSize = 50,
            message = None
        )

        assert result is not None
        assert len(result) == 0

    def test_splitLongStringIntoMessages_withOneSentences(self):
        result = utils.splitLongStringIntoMessages(
            maxMessages = 50,
            perMessageMaxSize = 50,
            message = 'Hello, World!'
        )

        assert result is not None
        assert len(result) == 1
        assert result[0] == 'Hello, World!'

    def test_splitLongStringIntoMessages_withThreeSentences(self):
        result = utils.splitLongStringIntoMessages(
            maxMessages = 50,
            perMessageMaxSize = 50,
            message = 'Hello, World! This is an example sentence. This should be broken up into smaller strings. This message is three strings!'
        )

        assert result is not None
        assert len(result) == 3
        assert result[0] == 'Hello, World! This is an example sentence. This'
        assert result[1] == 'should be broken up into smaller strings. This'
        assert result[2] == 'message is three strings!'

    def test_splitLongStringIntoMessages_withTwoSentences(self):
        result = utils.splitLongStringIntoMessages(
            maxMessages = 50,
            perMessageMaxSize = 50,
            message = 'Hello, World! This is an example sentence. This should be broken up into smaller strings.'
        )

        assert result is not None
        assert len(result) == 2
        assert result[0] == 'Hello, World! This is an example sentence. This'
        assert result[1] == 'should be broken up into smaller strings.'

    def test_strictStrToBool_withEmptyString(self):
        result: bool = None
        exception: Exception = None

        try:
            result = utils.strictStrToBool('')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, ValueError)

    def test_strictStrToBool_withF(self):
        result: bool = utils.strictStrToBool('f')
        assert result is False

    def test_strictStrToBool_withFalse(self):
        result: bool = utils.strictStrToBool('false')
        assert result is False

    def test_strictStrToBool_withNewLineString(self):
        result: bool = None
        exception: Exception = None

        try:
            result = utils.strictStrToBool('\n')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, ValueError)

    def test_strictStrToBool_withNone(self):
        result: bool = None
        exception: Exception = None

        try:
            result = utils.strictStrToBool(None)
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, ValueError)

    def test_strictStrToBool_withT(self):
        result: bool = utils.strictStrToBool('t')
        assert result is True

    def test_strictStrToBool_withTrue(self):
        result: bool = utils.strictStrToBool('true')
        assert result is True

    def test_strictStrToBool_withWhitespaceString(self):
        result: bool = None
        exception: Exception = None

        try:
            result = utils.strictStrToBool(' ')
        except Exception as e:
            exception = e

        assert result is None
        assert isinstance(exception, ValueError)

    def test_strToBool_withEmptyString(self):
        result: bool = utils.strToBool('')
        assert result is True

    def test_strToBool_withF(self):
        result: bool = utils.strToBool('f')
        assert result is False

    def test_strToBool_withFalse(self):
        result: bool = utils.strToBool('false')
        assert result is False

    def test_strToBool_withNewLineString(self):
        result: bool = utils.strToBool('\n')
        assert result is True

    def test_strToBool_withNone(self):
        result: bool = utils.strToBool(None)
        assert result is True

    def test_strToBool_withT(self):
        result: bool = utils.strToBool('t')
        assert result is True

    def test_strToBool_withTrue(self):
        result: bool = utils.strToBool('true')
        assert result is True

    def test_strToBool_withWhitespaceString(self):
        result: bool = utils.strToBool(' ')
        assert result is True
