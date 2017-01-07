#!/usr/bin/python

from oled import SDD1306OLED
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps
import time
import os.path

# Change these values to match the GPIO pins used
# to connect the display to your Raspberry Pi
dc_pin    = 24 # data command pin
reset_pin = 25 # screen reset pin

oled = SDD1306OLED(dc_pin, reset_pin)
oled.initialise()
oled.clearDisplay()

# Open example image
img = Image.open('python64x48.png')
oled.display(img) # display on the OLED

# Write text to image. This requires freefonts
# If not present then the code will skip this
fntpath = '/usr/share/fonts/truetype/freefont/FreeSans.ttf'
if os.path.isfile(fntpath):
    # Create a new 1 bit depth image which is the same size as the display
    img = Image.new("1", (64,48), 0)
    draw = ImageDraw.Draw(img) # Create a draw object to write to the image
    font = ImageFont.truetype(fntpath, 12) # Create 12pt font from the font library

    time.sleep(2) # Pause to display the image

    # Draw text halfway down the screen using the font and fill using value of 1
    draw.text( (0,img.size[1]/2) , "Test text", font=font, fill=1)
    oled.display(img) # Write the text image to the OLED

time.sleep(3) # show screen image for 3 sec

oled.turnOff() # Turn off screen
oled.close() # Close the SPI, GPIO and reset the display
