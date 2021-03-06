#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Browser for weather station images.
"""

# Check Python version.
import sys
version = sys.version_info[0]
if not 2 <= version <= 3:
    raise Exception('Frogweather requires Python 2 or 3. '
        'You are using Python {}.'.format(version))

# Import required packages.
import duallog
import logging
import os
from PIL import Image, ImageDraw, ImageFont
import time


# Define the supported image file extensions.
imageexts = ['.png', '.bmp', '.jpg', '.jpeg'] 

# Determine the package directory.
pkgdir = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir))

# Determine the image directory.
imagedir = os.path.join(pkgdir, 'images')


def search_images():
    """Search for all available weather station images.
    """

    logging.info('Searching weather station images ...')
    
    imagefiles = []
    logging.info('Searching images in directory \"{}\" ...'.format(imagedir))
    for dirpath, _, filenames in os.walk(imagedir):
        for filename in filenames:
            if os.path.splitext(filename)[-1].lower() in imageexts:
                imagefiles.append(os.path.join(dirpath, filename))

    logging.info('Found {} image(s).'.format(len(imagefiles)))

    return imagefiles


if __name__ == '__main__':
    """Interactively display weather station images on screen.
    """

    # Import required modules.
    import pygame
    from rgbmatrix import RGBMatrix, RGBMatrixOptions

    # Create the LED matrix controller.
    options = RGBMatrixOptions()
    options.hardware_mapping = 'adafruit-hat-pwm'
    options.rows = 64
    options.cols = 64
    options.chain_length = 2
    options.pixel_mapper_config="Rotate:270"
    options.parallel = 1
    options.led_rgb_sequence = 'RBG'
    options.show_refresh_rate = False
    options.scan_mode = 1
    matrix = RGBMatrix(options=options)
    matrix.brightness = 30

    # Define the font color in RGBA.
    fontcolor = (250, 250, 250, 255)

    # Load the fonts.
    fontspecs = [('SourceCodePro-Bold.otf', 18), \
        ('SourceCodePro-Regular.otf', 12)]
    fonts = []
    for font in fontspecs:
        fontfile = os.path.join(pkgdir, 'fonts', font[0])
        logging.info('Loading font from file \"{}\" ...'.format(fontfile))
        fonts.append(ImageFont.truetype(font=fontfile, size=font[1]))
        logging.info('Font loaded.')

    # Start the pygame engine.
    pygame.init()

    # Search all available weather station images.
    imagefiles = search_images()
    
    # If no image could be found, abort.
    if len(imagefiles) < 1:
        logging.error('No image files found.')
        sys.exit()

    # Initialize the image counter.
    i = 0
    action = 0

    # Start the game loop.
    while True:
        # Process game events.
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT:
                    action = +1
                elif event.key == pygame.K_UP or event.key == pygame.K_LEFT:
                    action = -1
                elif event.key == pygame.K_SPACE \
                    or event.key == pygame.K_RETURN:
                    action = 0
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Update the image rendered by the weather station.
        if action is not None:
            i = (i+action) % len(imagefiles)
            imagefile = imagefiles[i]
            print('Displaying image file {} ...'.format(imagefile))
            image = Image.open(imagefile)
            draw = ImageDraw.Draw(image)
            draw.fontmode = '1'  # Turn anti-aliasing off.
            draw.text((5, 7), '12:34', font=fonts[0], fill=fontcolor)
            draw.text((4, 28), u'{:> 3.0f}°'.format(25), \
                font=fonts[1], fill=fontcolor)
            draw.text((32, 28), '{:>4.0%}'.format(0.15), \
                font=fonts[1], fill=fontcolor)
            
            matrix.SetImage(image.convert('RGB'))

            action = None

        time.sleep(0.1)
