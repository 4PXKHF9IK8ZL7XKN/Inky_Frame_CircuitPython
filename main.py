import os
import socketpool
import wifi
import time
import fourwire
import board

import adafruit_ntp, rtc

#from inky_pins import LEDS

from my_functions.main import get_time, led_togggle
from digitalio import DigitalInOut, Direction, Pull

# pinout for Pimoroni Inky Frame 7.3

SCK_PIN  = board.GP18
MOSI_PIN = board.GP19
CS_PIN   = board.GP17
RST_PIN  = board.GP27
DC_PIN   = board.GP28
BUSY_PIN = board.GP10
MISO_PIN = board.GP16

CS_PIN_SD = board.GP22
SR_CLOCK  = board.GP8
SR_LATCH  = board.GP9
SR_DATA   = board.GP10

# LED Config

LED_A = DigitalInOut(board.GP11)
LED_B = DigitalInOut(board.GP12)
LED_C = DigitalInOut(board.GP13)
LED_D = DigitalInOut(board.GP14)
LED_E = DigitalInOut(board.GP15)
LED_ACT = DigitalInOut(board.GP6)
LED_CONN = DigitalInOut(board.GP7)
PICO_LED = DigitalInOut(board.LED)

LED_A.direction = Direction.OUTPUT
LED_B.direction = Direction.OUTPUT
LED_C.direction = Direction.OUTPUT
LED_D.direction = Direction.OUTPUT
LED_E.direction = Direction.OUTPUT
LED_ACT.direction = Direction.OUTPUT
LED_CONN.direction = Direction.OUTPUT
PICO_LED.direction = Direction.OUTPUT

LEDS = [LED_A, LED_B, LED_C, LED_D, LED_E, LED_ACT, LED_CONN, PICO_LED]

for item in LEDS:
    led_togggle(item)

# Get wifi AP credentials from settings.toml file
wifi_ssid = os.getenv("CIRCUITPY_WIFI_SSID")
wifi_password = os.getenv("CIRCUITPY_WIFI_PASSWORD")


if wifi_ssid is None:
   print("WiFi credentials are kept in settings.toml, please add them there!")
   raise ValueError("SSID not found in environment variables") # force quit


# Connect to WiFi
print(f"Trying to connect to: {wifi_ssid}")
try:
   wifi.radio.connect(wifi_ssid, wifi_password)
   print(f"Connected to {wifi_ssid} Wi-Fi!")
except (ConnectionError, TypeError) as e:
   print(f"Failed to connect: {e}")
   raise # force quit


# Create socket pool for network operations
pool = socketpool.SocketPool(wifi.radio)

# give wifi some time to boot
time.sleep(3)

# after connected to Wi-Fi and pool is created - setup the clock
clock = rtc.RTC()
ntp = adafruit_ntp.NTP(pool, tz_offset=+1)  # -5 for Eastern Time (EST)
# default will update the time every 3600 seconds, meaning once an hour.
# Note: For daylight saving time adjustment, you would need to change tz_offset manually
# EST is UTC-5, EDT is UTC-4

get_time(ntp,clock)


# Test Routine from some examples

import busio
import displayio
import fourwire
import busdisplay

from inky.inky_frame import InkyFrame_73

import terminalio

from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

print("starting program")
time.sleep(5)

print("releasing displays")
displayio.release_displays()

print("creating display")
spi = busio.SPI(clock=SCK_PIN,MOSI=MOSI_PIN, MISO=MISO_PIN)

display_bus = fourwire.FourWire(spi, command=DC_PIN, chip_select=CS_PIN, reset=RST_PIN, baudrate=488000)

display = InkyFrame_73(display_bus,
                        width=800,
                        height=480,
                        rotation=0,
                        black_bits_inverted=True,
                        color_bits_inverted=False,
                        grayscale=True,
                        refresh_time=1)

# Setup the Display
#display = busdisplay.BusDisplay(display_bus, INIT_SEQUENCE, width=800, height=480)

print("creating root-group")
g = displayio.Group()

# Set text, font, and color
text = "HELLO WORLD"
font = bitmap_font.load_font("/Helvetica-Bold-16.bdf")
color = 0x0000FF

# Create the text label
text_area = label.Label(font, text=text, color=color)

# Set the location
text_area.x = 100
text_area.y = 100

# Show it
display.root_group = text_area

with open("/display-ruler.bmp", "rb") as f:
  pic = displayio.OnDiskBitmap(f)
  t = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
  print("appending image")
  g.append(t)

  display.root_group = g
  print("starting refresh()")
  display.refresh()
  print("finished")
  #time.sleep(120)



