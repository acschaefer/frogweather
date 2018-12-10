# Frogweather - a Frog-Themed Weather Station

<p align="left">
    <img src="screenshots/screenshot_summer.png" width="200"/>
    <img src="screenshots/screenshot_rain.png" width="200"/>
    <img src="screenshots/screenshot_winter.png" width="200"/>
</p>

[Screenshots](https://github.com/acschaefer/frogweather/blob/master/screenshots)

## What is Frogweather?

Frogweather is a weather app written in Python. It generates images that show
both the current time and weather information, specifically the temperature and
precipitation probability within the next nine hours. The background image shows
a frog-themed visualization of the current weather.

Since this app is meant to provide weather station images that are displayed on
a 64x128 LED matrix, the images are of size 64x128. If you need other sizes, you
can resize the images or replace the background images by your own images. The
background images are located in the
[`images`](https://github.com/acschaefer/frogweather/tree/master/images) folder.

## How to use Frogweather?

First, run the example program:
1. Install the Python package: 
   
   ```shell
   pip install frogweather
   ```

2. [Request a Dark Sky API key](https://darksky.net/dev/register). The key
    comes for free and allows you to access the Dark Sky weather service 1000
    times a day without charge. Frogweather is designed not to exceed this 
    limit.
3. Paste your key into the file
    [`darkskykey.yaml`](https://github.com/acschaefer/frogweather/tree/master/darkskykey.yaml).
4. Find out the geographical coordinates of your location, for example via [GPS
   Coordinates](https://www.gps-coordinates.net/).
5. Paste your coordinates into the file
   [`location.yaml`](https://github.com/frogweather/tree/master/location.yaml).
6. Run the example program: 

   ```shell
   python frogweather.py
   ```

   This command will open a window that displays the weather station image. It
   will also continuously update the image.

Now you can use the frogweather module in your own Python program. The following
Python code snippet shows how to do it:

```python
# Import the module.
import frogweather

# Read the configuration files.
frogweather.init()

# Continuously check for new weather station images.
while True:
    # Check if a new weather station image is available.
    if frogweather.update():
        # Access the updated image.
        image = frogweather.get_image()
```

## How does Frogweather work?

In order to generate an image, the frogweather Python module executes the
following steps:
1. It retrieves the current time from the operating system.
2. It downloads the current local weather information, i.e. temperature and
   precipitation probability, from the Dark Sky weather server.
3. It renders the weather station image.

## Credits

* The background images used in this project are modifications of the background
  images shown in Google's weather app.
* This app is [powered by Dark Sky](https://darksky.net/poweredby/): The weather
  data is downloaded from the Dark Sky weather server.
