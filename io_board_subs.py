"""
Subroutines for controlling the ADCs, DACs and DIO on the Leiker/Force
I/O card
"""

class ADC:
  def __init__(self, adc_number, rate= 7, gain = 2):
    """
    There are two ADCs, 0 and 1.
    You may instantiate none, either or both of them
    Rate defaults ot 7 which is the highest speed of 860 samples/sec.
    For rate from 0 to 7, sampling rate is (8, 16, 32, 64, 128, 250, 475,860)
    Gain defaults to 2 which is +/-2.048V full scale.
    for gain from 0 to 7, Full Scale voltage is +/- (6.144, 4.096, 2.048,
    1.024, .512, .256, .256, .256)
    """
    if adc_number == 0:
      self.i2c_address = 0x48
      # gpio pin to receive the conversion complete transition
      self.interrupt_pin = 15
    elif adc_number == 1:
      self.i2c_address = 0x49
      self.interrupt_pin = 16
    else:
      raise ValueError('There are two ADCs, 0 and 1')
    if rate < 0 or rate > 7:
      raise ValueError('Rate must be in [0,7]')
    self. rate = rate
    if gain < 0 or gain > 7:
      raise ValueError('Gain must be in [0,7]')
    self.gain = gain
    # set thethreshold registers so that the alert.ready pin will act as a
    # conversion complete pin to potentially cause an interrupt
    bus.write_i2c_block_data(self.i2c_address, 2, [0x00,0x00])
    bus.write_i2c_block_data(self.i2c_address, 3, [0xff,0xff])
    GPIO.setup(self.interrupt_pin, GPIO.IN)
#    GPIO.add_event_detect(self.interrupt_pin, GPIO.RISING)
    GPIO.wait_for_edge(self.interrupt_pin, GPIO.RISING, timeout = 2)
    self.one_shot = True

  def read(self, chan=0, differential_mode = 0):
    """
    Read the adc in either one shot or contiunous mode.
    If the adc is in one shot mode, then chan and differenbtial mode will
    be used to set up the multiplexer.
    Differential_mode can be:
      0 for a ground reference for all 4 channels
      1 for input 1 as the reference for channel 0
      3 for input 3 as the reference for channels 0-2
    """
#    global lck

    if self.one_shot:
      if chan < 0 or chan > 3:
        raise ValueError('Chan must be in [0,3]')
      if differential_mode == 0:
        ctl1 = 0xC1 | (chan << 4) | (self.gain << 1)
      elif differential_mode == 1 and chan == 0:
        ctl1 = 0x81 | (self.gain << 1)  # Assume channel 0
      elif differential_mode == 3 and chan != 3:
        ctl1 = 0x81 | ((chan+1) << 4) | (self.gain << 1)
      else:
        raise ValueError(\
	  'differential_mode must be 0 ,1 or 3.  If it is 1, chan must be 0)')
      ctl2 = 8 | (self.rate << 5)
      #start conversion
      bus.write_i2c_block_data(self.i2c_address, 1, [ctl1,ctl2])
    GPIO.wait_for_edge(self.interrupt_pin, GPIO.RISING, timeout = 4)
#    while GPIO.event_detected(self.interrupt_pin) == False:
#      time.sleep(0.0005)
    bytes = bus.read_i2c_block_data(self.i2c_address, 0, 2)
    rtn = bytes[1] | bytes[0] << 8
    if rtn < 32768:
      return rtn
    else:
      return rtn - 65536
    return 0

  def set_one_shot_mode(self):
    """
    Put the ADC in one-shot mode so that a conversion is triggered
    by each call.  The channel and differential_mode will be set up for each
    read() call.  The maximum rate of reading will be considerably slower
    """
    self.one_shot = True
    x = self.read()

  def set_continuous_mode(self, chan=0, differential_mode = 0):
    """
    Start continuous conversions using the current rate and gain in
    addition to the chan and differential mod in the call
    Differential_mode can be:
      0 for a ground reference for all 4 channels
      1 for input 1 as the reference for channel 0
      3 for input 3 as the reference for channels 0-2
    """

    self.one_shot = False
    if chan < 0 or chan > 3:
      raise ValueError('Chan must be in [0,3]')
    if differential_mode == 0:
      ctl1 = 0xC0 | (chan << 4) | (self.gain << 1)
    elif differential_mode == 1 and chan == 0:
      ctl1 = 0x80 | (self.gain << 1)  # Assume channel 0
    elif differential_mode == 3 and chan != 3:
      ctl1 = 0x80 | ((chan+1) << 4) | (self.gain << 1)
    else:
      raise ValueError(\
	'differential_mode must be 0 ,1 or 3.  If it is 1, chan must be 0)')
    ctl2 = 8 | (self.rate << 5)
    #start conversion
    bus.write_i2c_block_data(self.i2c_address, 1, [ctl1,ctl2])

class DAC:
  def __init__(self, dac_number):
    """
    There are two DACs, 0 and 1.
    You may instantiate none, either or both of them
    """
    if dac_number == 0:
      self.i2c_address = 0x4c
    elif dac_number == 1:
      self.i2c_address = 0x4d
    else:
      raise ValueError("dac_number must be 0 or 1")


  def write(self, chan, val):
    """Write the value val to the DAC at channel chan
    val is in the range [0,65537] for 0-2V"""
  
    ctl = 0x10 | ((chan & 3) << 1)
    hByte = (int(val) >>8) & 0xff
    lByte = int(val) & 0xff
    bus.write_i2c_block_data(self.i2c_address, ctl, [hByte,lByte])

class DIO:
  def __init__(self, config0 = 0, config1 = 0xff):
    """
    There is one DIO chip with two 8 bit bytes of I/O lines, any of
    which can be configured as input or output.
    Bits in the config parameters determine I/O direction
    for the correcponding bits in the corresponding bytes. Set the bits to
    0 for output or 1 for input.  The default values set the first byte to
    outputs and the second to inputs.
    """
    self.i2c_address = 0x20
    # gpio pin to receive the conversion complete transition
    self.int_bar_pin = 13
    self.reset_bar_pin = 11
    self.value = [0,0]
    GPIO.setup(self.int_bar_pin, GPIO.IN)
    GPIO.setup(self.reset_bar_pin, GPIO.OUT, initial=GPIO.HIGH)
    bus.write_i2c_block_data(self.i2c_address, 6, [config0, config1])

  def write(self, value=0xff, byte = 0):
    """
    Write the bits in value to the corresponding bits in the given byte
    which are set up as output bits.
    By default, value is written to the first byte (byte 0).
    """
    bus.write_byte_data(self.i2c_address, 2+(byte & 0x1), value)
    self.value[byte] = value

  def read(self, byte = 1):
    """
    Read and return the state of the pins of the requested byte.  If a
    pin is set up as input, the pin is read directly.  If it is set up
    as output, the state written to that pin is returned.
    By default, the seconf byte is read (byte 1).
    """
    return(bus.read_byte_data(self.i2c_address, byte))

  def setbit(self, bit, value=1, byte = 0):
    """
    Set one of the bits in this byte to 0 or 1 without changing the others
    """
    mask = 1<<bit
    if (((self.value[byte] & mask) == 0) ^ (value == 0)):
      self.value[byte] ^= mask
      self.write(self.value[byte], byte)

#    curval = self.read(byte)
#    mask = 1<<bit
#    curval &= ~mask
#    if value:
#      curval |= mask
#    self.write(curval, byte)
#    return(curval)

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
import smbus
bus = smbus.SMBus(1)
#import time

#adc0 = ADC(0)
#dac0 = DAC(0)
#dio = DIO()
#
#import time
#
#def average(n = 1000):
#  start = time.time()
#
#  v = 0
#  for i in range(n):
#    v += adc1.read(0,1)
#  print float(v)/n, time.time() - start
