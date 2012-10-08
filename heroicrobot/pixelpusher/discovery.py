"""
UDP PixelPusher discovery module.
"""

import logging
import socket
import struct

BROADCAST_HOST = ''
BROADCAST_PORT = 7331

"""
Device Header format:
  uint8_t mac_address[6];
  uint8_t ip_address[4];
  uint8_t device_type;
  uint8_t protocol_version; // for the device, not the discovery 
  uint16_t vendor_id;
  uint16_t product_id;
  uint16_t hw_revision;
  uint16_t sw_revision;
  uint32_t link_speed;  // in bits per second
"""

class Error(Exception):
  pass


class WrongDiscoveryPacketLength(Error):
  pass


class Listener(object):
  
  HEADER_FORMAT = 'BBBBHHHHI'
  
  def __init__(self):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 
  
  def _ParsePacket(self, packet):
    header = struct.unpack(self.HEADER_FORMAT, packet)
    return header
  
  def GetConfigPacket(self):
    logging.info('Binding to socket')
    self.socket.bind((BROADCAST_HOST, BROADCAST_PORT))
    logging.info('Waiting for data')
    response = self.socket.recv(4096)
    if len(response) < 16:
      raise WrongDiscoveryPacketLength
    logging.info('Response length: %d', len(response))
    logging.info('Data received: %s', self._ParsePacket(response[:16]))
    

if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG)
  listener = Listener()
  listener.GetConfigPacket()