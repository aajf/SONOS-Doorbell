#! /usr/bin/python3


# Doorbell - Using doorbell relais to trigger SONOS doorbell
# Author: Ive Mees
#

import config
import sys
import time
import datetime
import RPi.GPIO as GPIO ## Import GPIO library
import soco
from soco import SoCo
from soco.snapshot import Snapshot
import urllib 
import requests
from fbchat import Client
from fbchat.models import *

def init_raspberry():
   #RaspberryPI pin setup
   GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
   GPIO.setup(config.RASPBERRY['gpio_setup_pin'],GPIO.IN)
   return

def init_sonos():

   global sonos

   #check if the configured sonos is available
   sonos_found = 'no'
   for device in soco.discover():
      if device.player_name == config.SONOS['sonos_name']:
        sonos_found = 'yes'
        sonos = SoCo(str(device.ip_address))

   if sonos_found == 'no':
      print ("** Sonos not found with name " + config.SONOS['sonos_name'] + " => please check the config." )
      print ("** Sonos available: ")
      for device in soco.discover():
         print ("** Sonos device " + device.player_name + " found at " + device.ip_address)
         sys.exit()
   
   return


def sonos_bell():
   global sonos
   
   # take snapshot of selected sonos zone
   snap = Snapshot(sonos)
   snap.snapshot()

   # set doorbell play volume
   sonos.volume = config.SONOS['doorbell_volume']

   # play the doorbell sound
   # MP3 shared in local network
   sonos.play_uri(config.SONOS['uri'])
   
   # give sonos time to start playing doorbell sound
   time.sleep(1)

   # wait for door bell sound to be finished playing
   while str(sonos.get_current_transport_info()[u'current_transport_state']) == "PLAYING":
      time.sleep(0.1)

   # restore state of selected sonos zone with fade = True
   snap.restore(True) 
   
   return

def get_ipcamera_picture():
   manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
   manager.add_password(None, config.IPCAMERA['baseurl'], config.IPCAMERA['username'], config.IPCAMERA['password'])
   auth = urllib.request.HTTPBasicAuthHandler(manager)

   opener = urllib.request.build_opener(auth)
   urllib.request.install_opener(opener)

   #response = urllib.request.urlopen(baseurl + "/image/jpeg.cgi")
   response = urllib.request.urlretrieve(config.IPCAMERA['baseurl'] + config.IPCAMERA['image_path'], config.IPCAMERA['temp_image_path'])
   
   return

def send_picture_fbchat():

   client = Client(config.FB['username'], config.FB['password'])
   client.sendLocalImage(config.IPCAMERA['temp_image_path'], message=Message(text='Er is iemand aan de deur!'), thread_id=client.uid, thread_type=ThreadType.USER)
   
   return

#
#   main program 
#

init_raspberry()
init_sonos()


while True:
        input_value = GPIO.input(config.RASPBERRY['gpio_setup_pin'])
        time.sleep(0.1)
	      #test doorbell => put value to 1
        #input_value = 1        
        if input_value == 1:
           get_ipcamera_picture()
           sonos_bell()
           send_picture_fbchat()
           time.sleep(2)
           #exits after one execution
           #break

GPIO.cleanup()
