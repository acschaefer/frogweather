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

## How to set up the LED matrix weather station

1. Plug the Adafruit LED Matrix Bonnet on the connectors of the Raspberry Pi.
1. Connect the LED Matrix Bonnet to two 64x64 LED matrices using the Hub 75 connector.
1. Connect the LED Matrix Bonnet to the matrices via the power cables.
1. Power up the LED Matrix Bonnet and the Raspberry Pi.
1. Boot Raspbian Lite on the Raspberry Pi.
1. Install and configure ssh: `sudo raspi-config`.
1. Set up WiFi: `sudo raspi-config`.
1. Switch off on-board sound (dtparam=audio=off in /boot/config.txt)
1. Disable unnecessary services: `sudo apt-get remove bluez bluez-firmware pi-bluetooth triggerhappy pigpio`
2. Append `isolcpus=3` to the system file `/boot/cmdline.txt` in order to isolate the fourth CPU from tasks scheduled by the operating system.
3. Download LED matrix driver repository (https://github.com/hzeller/rpi-rgb-led-matrix)
4. Make the Python bindings of the LED matrix driver: In rpi-rgb-led-matrix/bindings/python/ run 
    ```
    sudo apt-get update && sudo apt-get install python2.7-dev python-pillow -y
make build-python
sudo make install-python
    ```
5. Download the weather station repository: https://github.com/acschaefer/frogweather.
6. Add the key to the Dark Sky API to the file frogweather/darkskykey.yaml.
7. Specify your location in the file frogweather/location.yaml.
8. Start the weather station via `sudo python frogweather/frogweather/ledmatrix.py` to check if everything is working.
9. Append the command `sudo python /path/to/frogweather/frogweather/ledmatrix.py` to the `~/.bashrc` script. 
The weather station is now started at every login.

