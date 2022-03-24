from datetime import timedelta
from json.decoder import JSONDecodeError
from typing import Dict, List

import requests
from requests import ConnectionError, HTTPError, Timeout
from requests.exceptions import ReadTimeout, TooManyRedirects
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.location.location import Location
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.timedDict import TimedDict
    from CynanBotCommon.weather.airQualityIndex import AirQualityIndex
    from CynanBotCommon.weather.uvIndex import UvIndex
    from CynanBotCommon.weather.weatherReport import WeatherReport
except:
    import utils
    from location.location import Location
    from timber.timber import Timber
    from timedDict import TimedDict

    from weather.airQualityIndex import AirQualityIndex
    from weather.uvIndex import UvIndex
    from weather.weatherReport import WeatherReport


class WeatherRepository():

    def __init__(
        self,
        oneWeatherApiKey: str,
        timber: Timber,
        maxAlerts: int = 2,
        cacheTimeDelta: timedelta = timedelta(minutes = 20)
    ):
        if not utils.isValidStr(oneWeatherApiKey):
            raise ValueError(f'oneWeatherApiKey argument is malformed: \"{oneWeatherApiKey}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidNum(maxAlerts):
            raise ValueError(f'maxAlerts argument is malformed: \"{maxAlerts}\"')
        elif maxAlerts < 1:
            raise ValueError(f'maxAlerts argument is out of bounds: {maxAlerts}')
        elif cacheTimeDelta is None:
            raise ValueError(f'cacheTimeDelta argument is malformed: \"{cacheTimeDelta}\"')

        self.__oneWeatherApiKey: str = oneWeatherApiKey
        self.__timber: Timber = timber
        self.__maxAlerts: int = maxAlerts
        self.__cache = TimedDict(timeDelta = cacheTimeDelta)
        self.__conditionIcons: Dict[str, str] = self.__createConditionIconsDict()

    def __chooseTomorrowFromForecast(self, jsonResponse: Dict) -> Dict[str, object]:
        currentSunrise = jsonResponse['current']['sunrise']
        currentSunset = jsonResponse['current']['sunset']

        for dayJson in jsonResponse['daily']:
            if dayJson['sunrise'] > currentSunrise and dayJson['sunset'] > currentSunset:
                return dayJson

        raise RuntimeError(f'Unable to find viable tomorrow data in JSON response: \"{jsonResponse}\"')

    def __createConditionIconsDict(self) -> Dict[str, str]:
        # This dictionary is built from the Weather Condition Codes listed here:
        # https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2

        icons: Dict[str, str] = dict()
        icons['200'] = '⛈️'
        icons['201'] = icons['200']
        icons['202'] = icons['200']
        icons['210'] = '🌩️'
        icons['211'] = icons['210']
        icons['212'] = icons['211']
        icons['221'] = icons['200']
        icons['230'] = icons['200']
        icons['231'] = icons['200']
        icons['232'] = icons['200']
        icons['300'] = '☔'
        icons['301'] = icons['300']
        icons['310'] = icons['300']
        icons['311'] = icons['300']
        icons['313'] = icons['300']
        icons['500'] = icons['300']
        icons['501'] = '🌧️'
        icons['502'] = icons['501']
        icons['503'] = icons['501']
        icons['504'] = icons['501']
        icons['520'] = icons['501']
        icons['521'] = icons['501']
        icons['522'] = icons['501']
        icons['531'] = icons['501']
        icons['600'] = '❄️'
        icons['601'] = icons['600']
        icons['602'] = '🌨️'
        icons['711'] = '🌫️'
        icons['721'] = icons['711']
        icons['731'] = icons['711']
        icons['741'] = icons['711']
        icons['762'] = '🌋'
        icons['771'] = '🌬'
        icons['781'] = '🌪️'
        icons['801'] = '☁️'
        icons['802'] = icons['801']
        icons['803'] = icons['801']
        icons['804'] = icons['801']

        return icons

    def __fetchAirQualityIndex(self, location: Location) -> AirQualityIndex:
        if location is None:
            raise ValueError(f'location argument is malformed: \"{location}\"')

        # Retrieve air quality index from: https://openweathermap.org/api/air-pollution
        # Doing this requires an API key, which you can get here: https://openweathermap.org/api

        requestUrl = 'https://api.openweathermap.org/data/2.5/air_pollution?appid={}&lat={}&lon={}'.format(
            self.__oneWeatherApiKey, location.getLatitude(), location.getLongitude())

        rawResponse = None
        try:
            rawResponse = requests.get(url = requestUrl, timeout = utils.getDefaultTimeout())
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            self.__timber.log('WeatherRepository', f'Exception occurred when attempting to fetch air quality index from Open Weather for \"{location.getLocationId()}\" ({location.getName()}): {e}')
            raise RuntimeError(f'Exception occurred when attempting to fetch air quality index from Open Weather for \"{location.getLocationId()}\" ({location.getName()}): {e}')

        jsonResponse: Dict[str, object] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            self.__timber.log('WeatherRepository', f'Exception occurred when attempting to decode Open Weather\'s air quality index response into JSON for \"{location.getLocationId()}\" ({location.getName()}): {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Open Weather\'s air quality index response into JSON for \"{location.getLocationId()}\" ({location.getName()}): {e}')

        airQualityIndex = utils.getIntFromDict(
            d = jsonResponse['list'][0]['main'],
            key = 'aqi'
        )

        return AirQualityIndex.fromInt(airQualityIndex)

    def fetchWeather(self, location: Location) -> WeatherReport:
        if location is None:
            raise ValueError(f'location argument is malformed: \"{location}\"')

        cacheValue = self.__cache[location.getLocationId()]
        if cacheValue is not None:
            return cacheValue

        weatherReport = self.__fetchWeather(location)
        self.__cache[location.getLocationId()] = weatherReport

        return weatherReport

    def __fetchWeather(self, location: Location) -> WeatherReport:
        if location is None:
            raise ValueError(f'location argument is malformed: \"{location}\"')

        self.__timber.log('WeatherRepository', f'Fetching weather for \"{location.getName()}\" ({location.getLocationId()})...')

        # Retrieve weather report from https://openweathermap.org/api/one-call-api
        # Doing this requires an API key, which you can get here: https://openweathermap.org/api

        requestUrl = 'https://api.openweathermap.org/data/2.5/onecall?appid={}&lat={}&lon={}&exclude=minutely,hourly&units=metric'.format(
            self.__oneWeatherApiKey, location.getLatitude(), location.getLongitude())

        rawResponse = None
        try:
            rawResponse = requests.get(url = requestUrl, timeout = utils.getDefaultTimeout())
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            self.__timber.log('WeatherRepository', f'Exception occurred when attempting to fetch weather conditions from Open Weather for \"{location.getLocationId()}\" ({location.getName()}): {e}')
            raise RuntimeError(f'Exception occurred when attempting to fetch weather conditions from Open Weather for \"{location.getLocationId()}\" ({location.getName()}): {e}')

        jsonResponse: Dict[str, object] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            self.__timber.log('WeatherRepository', f'Exception occurred when attempting to decode Open Weather\'s weather response into JSON for \"{location.getLocationId()}\" ({location.getName()}): {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Open Weather\'s weather response into JSON for \"{location.getLocationId()}\" ({location.getName()}): {e}')

        currentJson: Dict[str, object] = jsonResponse['current']
        humidity = int(round(utils.getFloatFromDict(currentJson, 'humidity')))
        pressure = int(round(utils.getFloatFromDict(currentJson, 'pressure')))
        temperature = utils.getFloatFromDict(currentJson, 'temp')
        uvIndex = UvIndex.fromFloat(utils.getFloatFromDict(currentJson, 'uvi'))

        conditions: List[str] = list()
        if 'weather' in currentJson and len(currentJson['weather']) >= 1:
            for conditionJson in currentJson['weather']:
                conditions.append(self.__prettifyCondition(conditionJson))

        alerts: List[str] = list()
        if 'alerts' in jsonResponse and len(jsonResponse['alerts']) >= 1:
            for alertJson in jsonResponse['alerts']:
                event = alertJson.get('event')
                senderName = alertJson.get('sender_name')

                if event is not None and len(event) >= 1:
                    if senderName is None or len(senderName) == 0:
                        alerts.append(f'Alert: {event}.')
                    else:
                        alerts.append(f'Alert from {senderName}: {event}.')

                    if len(alerts) >= self.__maxAlerts:
                        break

        tomorrowsJson = self.__chooseTomorrowFromForecast(jsonResponse)
        tomorrowsHighTemperature = utils.getFloatFromDict(tomorrowsJson['temp'], 'max')
        tomorrowsLowTemperature = utils.getFloatFromDict(tomorrowsJson['temp'], 'min')

        tomorrowsConditions: List[str] = list()
        if 'weather' in tomorrowsJson and len(tomorrowsJson['weather']) >= 1:
            for conditionJson in tomorrowsJson['weather']:
                tomorrowsConditions.append(conditionJson['description'])

        return WeatherReport(
            airQualityIndex = self.__fetchAirQualityIndex(location),
            temperature = temperature,
            tomorrowsHighTemperature = tomorrowsHighTemperature,
            tomorrowsLowTemperature = tomorrowsLowTemperature,
            humidity = humidity,
            pressure = pressure,
            alerts = alerts,
            conditions = conditions,
            tomorrowsConditions = tomorrowsConditions,
            uvIndex = uvIndex
        )

    def __prettifyCondition(self, conditionJson: Dict) -> str:
        conditionIcon = ''
        if 'id' in conditionJson:
            conditionId = utils.getStrFromDict(conditionJson, 'id')

            if conditionId in self.__conditionIcons:
                icon = self.__conditionIcons[conditionId]
                conditionIcon = f'{icon} '

        conditionDescription = utils.getStrFromDict(conditionJson, 'description')
        return f'{conditionIcon}{conditionDescription}'
