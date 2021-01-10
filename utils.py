import RPi.GPIO as GPIO
import time
from random import randint
from librosa import resample

def GPIOinit():
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
