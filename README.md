# Frogweather - a Frog-Themed Weather Station

<p align="left">
    <img src="screenshots/screenshot_summer.png" width="200"/>
    <img src="screenshots/screenshot_rain.png" width="200"/>
    <img src="screenshots/screenshot_winter.png" width="200"/>
</p>

[Screenshots](https://github.com/acschaefer/frogweather/blob/master/screenshots)

## What is frogweather?

Frogweather is a weather app and library written in Python. 
It generates images that show both the current time and weather information, specifically the temperature and precipitation probability within the next three hours. 
The background image shows a frog-themed visualization of the current weather.

Since this app is meant to provide weather station images that are displayed on a 64x128 LED matrix, the images are of size 64x128. 
If you need other sizes, you can resize the images or replace the background images by your own images. 
The background images are located in the [`images`](https://github.com/acschaefer/frogweather/tree/master/images) folder.

## How to use frogweather?

First, run the example script:
1. Install the dependencies via `pip`:

   ```shell
   pip install duallog pygame PyYAML requests
   ```

2. Clone the repository:
   
   ```shell
   git clone https://github.com/acschaefer/frogweather
   ```

3. [Request an API key from Weather API](https://www.weatherapi.com). 
   The key comes for free and allows you to access the Weather API weather service 1M times per month free of charge. 
   Frogweather is designed not to exceed this limit.
4. Paste your key into the file
    [`apikey.yaml`](https://github.com/acschaefer/frogweather/tree/master/apikey.yaml).
5. Find out the geographical coordinates of your location, for example via the
   [GPS Coordinates website](https://www.gps-coordinates.net/).
6. Paste your coordinates into the file
   [`location.yaml`](https://github.com/frogweather/tree/master/location.yaml).
7. Run the example program: 

   ```shell
   python frogweather/frogweather.py
   ```

   This command will open a window that displays the weather station image. 
   It will also continuously update the image.

Now you can use the `frogweather` package in your own Python module. 
The following Python code snippet shows how to do it:

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

## How does frogweather work?

In order to generate an image, the `frogweather` module executes the following steps:
1. It retrieves the current time from the operating system.
2. It downloads the current local weather information, i.e. temperature and precipitation probability, from Weather API.
3. It renders the weather station image.

## How to set up a weather station on a Raspberry Pi?

In order to set up a frogweather-powered weather station consisting of a Raspberry Pi and two 64x64 LED matrices, you first need to set up the hardware.
For detailed instructions on setting up the matrices, see the [Raspberry Pi LED matrix driver repository](https://github.com/hzeller/rpi-rgb-led-matrix). 
If you have access to a 3D printer, you might find my [3D model of a frame for two LED matrices](https://github.com/acschaefer/3d_models/tree/master/frogweather) helpful.
Once the hardware is set up, follow the steps below to make the software work:
1. Install Raspberry Pi OS Lite on the Raspberry Pi. We recommend the version "bullseye".
   More recent versions enforce using virtual Python environments, which are harder to use with sudo privileges.
3. Switch off on-board sound, because it does not work with the LED matrix library:
   Change the corresponding line in the OS file `/boot/config.txt` to 
   
   ```
   dtparam=audio=off
   ```

   Then, blacklist the sound driver and reboot:
   ```shell
   cat <<EOF | sudo tee /etc/modprobe.d/blacklist-rgb-matrix.conf
   blacklist snd_bcm2835
   EOF    

   sudo update-initramfs -u
   sudo reboot
   ```

5. Disable unnecessary services: 
 
   ```shell
   sudo apt-get remove bluez bluez-firmware pi-bluetooth triggerhappy pigpio
   ```

6. To isolate the fourth CPU from tasks scheduled by the operating system, append the following to the Raspbian system file `/boot/cmdline.txt`:

   ```
   isolcpus=3
   ```

   Make sure the command above is separated by a space from the preceding commands; do not insert a line break.

7. Download the excellent [Raspberry Pi LED matrix driver repository](https://github.com/hzeller/rpi-rgb-led-matrix):

   ```shell
   git clone https://github.com/hzeller/rpi-rgb-led-matrix
   ```

8. Build the Python bindings of the LED matrix driver: 
   Navigate to your clone of the `rpi-rgb-led-matrix` repository and in the folder `rpi-rgb-led-matrix/bindings/python/`, run the following commands:

    ```shell
    sudo apt-get update && sudo apt-get install python3-dev cython3 -y
    make build-python 
    sudo make install-python 
    ```

8. Follow the steps in the previous section to install the frogweather app.
   Make sure to install all dependencies with `sudo` privileges - we need to run the app with `sudo` for the LED matrix library to work properly.

10. Navigate to the folder `frogweather/frogweather` and launch the weather station:

    ```shell
    sudo ./showfrog
    ```

    The `sudo` command is required by the LED matrix driver.

11. In order to launch the weather station automatically after boot, append the following command to the Raspbian system file `/etc/rc.local`:
   
    ```shell
    sudo python /path/to/frogweather/frogweather/showfrog &
    ```

The result looks like this:

![](weather_station.jpg)

[Frogweather weather station](https://github.com/acschaefer/frogweather/blob/master/weather_station.jpg)

## Credits

The background images used in this project are modifications of the background images shown in Google's weather app.
