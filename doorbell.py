#! /usr/bin/python


# Doorbell - Using doorbell relais to trigger SONOS doorbell
# Author: Ive Mees
#

import sys, getopt
import time
import RPi.GPIO as GPIO ## Import GPIO library
import soco
from soco import SoCo
from soco.snapshot import Snapshot

#RaspberryPI pin setup
GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
GPIO.setup(23, GPIO.IN)

def init_sonos():

   global sonosbell
   global sonos_bell_volume

   try:
      opts, args = getopt.getopt(sys.argv[1:], "h:s:v:l")
   except getopt.GetoptError:
      print "doorbell.py -s <sonosname>"
      sys.exit(2)
   for opt, arg in opts:
      if opt == "-h":
         print "doorbell.py -s <sonosname> -v <volume>"
         sys.exit()
      elif opt == "-s":
         sonosname = arg
      elif opt == "-v":
         sonos_bell_volume = arg
      elif opt == "-l":
         for device in soco.discover():
            sonosbell = SoCo(str(device.ip_address))
            print "** Sonos device " + device.player_name + " found at " + device.ip_address
         sys.exit()
      else:
         print "doorbell.py -s <sonosname>"
         sys.exit(2)
         
   #print sonosname
   
   for device in soco.discover():
      if device.player_name == sonosname:
         sonosbell = SoCo(str(device.ip_address))
         print "** Sonos device " + device.player_name + " found at " + device.ip_address

   
   return


def sonos_bell():
   global sonosname
   global sonosbell
   global sonos_bell_volume
   play_reset = "no"
   
   # take snapshot of selected sonos zone
   snap = Snapshot(sonosbell)
   snap.snapshot()

   # set doorbell play volume
   sonosbell.volume = sonos_bell_volume

   # play the doorbell sound
   # MP3 shared in local network
   sonosbell.play_uri('http://192.168.0.116/doorbell.mp3')
   
   # give sonos time to start playing doorbell sound
   time.sleep(1)

   # wait for door bell sound to be finished playing
   while str(sonosbell.get_current_transport_info()[u'current_transport_state']) == "PLAYING":
      time.sleep(0.1)

   # restore state of selected sonos zone with fade = True
   snap.restore(True) 
   
   return

#
#   main program 
#

init_sonos()

while True:
        input_value = GPIO.input(23)
        time.sleep(0.1)
	#test doorbell => put value to 1
        #input_value = 1        
        if input_value == 1:
           #print "There is someone at the door"
           sonos_bell()
           time.sleep(2)


GPIO.cleanup()

