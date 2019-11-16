#!/usr/bin/python
#Use this script at your own risk

import RPi.GPIO as GPIO
import os,time,sys,traceback

gpio_led=15 #the led
gpio_switch=3 #the switch
timeout = 4 #secs
timeout2=30 #how long do we wait for the shutdown?
timeout3= 2 #secs
GPIO.setmode(GPIO.BCM)

GPIO.setup(gpio_led,GPIO.OUT)

GPIO.setup(gpio_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#It's very important the pin is an input to avoid short-circuits
#The pull-up resistor means the pin is high by default

goOn=True

while goOn:
        GPIO.output(gpio_led,GPIO.HIGH)
        oddeven=GPIO.HIGH
        try:
                GPIO.wait_for_edge(gpio_switch, GPIO.FALLING)

                time.sleep(0.1) #poor-man's debounce

                now=time.time()
                while (GPIO.input(gpio_switch)==0):
                        print "switch pressed"
                        time.sleep(.2)
                        GPIO.output(gpio_led,oddeven)
                        time.sleep(.2)

                        if oddeven==GPIO.HIGH:
                                oddeven=GPIO.LOW
                        else:
                                oddeven=GPIO.HIGH

                        if (time.time()-now)>=timeout :
                                os.system("sudo shutdown -h now")
                                goOn=False

        except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                print ''.join('!! ' + line for line in lines)  # Log it or whatever here
