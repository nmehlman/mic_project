import RPi.GPIO as GPIO
import time
from random import randint

def init():
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)