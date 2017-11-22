import os, sys, serial, time
from pidfile import PidFile
import subprocess

#import pygame
#pygame.mixer.init()

def output(message):

    print(message)
    sys.stdout.flush()

codes = {}

def play_sound(sound):
    path = '/home/pi/Desktop/check-in-system/'
    subprocess.call(['play', path + sound])

def scan_code(code):
    
    if code in codes.keys():
        codes[code] = not codes[code]
    else:
        codes[code] = True
        
    if codes[code]:
        output('checked in: {}'.format(code))
        play_sound('check_in.wav')
    else:
        output('checked out: {}'.format(code))
        play_sound('check_out.wav')

def main():

    output('Started')

    ser = serial.Serial("/dev/ttyAMA0")
    ser.baudrate = 9600

    data_line = ''
    prev_line = ''
    prev_time = 0

    while True:

        try:

            data = ser.read()

            ## Begin code
            if data == '\x02':
                pass

            ## End code
            elif data == '\x03':

                if prev_line != data_line or time.time() - prev_time >= 0.1:

                    prev_line = data_line
                    scan_code(data_line)

                prev_time = time.time()
                data_line = ''

            ## Data
            else:
                data_line += data

        except Exception as e:
            output(e)

    ser.close()

    output('Finished')

if __name__ == "__main__":

    with PidFile("/tmp/check-in-system.pid"):
        main()
