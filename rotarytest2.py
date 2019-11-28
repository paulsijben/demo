from neopixel import *
import traceback,sys
from time import sleep
import time

# LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 16     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2812_STRIP   # Strip type and colour ordering

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
# Intialize the library (must be called once before other functions).
strip.begin()

def wheel(pos):
	"""Generate rainbow colors across 0-255 positions."""
	if pos < 85:
		return Color(pos * 3, 255 - pos * 3, 0)
	elif pos < 170:
		pos -= 85
		return Color(255 - pos * 3, 0, pos * 3)
	else:
		pos -= 170
		return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
	"""Draw rainbow that fades across all pixels at once."""
	for j in range(256*iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel((i+j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)

#rainbow(strip)

from RPi import GPIO

clk = 21
dt = 20
sw= 19
btn=26


counter = 0
colorindex=15
black=Color(0,0,0)
def renderStrip(strip,val):
	maxval=16
	inverse=-1
	base=3
	for i in range(maxval):
		if i >val:
			strip.setPixelColor(16+base-i, black)
		else:	
			strip.setPixelColor(16-i+base, wheel(colorindex))
	strip.show()	
	sleep(0.1)

def my_callback(channel):  
	global clkLastState
	global counter
	global strip
	try:
		clkState = GPIO.input(clk)
		dtState = GPIO.input(dt)

		print ">",clkState,dtState
		#if clkState != clkLastState:
		if 1:	
			if dtState != clkState:
				counter += 1
			else:
				counter -= 1
			print "@",counter
			renderStrip(strip, counter)
		#clkLastState = clkState
		sleep(0.01)
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
		print ''.join('!! ' + line for line in lines)  # Log it or whatever here
		pass

def my_btn(channel):
	print "BTN!"
	
def my_sw(channel):
	print "SW!"
	global colorindex
	colorindex+=16
	if colorindex>255: colorindex-=256
	renderStrip(strip,counter)

if __name__ == '__main__':
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	clkLastState = GPIO.input(clk)
	GPIO.add_event_detect(clk, GPIO.FALLING  , callback=my_callback, bouncetime=300)  
	GPIO.add_event_detect(btn, GPIO.FALLING  , callback=my_btn, bouncetime=300)  
	GPIO.add_event_detect(sw, GPIO.FALLING  , callback=my_sw, bouncetime=300) 
	renderStrip(strip,-1)
	raw_input("Enter anything")
	GPIO.cleanup()
	
