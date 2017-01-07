# SDD1306OLED Python class
Python code for the Sparkfun micro OLED using the SDD1306 and a 64x48 pixel screen
This may work with other SDD1306 displays by overridding the _width and _height

## Constraints
This Python class only works with SPI configuration for the displays.
All display work is done in the PIL library.
A default orientation is set for the display with the connection ribbon being the bottom of the display

## Packages required
Run an update
> sudo apt-get update

Install GIT to pull this repository
> sudo apt-get install git

Freefonts required for example.py code. Optional to install
> sudo apt-get install fonts-freefont-ttf

SPIDEV used to send data.
> sudo apt-get install python-spidev

Pillow PIL fork required
> sudo apt-get install python-imaging

## Example
example.py can be run (ensure it is executable) to demonstrate using PIL with the OLED library
The example python64x48.png is required to be in the same directory as the example.py to successfully run.

## Reference

### initialise()
Call to open the SPI connection, configure the GPIO and send all setup commands to the display
Always call before any other functions or after a close() call

### printSPI()
Helper function to show SPI settings on the command line

### turnOff()
Turn off the screen and anything displayed on it

### turnOn()
Resumes the display and any previous image shown before turnOff()

### clearDisplay()
Write zeros to the OLED memory and blank the display

### display(image)
Pass in a PIL image to display. This will attempt to format and resize the image if not 1 bit and the correct size. Resizing and conversion may not produce good results.

### close()
Close GPIO, SPI and reset the display. initialise() will need to be called again to reopen.
