import json
import random
from json.decoder import JSONDecodeError
from os import path

import requests
from google.cloud import translate_v2 as translate
from requests import ConnectionError, HTTPError, Timeout
from requests.exceptions import ReadTimeout, TooManyRedirects
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.language.languageEntry import LanguageEntry
    from CynanBotCommon.language.languagesRepository import LanguagesRepository
    from CynanBotCommon.language.translationApiSource import \
        TranslationApiSource
except:
    import utils

    from language.languageEntry import LanguageEntry
    from language.languagesRepository import LanguagesRepository
    from language.translationApiSource import TranslationApiSource


class TranslationResponse():

    def __init__(
        self,
        originalLanguage: LanguageEntry,
        translatedLanguage: LanguageEntry,
        originalText: str,
        translatedText: str,
        translationApiSource: TranslationApiSource
    ):
        if originalLanguage is not None and not originalLanguage.hasIso6391Code():
            raise ValueError(f'originalLanguage argument must be either None or have an ISO 639-1 code: \"{originalLanguage}\"')
        elif translatedLanguage is not None and not translatedLanguage.hasIso6391Code():
            raise ValueError(f'translatedLanguage argument must be either None or have an ISO 639-1 code: \"{translatedLanguage}\"')
        elif not utils.isValidStr(originalText):
            raise ValueError(f'originalText argument is malformed: \"{originalText}\"')
        elif not utils.isValidStr(translatedText):
            raise ValueError(f'translatedText argument is malformed: \"{translatedText}\"')
        elif translationApiSource is None:
            raise ValueError(f'translationApiSource argument is malformed: \"{translationApiSource}\"')

        self.__originalLanguage: LanguageEntry = originalLanguage
        self.__translatedLanguage: LanguageEntry = translatedLanguage
        self.__originalText: str = originalText
        self.__translatedText: str = translatedText
        self.__translationApiSource: TranslationApiSource = translationApiSource

    def getOriginalLanguage(self) -> LanguageEntry:
        return self.__originalLanguage

    def getOriginalText(self) -> str:
        return self.__originalText

    def getTranslatedLanguage(self) -> LanguageEntry:
        return self.__translatedLanguage

    def getTranslatedText(self) -> str:
        return self.__translatedText

    def getTranslationApiSource(self) -> TranslationApiSource:
        return self.__translationApiSource

    def hasOriginalLanguage(self) -> bool:
        return self.__originalLanguage is not None

    def hasTranslatedLanguage(self) -> bool:
        return self.__translatedLanguage is not None

    def toStr(self) -> str:
        prefixText = ''

        if self.hasOriginalLanguage():
            if self.hasTranslatedLanguage():
                firstLangText = ''
                if self.__originalLanguage.hasFlag():
                    firstLangText = self.__originalLanguage.getFlag()
                else:
                    firstLangText = self.__originalLanguage.getIso6391Code().upper()

                secondLangText = ''
                if self.__translatedLanguage.hasFlag():
                    secondLangText = self.__translatedLanguage.getFlag()
                else:
                    secondLangText = self.__translatedLanguage.getIso6391Code().upper()

                prefixText = f'[ {firstLangText} ➡ {secondLangText} ] '
            elif self.__originalLanguage.hasFlag():
                prefixText = f'[ {self.__originalLanguage.getFlag()} ]'
            else:
                prefixText = f'[ {self.__originalLanguage.getIso6391Code().upper()} ]'

        return f'{prefixText}{self.__translatedText}'


class TranslationHelper():

    def __init__(
        self,
        languagesRepository: LanguagesRepository,
        deepLAuthKey: str,
        googleServiceAccountFile: str = 'CynanBotCommon/googleServiceAccount.json'
    ):
        if languagesRepository is None:
            raise ValueError(f'languagesRepository argument is malformed: \"{languagesRepository}\"')
        elif not utils.isValidStr(deepLAuthKey):
            raise ValueError(f'deepLAuthKey argument is malformed: \"{deepLAuthKey}\"')
        elif not utils.isValidStr(googleServiceAccountFile):
            raise ValueError(f'googleServiceAccountFile argument is malformed: \"{googleServiceAccountFile}\"')

        self.__languagesRepository: LanguagesRepository = languagesRepository
        self.__deepLAuthKey: str = deepLAuthKey
        self.__googleServiceAccountFile: str = googleServiceAccountFile
        self.__googleTranslateClient = None

    def __deepLTranslate(self, text: str, targetLanguageEntry: LanguageEntry) -> TranslationResponse:
        print(f'Fetching translation from DeepL... ({utils.getNowTimeText()})')

        # Retrieve translation from DeepL API: https://www.deepl.com/en/docs-api/

        requestUrl = 'https://api-free.deepl.com/v2/translate?auth_key={}&text={}&target_lang={}'.format(
            self.__deepLAuthKey, text, targetLanguageEntry.getIso6391Code())

        rawResponse = None
        try:
            rawResponse = requests.get(url = requestUrl, timeout = utils.getDefaultTimeout())
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            print(f'Exception occurred when attempting to fetch translation from DeepL for \"{text}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to fetch translation from DeepL for \"{text}\": {e}')

        jsonResponse = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            print(f'Exception occurred when attempting to decode DeepL\'s response for \"{text}\" into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode DeepL\'s response for \"{text}\" into JSON: {e}')

        translationsJson = jsonResponse.get('translations')
        if not utils.hasItems(translationsJson):
            raise RuntimeError(f'DeepL\'s JSON response for \"{text}\" has missing or empty \"translations\" field: {jsonResponse}')

        translationJson = translationsJson[0]

        originalLanguage: LanguageEntry = None
        detectedSourceLanguage = translationJson.get('detected_source_language')
        if utils.isValidStr(detectedSourceLanguage):
            originalLanguage = self.__languagesRepository.getLanguageForCommand(detectedSourceLanguage, hasIso6391Code = True)

        return TranslationResponse(
            originalLanguage = originalLanguage,
            translatedLanguage = targetLanguageEntry,
            originalText = text,
            translatedText = utils.getStrFromDict(translationJson, 'text', clean = True, htmlUnescape = True),
            translationApiSource = TranslationApiSource.DEEP_L
        )

    def __getGoogleTranslateClient(self):
        if self.__googleTranslateClient is None:
            print(f'Initializing new Google translate.Client instance... ({utils.getNowTimeText()})')

            if not self.__hasGoogleApiCredentials():
                raise RuntimeError(f'Unable to initialize a new Google translate.Client instance because the Google API credentials are missing')
            elif not path.exists(self.__googleServiceAccountFile):
                raise FileNotFoundError(f'googleServiceAccount file not found: \"{self.__googleServiceAccountFile}\"')

            self.__googleTranslateClient = translate.Client.from_service_account_json(self.__googleServiceAccountFile)

        return self.__googleTranslateClient

    def __googleTranslate(self, text: str, targetLanguageEntry: LanguageEntry) -> TranslationResponse:
        print(f'Fetching translation from Google Translate... ({utils.getNowTimeText()})')

        translationResult = self.__getGoogleTranslateClient().translate(
            text,
            target_language = targetLanguageEntry.getIso6391Code()
        )

        if not utils.hasItems(translationResult):
            raise RuntimeError(f'error in the data response when attempting to translate \"{text}\": {translationResult}')

        originalText = translationResult.get('input')
        if not utils.isValidStr(originalText):
            raise RuntimeError(f'\"input\" field is missing or malformed from translation result for \"{text}\": {translationResult}')

        translatedText = translationResult.get('translatedText')
        if not utils.isValidStr(translatedText):
            raise RuntimeError(f'\"translatedText\" field is missing or malformed from translation result for \"{text}\": {translationResult}')

        originalLanguage: LanguageEntry = None
        detectedSourceLanguage = translationResult.get('detectedSourceLanguage')
        if utils.isValidStr(detectedSourceLanguage):
            originalLanguage = self.__languagesRepository.getLanguageForCommand(detectedSourceLanguage, hasIso6391Code = True)

        return TranslationResponse(
            originalLanguage = originalLanguage,
            translatedLanguage = targetLanguageEntry,
            originalText = originalText,
            translatedText = utils.cleanStr(translatedText, htmlUnescape = True),
            translationApiSource = TranslationApiSource.GOOGLE_TRANSLATE
        )

    def __hasGoogleApiCredentials(self) -> bool:
        if not path.exists(self.__googleServiceAccountFile):
            return False

        with open(self.__googleServiceAccountFile, 'r') as file:
            jsonContents = json.load(file)

        return utils.hasItems(jsonContents)

    def translate(
        self,
        text: str,
        targetLanguageEntry: LanguageEntry = None
    ) -> TranslationResponse:
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = utils.cleanStr(text)

        if targetLanguageEntry is not None and not targetLanguageEntry.hasIso6391Code():
            raise ValueError(f'the given LanguageEntry is not supported for translation: \"{targetLanguageEntry.getName()}\"')
        elif targetLanguageEntry is None:
            targetLanguageEntry = self.__languagesRepository.requireLanguageForCommand('en', hasIso6391Code = True)

        if self.__googleTranslateClient is None and not self.__hasGoogleApiCredentials():
            # This isn't an optimal situation, but it means that we're currently running in a
            # situation where we have no Google API credentials, but we do have DeepL credentials.
            # So here we'll just always use DeepL for translation, rather than evenly splitting
            # the workload between both services.
            return self.__deepLTranslate(text, targetLanguageEntry)

        # In order to help keep us from running beyond the free usage tiers for the Google
        # Translate and DeepL translation services, let's randomly choose which translation service
        # to use. At the time of this writing, both services have a 500,000 character monthly limit.
        # So theoretically, this gives us a 1,000,000 character translation capability.

        translationApiSource = random.choice(list(TranslationApiSource))

        if translationApiSource is TranslationApiSource.DEEP_L:
            return self.__deepLTranslate(text, targetLanguageEntry)
        elif translationApiSource is TranslationApiSource.GOOGLE_TRANSLATE:
            return self.__googleTranslate(text, targetLanguageEntry)
        else:
            raise ValueError(f'unknown TranslationApiSource: \"{translationApiSource}\"')
