import socket
import time
from math import pi, sin

UDP_IP = '192.168.1.148'
UDP_PORT = 9897

def sinc(x):
  try:
    x = pi * x
    return sin(x) / x
  except ZeroDivisionError:  # sinc(0) = 1
    return 1.0

def ColorFromAngle(angle):
  return abs(int(sinc(angle) * 255))

def CreatePixel(red, green, blue):
  return [red, green, blue]

def Push(messages):
  assert type(messages) == list
  for message in messages:
    #print message
    message = "".join(map(chr, message))
    sock = socket.socket(
      socket.AF_INET, # Internet
      socket.SOCK_DGRAM) # UDP
    bytes_sent = sock.sendto(message, (UDP_IP, UDP_PORT))
    #print 'Bytes sent: %d' % bytes_sent

RANGE = pi

def Dance():
  increment = 0
  while True:
    increment += .0005
    start_angle = (increment % (RANGE)) - (RANGE/2)
    #print 'Start angle: %f' % (start_angle)
    for strip in xrange(2):
      msg = [strip]
      for i in xrange(60):
        offset = (i * pi/180)
        red = ColorFromAngle((start_angle + offset) * 3)
        blue = ColorFromAngle((start_angle + offset) * 2)
        green = ColorFromAngle(start_angle + offset)
        red = green = blue = 0
        msg += CreatePixel(red, green, blue)
      Push([msg])
      
    
    time.sleep(.00005)
    

if __name__ == '__main__':
  Dance()
