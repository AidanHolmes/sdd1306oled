# Copyright 2017 Aidan Holmes
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import RPi.GPIO as GPIO
import spidev
import time
from PIL import Image
from PIL import ImageOps
from sys import version_info

class SDD1306OLED(object):
        "OLED interface for Sparkfun SDD1306 micro OLED breakout"

        def __init__(self, dc, reset, bus = 0, cs = 0, mhz = 6):
                self._reset_pin = reset
                self._dc_pin = dc
                self._chip_select = cs
                self._bus = bus
                self._width = 64
                self._height = 48
                self._spi = spidev.SpiDev()
                self._hz = mhz * 1000000

        def writeSPI(self, byte):
                self._spi.xfer2([byte])
                
        def writeCommand(self,c):
                GPIO.output(self._dc_pin, 0)
                self._spi.xfer2([c])

        def writeData(self, d):
                GPIO.output(self._dc_pin, 1)
                self._spi.xfer2([d])

        def initialise(self):
                'Initialise the OLED. Needs running prior to setting images or after a call to close()'
                self._spi.open(self._bus,self._chip_select)
                GPIO.setmode(GPIO.BCM)

                GPIO.setup(self._dc_pin, GPIO.OUT)
                GPIO.setup(self._reset_pin, GPIO.OUT)

                self._spi.mode = 0
                self._spi.cshigh = False
                self._spi.bits_per_word = 8
                self._spi.max_speed_hz = self._hz

                GPIO.output(self._dc_pin, 1) # pull high for data and low for command
                GPIO.output(self._reset_pin, 0) # set low to reset 
                time.sleep(0.1) # pause

                # Basically follow the specification to enable and pinch a 
                # few lines from ADA fruit and Sparkfun initialisation code for this chip
                GPIO.output(self._reset_pin, 1) # enable display
                GPIO.output(self._dc_pin,0) # set to command mode
                time.sleep(0.1) # wait 100ms (spec is for 5ms min)
                GPIO.output(self._reset_pin, 0) # disable display
                time.sleep(0.1) # wait 100ms (spec is for 10ms min)
                GPIO.output(self._reset_pin, 1) # enable display

                self.writeSPI(0xAE) # display off command

                self.writeSPI(0xD5) # display clock div
                self.writeSPI(0x80) # 1000 0000 seems to suggest no divide ratio and default frequency

                self.writeSPI(0xA8) # set muliplex
                #	self.writeSPI(0x3F) # default value of 63 (defined in spec)
                self.writeSPI(0x2F) # Defined for display - don't mess around with

                self.writeSPI(0xD3) # set display offset
                self.writeSPI(0x0) # com offset set to 0

                self.writeSPI(0x40 | 0x00) # set startline offset to zero

                self.writeSPI(0x8D) # charge pump
                self.writeSPI(0x14) # enable pump (disable with 0x00). 0xAF completes pump charge

                self.writeSPI(0xA6) # normal display

                self.writeSPI(0xA4) # display all on resume

                self.writeSPI(0x20) # memory mode
                self.writeSPI(0x10) # page address mode (10b for page, 01b for vertical)

                #	self.writeSPI(0xA0 | 0x00) # seg remap 0 to SEG0. Rows are right to left from display ribbon
                self.writeSPI(0xA0 | 0x01) # seg remap 127 to SEG0. Rows are left to right from display ribbon

                self.writeSPI(0xC8) # com scan descend. Basically flips the display from display connector ribbon
                #self.writeSPI(0xC0) # com scan ascend from display connector

                self.writeSPI(0xDA) # set com pins
                self.writeSPI(0x12) # A4 is 0 so sequential COM pin. A5 is 1 so enable com left/right remap

                self.writeSPI(0x81) # set contrast
                self.writeSPI(0xCF) # 00h to FFh contrast values. Be aware of current draw

                self.writeSPI(0xD9) # set precharge
                self.writeSPI(0xF1) # Phase 1: 1 dclk (max 15), Phase 2: 15 dclks (max 15)

                self.writeSPI(0xDB) # set com deselect
                self.writeSPI(0x40) # above 0.83 x Vcc for regulator output. 

                self.writeSPI(0xAF) # display on

                time.sleep(0.1)

        
        def printSPI(self):
                ' Helper function to show SPI parameters'
                print "Settings:"
                print " bits_per_word->", self._spi.bits_per_word
                print " cshigh->", self._spi.cshigh
                print " lsbfirst->", self._spi.lsbfirst
                print " max_speed_hz->", self._spi.max_speed_hz
                print " mode->", self._spi.mode


        def turnOff(self):
                self.writeCommand(0xAE)

        def turnOn(self):
                self.writeCommand(0xAF)
	
        def setColumnAddress(self,add):
                self.writeCommand ((0x10 | add >> 4) + 0x02)
                self.writeCommand (0x0F & add) 

        def clearDisplay(self):
                'Write zeros to the OLED directly and clear the screen'
                for y in range(0,6):
                        self.setColumnAddress(0)
                        self.writeCommand(0xB0 | y)
                        for x in range(0,64):
                                self.writeData(0x00)

        def close(self):
                'Close GPIO and SPI. Initialise will be needed to open again. This will reset the display'
                # clean up
                GPIO.output(self._reset_pin, 0)
                GPIO.cleanup()
                self._spi.close()
                
        def display(self, image):
                "Display a PIL image on the display"

                if image.size[0] != self._width or image.size[1] != self._height:
                        # Resize
                        image = image.resize((self._width, self._height))

                # Try to convert any images which are not 1 bit depth
                if image.mode != "1":
                        image = ImageOps.grayscale(image).convert("1", dither=Image.FLOYDSTEINBERG)

                # Get the Python version
                major_version = version_info[0]
                raw = image.tobytes() # 1 bit colour image

                # Iterate through the memory pages of the OLED and copy the image bits from PIL
                for mem_page in range (0, int(self._height/8)):
                        self.setColumnAddress(0)
                        self.writeCommand(0xB0 | mem_page)
                        
                        for x in range (0, self._width):
                                out = 0x00
                                idx = x + (mem_page * self._width * 8)
                                for y in range (0, 8):
                                        bitout = 0x00
                                        # Python 2 and 3 handle the byte data differently
                                        if major_version >= 3:
                                                bitout = raw[int(idx/8)] & (0x01 << (7-idx%8))
                                        else:
                                                bitout = ord(raw[int(idx/8)]) & (0x01 << (7-idx%8))
                                        idx += self._width # Move the image index to the next row

                                        # If the bit was set in the PIL image then set the bit for the OLED
                                        if bitout > 0:
                                                out |= 0x01 << y
                                # Write the image byte to the OLED
                                self.writeData(out)




