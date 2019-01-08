#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Frog-themed weather station displayed on two 64x64 LED matrices
"""

# Check Python version.
import sys
version = sys.version_info[0]
if not 2 <= version <= 3:
    raise Exception('Frogweather requires Python 2 or 3. '
        'You are using Python {}.'.format(version))

# Set up logging.
import duallog
duallog.setup('log')

# Import external packages.
import frogweather
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import time


# Initialize the weather station.
frogweather.init()

# Create the LED matrix controller.
options = RGBMatrixOptions()
options.hardware_mapping = 'adafruit-hat-pwm'
options.rows = 64
options.cols = 64
options.chain_length = 2
options.pixel_mapper_config="Rotate:90"
options.parallel = 1
options.brightness = 70
options.led_rgb_sequence = 'RBG'
options.show_refresh_rate = False
options.scan_mode = 1
matrix = RGBMatrix(options=options)

# Periodically update the weather station image.
while True:
    # If the image changed, display it.
    if frogweather.update():
        matrix.SetImage(frogweather.get_image().convert('RGB'))

    time.sleep(1.0)
