#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Frog-themed weather station

This module contains the class WeatherStation, which periodically generates
frog-themed weather station images, calls a user-defined callback function, and
passes the image to it. 

More specifically, WeatherStation periodically executes the following steps:
1. It requests the current time from the operating system.
2. It downloads the current weather information, i.e. temperature and
   precipitation probability, from the Dark Sky weather server.
3. It creates an image that displays both the time and the weather information
   on top of a frog-themed background image that reflects the current weather.
4. It calls the user-defined callback function, which processes the image.

In order to use this module, create a WeatherStation object by passing the
callback function to it. See the bottom of this file for examplary usage.
"""


# Import standard libraries.
import datetime
import logging
import os
import time
import random

# Import external libraries.
import darksky
import yaml
from PIL import Image, ImageDraw, ImageFont


class WeatherStation:
    """Contains all functionality to render weather station images.
    """

    def __init__(self, callback=lambda image: image.show()):
        """Constructor.

        Loads the Dark Sky API key and the user's geographical location from
        file, and starts the update process of the clock and the weather
        information.
        """

        # Initialize member variables.
        self._callback = callback
        self._fontcolor = (250, 250, 250, 255)
        self._update = None     # Time of last weather information update.
        self._time = None       # Current time.
        self._temp = None       # Current temperature.
        self._precip = None     # Current precipitation probability.
        self._icon = None       # Weather station image description.
        self._image = None      # Weather station background image.
        self._imagefile = None  # Weather station background image file name.
        self._loc = None        # User location.

        # Determine the directory where all code and all resources reside.
        self._maindir = os.path.normpath(os.path.join(
            os.path.dirname(os.path.abspath(__file__)), os.pardir))

        # Read the key to the Dark Sky weather API from the respective file.
        keyfile = os.path.join(self._maindir, 'darkskykey.yaml')
        logging.info(
            'Reading Dark Sky API key from file \"{}\" ...'.format(keyfile))
        with open(keyfile, 'r') as file:
            self._apikey = yaml.load(file.read())
        logging.info('Read Dark Sky API key \"{}\".'.format(self._apikey))

        # Read the user's geographical location from file.
        locfile = os.path.join(self._maindir, 'location.yaml')
        logging.info(
            'Reading location from file \"{}\" ...'.format(locfile))
        with open(locfile, 'r') as file:
            self._loc = yaml.load(file.read())
        logging.info('Read location coordinate: {} N {} W.'.format(
            self._loc['lat'], self._loc['lon']))

        # Check the validity of the location coordinate.
        logging.info('Validating location coordinate ...')
        if not (-90.0 <= self._loc['lat'] <= 90.0 
                and -180.0 <= self._loc['lon'] <= 180.0):
            raise ValueError('Coordinate {} N {} W is invalid.'.format(
                self._loc['lat'], self._loc['lon']))
        logging.info('Successfully validated coordinate.')

        # Load the fonts.
        fonts = [['SourceCodePro-Bold.otf', 18], 
            ['SourceCodePro-Regular.otf', 12]]
        self._fonts = []
        for font in fonts:
            fontfile = os.path.join(
                self._maindir, 'fonts', font[0])
            logging.info('Loading font from file \"{}\" ...'.format(fontfile))
            self._fonts.append(ImageFont.truetype(fontfile, font[1]))
            logging.info('Font loaded.')

        # Start the periodical update of the rendered image.
        self.render_images()


    def get_image(self):
        """Load background image corresponding to weather icon and temperature.
        """

        # Get all images that correspond to both the current weather icon and
        # the given temperature.
        imagefiles = []
        imagedir = os.path.join(self._maindir, 'images')
        icondir = os.path.join(imagedir, self._icon)
        logging.info('Searching images in directory \"{}\" ...'.format(icondir))
        try:
            for file in os.listdir(icondir):
                tempdir = os.path.join(icondir, file)
                if os.path.isdir(tempdir):
                    temprange = [float(bound) for bound in file.split('_')]
                    if temprange[0] <= round(self._temp) <= temprange[-1]:
                        imagefiles += [os.path.join(tempdir, file) \
                            for file in os.listdir(tempdir) \
                            if os.path.splitext(file)[-1].lower() == '.png']
            
            # If no image for the specified temperature is available, search for
            # default images that correspond to the current weather icon.
            if not imagefiles:
                imagefiles = [os.path.join(icondir, file) \
                    for file in os.listdir(icondir) \
                    if os.path.splitext(file)[-1].lower() == '.png']
        except Exception as e:
            logging.warning(e)
        logging.info('Found {} image(s).'.format(len(imagefiles)))

        # If no image for the current icon is available, search for default
        # images.
        if not imagefiles:
            logging.info('Searching images in directory \"{}\" ...'.format(
                imagedir))
            try:
                imageexts = ['.png', '.bmp', '.jpg', '.jpeg']
                for file in os.listdir(imagedir):
                    filepath = os.path.join(imagedir, file)
                    if os.path.isfile(filepath) \
                            and os.path.splitext(file)[-1].lower() in imageexts:
                        imagefiles.append(filepath)
            except Exception as e:
                logging.warning(e)
            logging.info('Found {} image(s).'.format(len(imagefiles)))

        # If the image currently on display is among the retrieved images, do
        # nothing. Otherwise, randomly select one of the found images. If none
        # was found, create a monochrome image.
        if self._imagefile not in imagefiles:
            if imagefiles:
                self._imagefile = imagefiles[random.randint(
                    0, len(imagefiles)-1)]
                self._image = Image.open(self._imagefile)
                logging.info('Selected image: \"{}\".'.format(self._imagefile))
            else:
                # If no default image is available, generate a monochrome image.
                self._imagefile = None
                self._image = Image.new('RGB', (64, 128), color='blue')
                logging.info('Created default background image.')
        

    def update_weather_info(self):
        """Update member variables that store weather information.
        """

        logging.info('Updating weather information ...')

        # Compute the minimum duration between two calls to the Dark Sky weather
        # API in order not to exceed the daily limit.
        minduration = datetime.timedelta(days=1) / 1000

        # Get the current time.
        self._time = datetime.datetime.now()

        # Abort if the waiting time to the next call has not yet passed.
        if (self._update and self._time - self._update < minduration):
            waittime = minduration - (self._time - self._update)
            logging.info(
                'Cannot call weather API in order not to exceed daily limit. '
                'Time to next call {:.1f} s.'.format(waittime.total_seconds()))
            return
        else:
            self._update = self._time

        # Get the current weather.
        logging.info('Retrieving weather information from server ...')
        try:
            with darksky.forecast(
                    key=self._apikey,
                    latitude=self._loc['lat'],
                    longitude=self._loc['lon'],
                    timeout=10,
                    units='si') as forecast:
                # Determine the current temperature and weather icon.
                self._temp = forecast.currently.temperature
                self._icon = forecast.icon

                # Determine the precipitation probability for the next couple of
                # hours.
                dry = 1.0
                for hour in forecast.hourly[:9]:
                    dry *= 1.0 - hour.precipProbability
                self._precip = 1.0 - dry
                
                logging.info('Successfully retrieved weather information: '
                    'icon: {}, temperatue: {:2.1f}°C, precipitation: {:2.0%}.'\
                    .format(self._icon, self._temp, self._precip))
        except Exception as e:
            logging.error(
                'Failed to retrieve weather information: {}.'.format(e))


    def render_image(self):
        """Render weather station image.

        This function renders a 64x128 image that displays the current time,
        temperature, and precipitation probability within the next hours along
        with a frog-themed weather illustration in the background. It then calls
        the user-defined callback function and passes this image to it.
        """
        
        # Update the weather information.
        self.update_weather_info()

        # Update the background image.
        self.get_image()

        # Draw clock and weather information on top of the background image.
        logging.info('Rendering text ...')
        image = self._image.copy()
        draw = ImageDraw.Draw(image)
        draw.fontmode = '1'
        clocktext = '{:>2d}:{:02d}'.format(self._time.hour, self._time.minute)
        draw.text((5, 5), clocktext, font=self._fonts[0], fill=self._fontcolor)
        
        temptext = ''
        if self._temp is None:
            logging.warn('Cannot display temperature: '
                'no information available.')
        else:
            temptext = u'{:> 3.0f}°'.format(self._temp)
        draw.text((4, 26), temptext, font=self._fonts[1], fill=self._fontcolor)
        
        preciptext = ''
        if self._precip is None:
            logging.warn('Cannot display precipitation probability: '
                'no information available.')
        else:
            preciptext = '{:>4.0%}'.format(min(self._precip, 0.99))
        draw.text((32, 26), preciptext, font=self._fonts[1], 
            fill=self._fontcolor)
        logging.info('Rendered text.')
        
        # Call the external callback function and pass the image to it.
        logging.info('Calling callback function ...')
        try:
            self._callback(image)
            logging.info('Called callback function.')
        except Exception as e:
            logging.error('Failed to call callback function: {}.'.format(e))


    def render_images(self):
        """Periodically render weather station images and call callback.
        """

        logging.info('Starting infinite weather station update process ...')
        while True:
            self.render_image()

            # Wait until the minute is full.
            time.sleep(60.0 - time.time() % 60)


if __name__ == '__main__':
    """Display and continuously update weather station image on screen.
    """

    # Set up logging.
    logging.basicConfig(level=logging.INFO)

    import pygame

    # Define the size of the weather station window.
    screensize = (240, 480)

    # Start the pygame engine and create a window.
    pygame.init()
    pygame.display.set_caption('Frogweather')
    screen = pygame.display.set_mode(screensize)

    # Define the callback function.
    def update(image):
        """Convert PIL image to pygame image and display it on screen.
        """
        
        # Resize the image to fit the output window.
        image = image.resize(screensize)

        # Convert the PIL image to a pygame image.
        data = image.tobytes()
        size = image.size
        mode = image.mode
        image = pygame.image.fromstring(data, size, mode)

        # Load the pygame image into the output window and refresh it.
        screen.blit(image, (0, 0))
        pygame.display.flip()

    # Periodially update the weather station window.
    weather_station = WeatherStation(lambda image: update(image))
