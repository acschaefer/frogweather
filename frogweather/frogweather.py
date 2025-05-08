#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Frog-themed weather station

This module renders frog-themed images that display time and local weather
information.

In order to generate an image, the module executes the following steps:
1. It retrieves the current time from the operating system.
2. It downloads the current local weather information, i.e. temperature and
   precipitation probability, from the Weather API server.
3. It creates an image that displays both the time and the weather information
   on top of a frog-themed background image that reflects the current weather.

Use this module as follows:
1. Add the key to the Weather API to the file "apikey.yaml".
2. Specify the geographical coordinates of your location in the file
   "location.yaml".
3. In Python, import this module and call "frogweather.init()" to make it read
   the configuration files.
4. Use "frogweather.update()" to check if a new image is available.
5. Access the image via "frogweather.get_image()".
"""

import yaml
import requests
from PIL import Image, ImageDraw, ImageFont
import time
import random
import os
import logging
import datetime
import sys

# Check Python version.
version = sys.version_info[0]
if not 2 <= version <= 3:
    raise Exception('Frogweather requires Python 2 or 3. '
                    'You are using Python {}.'.format(version))

# Initialize global variables.
_apikey = None          # API key.
_session = None         # HTTP session used for querying the weather server.
_loc = None             # Geographical location of the user.
_fonts = []             # Fonts for drawing time and weather information.
_weatherupdate = None   # Time of last weather update.
_clockupdate = None     # Time of last clock update.
_temp = None            # Current temperature.
_precip = None          # Current precipitation probability.
_desc = None            # Current weather description.
_image = None           # Current weather station image.
_background = None      # Background image.
_backgroundfile = None  # Background image file name.

# Define the supported image file extensions.
_imageexts = ['.png', '.bmp', '.jpg', '.jpeg']

# Define the font color in RGBA.
_fontcolor = (250, 250, 250, 255)

# Compute the minimum duration between two calls to
# Weather API in order not to exceed the monthly limit.
_waittime = max(datetime.timedelta(seconds=10),
                datetime.timedelta(days=31) / 1000000)

# Determine the package directory.
_pkgdir = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir))

# Determine the image directory.
_imagedir = os.path.join(_pkgdir, 'images')


def init():
    """Initialize frogweather module.

    Loads the API key, the user's geographical location, and the
    required fonts from file.
    """

    global _apikey, _session, _loc, _fonts

    logging.info('Initializing frogweather module ...')

    # Read the key to Weather API from file.
    keyfile = os.path.join(_pkgdir, 'apikey.yaml')
    logging.info(
        'Reading Weather API key from file \"{}\" ...'.format(keyfile))
    with open(keyfile, 'r') as file:
        _apikey = yaml.safe_load(file.read())

        # Make sure the API key is non-empty.
        if not _apikey:
            raise ValueError('Key file \"{}\" is empty. '
                             'Please provide a key to Weather API.'
                             .format(keyfile))
    logging.info('Read Weather API key \"{}\".'.format(_apikey))

    # Open the HTTP session.
    _session = requests.Session()

    # Read the user's geographical location from file.
    locfile = os.path.join(_pkgdir, 'location.yaml')
    logging.info('Reading location from file \"{}\" ...'.format(locfile))
    with open(locfile, 'r') as file:
        _loc = yaml.safe_load(file.read())
    logging.info('Read location coordinate: {} N {} W.'.format(
        _loc['lat'], _loc['lon']))

    # Load the fonts.
    fonts = [('SourceCodePro-Bold.otf', 18), ('SourceCodePro-Regular.otf', 12)]
    for font in fonts:
        fontfile = os.path.join(_pkgdir, 'fonts', font[0])
        logging.info('Loading font from file \"{}\" ...'.format(fontfile))
        _fonts.append(ImageFont.truetype(font=fontfile, size=font[1]))
        logging.info('Font loaded.')

    logging.info('Module initialized.')


def update():
    """Updates the weather station image, if required.

    Returns:
        True if the image was updated, False otherwise.
    """

    # If the weather station image is outdated, update it.
    now = datetime.datetime.now()
    if not _clockupdate or now.minute != _clockupdate.minute \
            or not _weatherupdate or now - _weatherupdate >= _waittime:
        _render_image()
        return True
    else:
        return False


def get_image():
    """Get latest weather station image.

    Returns:
        PIL Image.
    """

    return _image


def _render_image():
    """Render weather station image.

    Renders a 64x128 image that displays the current time, temperature, and
    precipitation probability within the next hours along with a frog-themed
    weather illustration in the background.
    """

    global _image, _clockupdate

    logging.info('Rendering image ...')

    # Make sure the background image is up to date.
    _update_background()

    # Draw the clock.
    _image = _background.copy()
    draw = ImageDraw.Draw(_image)
    draw.fontmode = '1'  # Turn anti-aliasing off.
    _clockupdate = datetime.datetime.now()
    clocktext = '{:>5}'.format(_clockupdate.strftime('%I:%M'))
    clocktext = clocktext.replace('0', ' ', int(clocktext[0] == '0'))
    draw.text((5, 7), clocktext, font=_fonts[0], fill=_fontcolor)

    # Draw the temperature.
    temptext = ''
    if _temp is None:
        logging.warning(
            'Cannot display temperature: no information available.')
    else:
        temptext = u'{:> 3.0f}°'.format(_temp)
    draw.text((4, 28), temptext, font=_fonts[1], fill=_fontcolor)

    # Draw the precipitation probability.
    preciptext = ''
    if _precip is None:
        logging.warning('Cannot display precipitation probability: '
                        'no information available.')
    else:
        preciptext = '{:>4.0%}'.format(min(_precip, 0.99))
    draw.text((32, 28), preciptext, font=_fonts[1], fill=_fontcolor)

    logging.info('Image rendered.')


def _update_background():
    """Load background image corresponding to current weather.
    """

    global _background, _backgroundfile

    logging.info('Loading background image ...')

    # Make sure the weather information is up to date.
    _update_weather()

    # Get all images that correspond to both the current weather description and
    # the current temperature.
    imagefiles = []
    if _desc:
        descdir = os.path.join(_imagedir, _desc)
        logging.info(
            'Searching images in directory \"{}\" ...'.format(descdir))
        if _temp:
            try:
                for file in os.listdir(descdir):
                    tempdir = os.path.join(descdir, file)
                    if os.path.isdir(tempdir):
                        temprange = [float(bound) for bound in file.split('_')]
                        if temprange[0] <= round(_temp) <= temprange[-1]:
                            imagefiles.extend([os.path.join(tempdir, file)
                                               for file in os.listdir(tempdir)
                                               if os.path.splitext(file)[-1].lower()
                                               in _imageexts])
            except Exception as e:
                logging.warning(e)

        # If no image corresponds to the current temperature, search for default
        # images that correspond to the current weather description.
        if not imagefiles:
            try:
                for file in os.listdir(descdir):
                    descfile = os.path.join(descdir, file)
                    if os.path.isfile(descfile):
                        ext = os.path.splitext(descfile)[-1].lower()
                        if ext in _imageexts:
                            imagefiles.append(descfile)
            except Exception as e:
                logging.warning(e)
        logging.info('Found {} image(s).'.format(len(imagefiles)))

    # If no image corresponds to the current weather description, search for
    # default images.
    if not imagefiles:
        logging.info('Searching images in directory \"{}\" ...'.format(
            _imagedir))
        try:
            for file in os.listdir(_imagedir):
                filepath = os.path.join(_imagedir, file)
                if os.path.isfile(filepath) \
                        and os.path.splitext(file)[-1].lower() in _imageexts:
                    imagefiles.append(filepath)
        except Exception as e:
            logging.warning(e)
        logging.info('Found {} image(s).'.format(len(imagefiles)))

    # If the image currently on display is among the retrieved images, do
    # nothing. Otherwise, randomly select one of the images found. If none was
    # found, create a monochrome image.
    if _backgroundfile in imagefiles:
        logging.info('No background image update: last image still valid.')
    else:
        if imagefiles:
            _backgroundfile = imagefiles[random.randint(0, len(imagefiles)-1)]
            _background = Image.open(_backgroundfile)
            logging.info('Selected image: \"{}\".'.format(_backgroundfile))
        else:
            # If no default image is available, generate a monochrome image.
            logging.info('Creating fallback background image ...')
            _background = Image.new('RGB', (64, 128), color='blue')
            _backgroundfile = None

    logging.info('Background image loaded.')


def response_to_desc(response):
    """Extract a description of the current weather from the Weather API repsonse dictionary.
    """
    return {
        "Sunny": "clear-day",
        "Clear": "clear-day" if response["current"]["is_day"] else "clear-night",
        "Partly cloudy": "partly-cloudy-day" if response["current"]["is_day"] else "partly-cloudy-night",
        "Cloudy": "cloudy",
        "Overcast": "cloudy",
        "Mist": "fog",
        "Patchy rain possible": "rain",
        "Patchy snow possible": "snow",
        "Patchy sleet possible": "sleet",
        "Patchy freezing drizzle possible": "sleet",
        "Thundery outbreaks possible": "thunderstorm",
        "Blowing snow": "snow",
        "Blizzard": "snow",
        "Fog": "fog",
        "Freezing fog": "fog",
        "Patchy light drizzle": "rain",
        "Light drizzle": "rain",
        "Freezing drizzle": "sleet",
        "Heavy freezing drizzle": "sleet",
        "Patchy light rain": "rain",
        "Light rain": "rain",
        "Moderate rain at times": "rain",
        "Moderate rain": "rain",
        "Heavy rain at times": "rain",
        "Heavy rain": "rain",
        "Light freezing rain": "sleet",
        "Moderate or heavy freezing rain": "sleet",
        "Light sleet": "sleet",
        "Moderate or heavy sleet": "sleet",
        "Patchy light snow": "snow",
        "Light snow": "snow",
        "Patchy moderate snow": "snow",
        "Moderate snow": "snow",
        "Patchy heavy snow": "snow",
        "Heavy snow": "snow",
        "Ice pellets": "sleet",
        "Light rain shower": "rain",
        "Moderate or heavy rain shower": "rain",
        "Torrential rain shower": "thunderstorm",
        "Light sleet showers": "sleet",
        "Moderate or heavy sleet showers": "sleet",
        "Light snow showers": "snow",
        "Moderate or heavy snow showers": "snow",
        "Light showers of ice pellets": "sleet",
        "Moderate or heavy showers of ice pellets": "sleet",
        "Patchy light rain with thunder": "thunderstorm",
        "Moderate or heavy rain with thunder": "thunderstorm",
        "Patchy light snow with thunder": "snow",
        "Moderate or heavy snow with thunder": "snow",
    }[response["current"]["condition"]["text"]]


def _update_weather():
    """Download latest weather information from Weather API server.
    """

    global _weatherupdate, _temp, _desc, _precip

    logging.info('Updating weather information ...')

    # If the waiting time to the next call has not yet passed, do nothing.
    now = datetime.datetime.now()
    if _weatherupdate and now - _weatherupdate < _waittime:
        waittime = _waittime - (now - _weatherupdate)
        logging.info(
            'Cannot call Weather API in order not to exceed monthly limit. '
            'Time to next call {:.1f} s.'.format(waittime.total_seconds()))
        return

    # Reset weather information.
    _weatherupdate = now
    _temp = None
    _precip = None
    _desc = None

    # If today is a special date, update the description accordingly.
    if _weatherupdate.month == 1 and _weatherupdate.day == 1:
        _desc = 'new-years-day'
    elif now.month == 12 and now.day == 31:
        _desc = 'new-years-eve'

    # Get the current weather.
    logging.info('Downloading weather information from server ...')
    try:
        response = _session.get("https://api.weatherapi.com/v1/forecast.json", params={
            "key": _apikey,
            "q": "{},{}".format(_loc['lat'], _loc['lon']),  # Location.
            "days": 2,                                      # Forecast horizon.
            "aqi": "no",                                    # Air quality data.
            "alerts": "no"}                                 # Weather alerts.
        ).json()
        _temp = response["current"]["temp_c"]
        if _desc is None:
            _desc = response_to_desc(response)

        # Determine the precipitation probability for the next couple of
        # hours.
        pp_rain = [forecast_hour["chance_of_rain"] * 0.01
                   for forecast_day in response["forecast"]["forecastday"]
                   for forecast_hour in forecast_day["hour"]]
        p_dry = 1.0
        for p_rain in pp_rain[now.hour:now.hour+3]:
            p_dry *= 1.0 - p_rain
        _precip = 1.0 - p_dry

        logging.info(
            'Successfully retrieved weather information: '
            'description: {}, temperatue: {:.1f}°C, '
            'precipitation: {:.0%}.'.format(_desc, _temp, _precip))
    except Exception as e:
        logging.error('Failed to retrieve weather information: {}.'.format(e))

    logging.info('Weather information updated.')


if __name__ == '__main__':
    """Display and continuously update weather station image on screen.
    """

    # Import required packages.
    import pygame

    # Define the size of the weather station window.
    screensize = (240, 480)

    # Start the pygame engine and create a window.
    pygame.init()
    pygame.display.set_caption('Frogweather')
    screen = pygame.display.set_mode(screensize)

    # Initialize the weather station.
    init()

    # Start the game loop.
    while True:
        # Process game events.
        for event in pygame.event.get():
            # Exit game.
            if event.type == pygame.QUIT \
                    or (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

        # Update the image rendered by the weather station.
        if update():
            # Convert the returned PIL image to a pygame image.
            image = get_image().resize(screensize)
            data = image.tobytes()
            size = image.size
            mode = image.mode
            image = pygame.image.fromstring(data, size, mode)

            # Load the pygame image into the output window and refresh it.
            screen.blit(image, (0, 0))
            pygame.display.flip()

        time.sleep(0.1)
