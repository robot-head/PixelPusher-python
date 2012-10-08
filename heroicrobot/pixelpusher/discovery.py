"""
UDP PixelPusher discovery module.
"""

import logging
import socket
import struct

BROADCAST_HOST = ''
BROADCAST_PORT = 7331


class Error(Exception):
  pass


class WrongDiscoveryPacketLength(Error):
  pass


class DeviceTypes(object):
  
  ETHERDREAM = 'EtherDream'
  LUMIABRIDGE = 'LumiaBridge'
  PIXELPUSHER = 'PixelPusher'

  _type_map = {
      0: ETHERDREAM,
      1: LUMIABRIDGE,
      2: PIXELPUSHER}
  
  @staticmethod
  def TypeFromId(type_id):
    assert type_id in DeviceTypes._type_map
    return DeviceTypes._type_map[type_id]


class DeviceHeader(object):
  
  def __init__(
      self, mac_address, ip_address, device_type, protocol_version, vendor_id,
      product_id, hw_revision, sw_revision, link_speed):
    self.mac_address = mac_address
    self.ip_address = ip_address
    self.device_type = device_type
    self.protocol_version = protocol_version
    self.vendor_id = vendor_id
    self.product_id = product_id
    self.hw_revision = hw_revision
    self.sw_revision = sw_revision
    self.link_speed = link_speed

  def __str__(self):
    return (
        'Mac(%s) Ip(%s) Type(%s) Prot.Ver(%d) Vend (%s) Product(%s) '
        'HW Rev (%s) SW Rev(%s) Link(%s)' % (
            self.mac_address, self.ip_address, self.device_type,
            self.protocol_version, self.vendor_id, self.product_id,
            self.hw_revision, self.sw_revision, self.link_speed))


class Device(object):
  
  def __init__(self, header):
    self.header = header
    
  def __str__(self):
    return str(self.__dict__)
  
class PixelPusher(Device):
  
  def __init__(
      self, header, strips_attached, max_strips_per_packet, pixels_per_strip,
      update_period):
    super(PixelPusher, self).__init__(header)
    self.strips_attached = strips_attached
    self.max_strips_per_packet = max_strips_per_packet
    self.pixels_per_strip = pixels_per_strip
    self.update_period = update_period
    
class Listener(object):
  
  HEADER_FORMAT = 'BBBBBBBBBBBBHHHHI'
  PP_FORMAT = 'BBHI'
  
  def __init__(self):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 
  
  def _ParsePacket(self, packet):
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
    header_tuple = struct.unpack(self.HEADER_FORMAT, packet)
    mac_address = 'foo'
    ip_address = '%d.%d.%d.%d' % (
        header_tuple[6], header_tuple[7], header_tuple[8], header_tuple[9])
    device_type = DeviceTypes.TypeFromId(header_tuple[10])
    protocol_version = header_tuple[11]
    vendor_id = header_tuple[12]
    product_id = header_tuple[13]
    hw_revision = header_tuple[14]
    sw_revision = header_tuple[15]
    link_speed = header_tuple[16]
    device_header = DeviceHeader(
        mac_address, ip_address, device_type, protocol_version, vendor_id, 
        product_id, hw_revision, sw_revision, link_speed)
    return device_header
  
  def _ParsePixelPusherConfig(self, header, config):
    """
    typedef struct PixelPusher {
      uint8_t  strips_attached;
      uint8_t  max_strips_per_packet;
      uint16_t pixels_per_strip;  // uint16_t used to make alignment work 
      uint32_t update_period;  // in microseconds
    } PixelPusher;
    """
    
    c = struct.unpack(self.PP_FORMAT, config)
    pixel_pusher = PixelPusher(header, c[0], c[1], c[2], c[3])
    return pixel_pusher
  
  def GetConfigPacket(self):
    logging.info('Binding to socket')
    self.socket.bind((BROADCAST_HOST, BROADCAST_PORT))
    logging.info('Waiting for data')
    response = self.socket.recv(4096)
    expected_size = struct.calcsize(self.HEADER_FORMAT)
    if len(response) < expected_size:
      raise WrongDiscoveryPacketLength
    logging.info('Response length: %d', len(response))
    header = self._ParsePacket(response[:expected_size])
    logging.info('Data received: %s', header)
    if header.device_type == DeviceTypes.PIXELPUSHER:
      expected_ppconfig_size = struct.calcsize(self.PP_FORMAT)
      logging.info(
          'Parsing %d to %d', expected_size,
          expected_size + expected_ppconfig_size)
      pixel_pusher = self._ParsePixelPusherConfig(
          header,
          response[expected_size:expected_size + expected_ppconfig_size])
      logging.info('PixelPusher info: %s', pixel_pusher)


if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG)
  listener = Listener()
  listener.GetConfigPacket()