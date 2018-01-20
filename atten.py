"""
Test a subroutine to set the digital attenuator HMC1019.
"""

import time
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
execfile("/home/smauser/ContDet/io_board_subs.py")
dio = DIO()
clk = 0
le = 1
serin = 2

def clock_cycle():
  dio.setbit(clk, 1)
#  print "Clock: word = 0x%x" % (dio.value[0])
  dio.setbit(clk, 0)
#  print "Clock: word = 0x%x" % (dio.value[0])

def SetAtten(value):
  v = int(value&0x1F)
#  print "v = 0x%x" % (v)
  mask = 0x20
  while mask != 0:
#    print "mask = 0x%x" % (mask)
    dio.setbit(serin, v & mask)
    clock_cycle()
#    print "output 0x%x" % (v & mask)
#    print "mask = 0x%x, word = 0x%x" % (mask, dio.value[0])
    mask >>= 1

dio.write(0)
def timeit(v = 31):
  start = time.time()
  SetAtten(v)
  stop = time.time()
  print "Execution time %f" % (stop - start)
