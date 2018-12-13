#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Frog-themed weather station

This module renders frog-themed images that display time and local weather
information.

In order to generate an image, the module executes the following steps:
1. It retrieves the current time from the operating system.
2. It downloads the current local weather information, i.e. temperature and
   precipitation probability, from the Dark Sky weather server.
3. It creates an image that displays both the time and the weather information
   on top of a frog-themed background image that reflects the current weather.

Use this module as follows:
1. Add the key to the Dark Sky API to the file "darkskykey.yaml".
2. Specify the geographical coordinates of your location in the file
   "location.yaml".
3. In Python, import this module and call "frogweather.init()" to make it read
   the configuration files.
4. Use "frogweather.update()" to check if a new image is available.
5. Access the image via "frogweather.get_image()".
"""

# Check Python version.
import sys
version = sys.version_info[0]
if version != 2:
    raise Exception('Frogweather requires Python 2. '
        'You are using Python {}.'.format(version))

# Import standard modules.
import datetime
import logging
import os
import random
import time

# Import external modules.
import darksky
from PIL import Image, ImageDraw, ImageFont
import yaml


# Initialize global variables.
_apikey = None          # Dark Sky API key.
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

# Compute the minimum duration between two calls to the Dark Sky weather
# API in order not to exceed the daily limit.
_waittime = datetime.timedelta(days=1) / 1000

# Determine the package directory.
_pkgdir = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir))

# Determine the image directory.
_imagedir = os.path.join(_pkgdir, 'images')


def init():
    """Initialize frogweather module.

    Loads the Dark Sky API key, the user's geographical location, and the
    required fonts from file.
    """

    global _apikey, _loc, _fonts
    
    logging.info('Initializing frogweather module ...')

    # Read the key to the Dark Sky weather API from file.
    keyfile = os.path.join(_pkgdir, 'darkskykey.yaml')
    logging.info(
        'Reading Dark Sky API key from file \"{}\" ...'.format(keyfile))
    with open(keyfile, 'r') as file:
        _apikey = yaml.load(file.read())

        # Make sure the API key is non-empty.
        if not _apikey:
            raise ValueError('Key file \"{}\" is empty. '
                'Please provide a key to the Dark Sky weather API.'\
                    .format(keyfile))
    logging.info('Read Dark Sky API key \"{}\".'.format(_apikey))

    # Read the user's geographical location from file.
    locfile = os.path.join(_pkgdir, 'location.yaml')
    logging.info('Reading location from file \"{}\" ...'.format(locfile))
    with open(locfile, 'r') as file:
        _loc = yaml.load(file.read())
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
    time = datetime.datetime.now()
    if not _clockupdate or time.minute != _clockupdate.minute \
            or not _weatherupdate or time - _weatherupdate >= _waittime:
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
    clocktext = '{:>2d}:{:02d}'.format(_clockupdate.hour, _clockupdate.minute)
    draw.text((5, 7), clocktext, font=_fonts[0], fill=_fontcolor)
    
    # Draw the temperature.
    temptext = ''
    if _temp is None:
        logging.warning('Cannot display temperature: no information available.')
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
        logging.info('Searching images in directory \"{}\" ...'.format(descdir))
        if _temp:
            try:
                for file in os.listdir(descdir):
                    tempdir = os.path.join(descdir, file)
                    if os.path.isdir(tempdir):
                        temprange = [float(bound) for bound in file.split('_')]
                        if temprange[0] <= round(_temp) <= temprange[-1]:
                            imagefiles.extend([os.path.join(tempdir, file) \
                                for file in os.listdir(tempdir) \
                                if os.path.splitext(file)[-1].lower() \
                                    in _imageexts])
            except Exception as e:
                logging.warning(e)
        print(imagefiles)    
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
        

def _update_weather():
    """Download latest weather information from Dark Sky server.
    """

    global _weatherupdate, _temp, _desc, _precip

    logging.info('Updating weather information ...')

    # If the waiting time to the next call has not yet passed, do nothing.
    time = datetime.datetime.now()
    if _weatherupdate and time - _weatherupdate < _waittime:
        waittime = _waittime - (time - _weatherupdate)
        logging.info(
            'Cannot call weather API in order not to exceed daily limit. '
            'Time to next call {:.1f} s.'.format(waittime.total_seconds()))
        return
    
    _weatherupdate = time
    _temp = None
    _precip = None
    _desc = None

    # Get the current weather.
    logging.info('Downloading weather information from server ...')
    try:
        with darksky.forecast(
                key=_apikey,
                latitude=_loc['lat'],
                longitude=_loc['lon'],
                timeout=10,
                units='si') as forecast:
            # Determine the current temperature and weather description.
            _temp = forecast.currently.temperature
            _desc = forecast.icon

            # Determine the precipitation probability for the next couple of
            # hours.
            dry = 1.0
            for hour in forecast.hourly[1:9]:
                dry *= 1.0 - hour.precipProbability
            _precip = 1.0 - dry
            
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

    # Import required module.
    import duallog
    import pygame

    # Set up logging.
    duallog.setup('log')

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
