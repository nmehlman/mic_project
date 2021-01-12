import RPi.GPIO as GPIO
import time
from random import randint

def GPIOinit():
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)