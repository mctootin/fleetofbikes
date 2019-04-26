# Simple GPS module demonstration.
# Will wait for a fix and print a message every second with the current location
# and other details.
import time
import board
# import subprocess
# from request import Request
import RPi.GPIO as GPIO
# from Exceptions.HologramError import HologramError
# from Hologram.CustomCloud import CustomCloud
#import busio

import adafruit_gps

post_endpoint = ''
post_port = 80
post_header = ''
get_endpoint = ''
get_port = 80


GPS_PERIOD = 60.0 #60 second between sending GPS coordinates
RECV_PERIOD = 5.0 #5 second  between check if messages have arrived

time_curr = 0.0
time_gps = GPS_PERIOD
time_recv = RECV_PERIOD

# Define RX and TX pins for the board's serial port connected to the GPS.
# These are the defaults you should use for the GPS FeatherWing.
# For other boards set RX = GPS module TX, and TX = GPS module RX pins.
#RX = board.RX
#TX = board.TX

# Create a serial connection for the GPS connection using default speed and
# a slightly higher timeout (GPS modules typically update once a second).
#uart = busio.UART(TX, RX, baudrate=9600, timeout=3000)

# for a computer, use the pyserial library for uart access
import serial
uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=3000)

# Create a GPS module instance.
gps = adafruit_gps.GPS(uart, debug=False)

# Initialize the GPS module by changing what data it sends and at what rate.
# These are NMEA extensions for PMTK_314_SET_NMEA_OUTPUT and
# PMTK_220_SET_NMEA_UPDATERATE but you can send anything from here to adjust
# the GPS module behavior:
#   https://cdn-shop.adafruit.com/datasheets/PMTK_A11.pdf

# Turn on the basic GGA and RMC info (what you typically want)
gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Turn on just minimum info (RMC only, location):
#gps.send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Turn off everything:
#gps.send_command(b'PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Tuen on everything (not all of it is parsed!)
#gps.send_command(b'PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0')

# Set update rate to once a second (1hz) which is what you typically want.
gps.send_command(b'PMTK220,1000')
# Or decrease to once every two seconds by doubling the millisecond value.
# Be sure to also increase your UART timeout above!
#gps.send_command(b'PMTK220,2000')
# You can also speed up the rate, but don't go too fast or else you can lose
# data during parsing.  This would be twice a second (2hz, 500ms delay):
#gps.send_command(b'PMTK220,500')

# Main loop runs forever printing the location, etc. every second.
do_send = 1

# customCloud = CustomCloud(None,
#                           send_host=post_endpoint,
#                           send_port=post_port,
#                           receive_host=get_endpoint,
#                           receive_port=get_port,
#                           enable_inbound=True)

time_curr = time.monotonic()
time_gps = time_curr
time_recv = time_curr

while True:
    # Make sure to call gps.update() every loop iteration and at least twice
    # as fast as data comes from the GPS unit (usually every second).
    # This returns a bool that's true if it parsed new data (you can ignore it
    # though if you don't care and instead look at the has_fix property).
    gps.update()
    time_curr = time.monotonic()
    # Every second print out current location details if there's a fix.
    if time_curr - time_gps >= GPS_PERIOD:
        time_gps = time_curr
        if not gps.has_fix:
            # Try again if we don't have a fix yet.
            print('Waiting for fix...')
            continue
        # We have a fix! (gps.has_fix is true)
        # Print out details about the fix like location, date, etc.
        if do_send == 1:
            gps_data = '\"'
            print('=' * 40)  # Print a separator line.
            print('Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}'.format(
                gps.timestamp_utc.tm_mon,   # Grab parts of the time from the
                gps.timestamp_utc.tm_mday,  # struct_time object that holds
                gps.timestamp_utc.tm_year,  # the fix time.  Note you might
                gps.timestamp_utc.tm_hour,  # not get all data like year, day,
                gps.timestamp_utc.tm_min,   # month!
                gps.timestamp_utc.tm_sec))
            gps_data += '{}/{}/{} {:02}:{:02}:{:02}\n'.format(
                gps.timestamp_utc.tm_mon,   # Grab parts of the time from the
                gps.timestamp_utc.tm_mday,  # struct_time object that holds
                gps.timestamp_utc.tm_year,  # the fix time.  Note you might
                gps.timestamp_utc.tm_hour,  # not get all data like year, day,
                gps.timestamp_utc.tm_min,   # month!
                gps.timestamp_utc.tm_sec)
            print('Latitude: {0:.6f} degrees'.format(gps.latitude))
            gps_data += 'Latitude: {0:.8f}\n'.format(gps.latitude)
            print('Longitude: {0:.6f} degrees'.format(gps.longitude))
            gps_data += 'Longitude: {0:.8f}\n'.format(gps.longitude)
            print('Fix quality: {}'.format(gps.fix_quality))
            #gps_data += 'Fix quality: {}\n'.format(gps.fix_quality)
            # Some attributes beyond latitude, longitude and timestamp are optional
            # and might not be present.  Check if they're None before trying to use!
            if gps.satellites is not None:
                print('# satellites: {}'.format(gps.satellites))
                # gps_data += '# satellites: {}\n'.format(gps.satellites)
            if gps.altitude_m is not None:
                print('Altitude: {} meters'.format(gps.altitude_m))
                # gps_data += 'Altitude: {} meters\n'.format(gps.altitude_m)
            if gps.speed_knots is not None:
                print('Speed: {} knots'.format(gps.speed_knots))
                gps_data += 'Speed: {}\n'.format(gps.speed_knots)
            if gps.track_angle_deg is not None:
                print('Track angle: {} degrees'.format(gps.track_angle_deg))
            if gps.horizontal_dilution is not None:
                print('Horizontal dilution: {}'.format(gps.horizontal_dilution))
            if gps.height_geoid is not None:
                print('Height geo ID: {} meters'.format(gps.height_geoid))
            # do_send = 0
            gps_data += '\"'
            # subprocess.run(['sudo', 'hologram', 'connect'])
            # subprocess.run(['sudo', 'hologram', 'send', gps_data])
    #         payload = {'Latitude': '{}'.format(gps.latitude), 'Longitude': '{}'.format(gps.longitude)}
    #         req = Request('Post', post_endpoint, data=payload, headers=post_header)
    #         print(req.text)
    # if time_curr - time_recv >= RECV_PERIOD:
