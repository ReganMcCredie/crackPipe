# Button imports
from time import sleep

# Display imports
from PIL import Image, ImageDraw, ImageFont
from adafruit_display_text import label
import displayio
import terminalio
import board
import adafruit_displayio_ssd1306


displayio.release_displays()

WIDTH = 128
HEIGHT = 64

i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

#display
splash = displayio.Group()
display.show(splash)


text = "this is a test"
text_area = label.Label(
    terminalio.FONT, text=text, color=0xFFFFFF, x=28, y=HEIGHT // 2-1)

# Body of program
splash.append(text_area)
while True:
    pass
