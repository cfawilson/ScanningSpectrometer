"""Routines for testing Edward's spectrometer using the Leiker/Force
I/O card for Raspberry Pis"""
import time
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
from threading import Thread, Semaphore
#lck = Lock()
#import multiprocessing as mp
import redis
execfile("/home/smauser/ContDet/io_board_subs.py")

class YIG:
  def __init__(self, dac, freq_offset = 0):
    self.dac = dac
    self.freq_offset = freq_offset
  
  def set_freq_offset(freq_offset = 0):
    self.freq_offset = freq_offset

  def set_freq(self, freq):
    self.freq = freq
    self.v = (freq-2.0 + self.freq_offset)/2.45
    self.dac.write(0, int(6480 * self.v))


class SPECTROMETER:
  def __init__(self, adc, yig, number, fStart=2, fStop=20, df=0.025):
    self.adc = adc
    self.yig = yig
    self.number = number
    self.fStart = fStart
    self.fStop = fStop
    self.df = df
    self. nSamp = int((fStop-fStart)/df)
    self.freqs = np.empty(self.nSamp, dtype = float)
    self.vals = np.empty(self.nSamp, dtype=np.int16)

  def sweep(self):
    """ Do a frequency sweep from fStart to fStop reading the ADC at each
    frequency. Put the measured values in the global array vals and
    the frequencies in the array freqs.
    freqs and vals are stored in the file sweep.txt"""
    global vname
  
    freq = self.fStart
    self.yig.set_freq(freq)
    time.sleep(.01)
    start =  time.time()
    for i in range(self.nSamp):
      self.vals[i] = self.adc.read(0,1)
      self.freqs[i] = freq
      freq += self.df
      self.yig.set_freq(freq)
    self.s = self.vals.tostring()
    print self.number, time.time() - start
  
  def plotSweep(self):
    """Plot vals vs freqs from the last sweep"""
    plt.plot(self.freqs, self.vals)
    plt.show(block = False)

  def main(self):
    self.adc.set_continuous_mode(0,1)
#    self.adc.set_one_shot_mode()
    for i in range(5):
      self.sweep()
#      redis_db.set(vname, self.vals.tostring())
#      redis_db.set(vname, self.vals)
    
  def send_to_redis(self, sem, name):
    j = 0
    while self.run == True:
      sem.acquire()
      redis_db.set(name, self.s)
      print "Sent number", j, self.run
      j += 1

  def run_send(self):
    self.adc.set_continuous_mode(0,1)
    self.s = '0x00'
    print time.time()
    self.run = True
    sem = Semaphore(0)
    name = "vals%d" % (self.number)
    send_t = Thread(target=self.send_to_redis, args = (sem, name))
    send_t.start()
    for i in range(5):
      self.sweep()
      if i == 4:
        self.run = False
      sem.release()
    send_t.join()
    print time.time()


#Instantiate the devices and objects we need
#dio = DIO()
adc0 = ADC(0)
dac0 = DAC(0)
yig0 = YIG(dac0)
spec0 = SPECTROMETER(adc0, yig0, 0)
adc1 = ADC(1)
dac1 = DAC(1)
yig1 = YIG(dac1)
spec1 = SPECTROMETER(adc1, yig1, 1)

def runTwo():
  print time.time()
  p0 = mp.Process(target=spec0.main)
  p1 = mp.Process(target=spec1.main)
  p0.start()
  p1.start()
  p0.join()
  p1.join()
  print time.time()

redis_db = redis.StrictRedis(host="192.168.1.152", port=6379)
#setADCContinuous()
##setADCOneShot()
#
#def timeSeries(attV=0.0, freq = 10.6, len=4096):
#  """Take a time series of data at constant frequency and attenuator settings"""
#  vals = np.empty(len)
#  yigV(v(freq))
#  attenV(attV)
#  start =  time.time()
#  for i in range(0,len,1):
#    vals[i] = readADC(0)
#  return(vals, time.time() - start)
#
#def measureNoise(freq=10.6, doplot = True):
#
#  """For attenuator settings from 0 - 2V in 0.25V steps, measure the
#  rms noise in 4096 samples with the YIG set to freq.
#  Write attenuator V, mean value, std and std/mean for each measurement
#  in the file mn.out.  Make a plot if doplot is True"""
#
#  outFile = open("mn.out", 'w')
#  for attV in frange(0.0, 2.0, .25):
#    (vals, dt) = timeSeries(attV=attV, freq=freq)
#    m = mean(vals)
#    s = std(vals)
#    print >>outFile, "%.2f %.1f %.2f %.6f" % (attV, m, s, s/m)
#    outFile.flush()
#    if doplot:
#      plot(vals)
#      show()
#  outFile.close()
#
#def average(len=4096, attV=0.0, freq = 10.6):
#  """ return the average of len measurements at the given atten
#  and freq setting"""
#
#  sum = 0
#  yigV(v(freq))
#  attenV(attV)
#  for i in range(0,len,1):
#    sum += readADC(0)
#  return(float(sum)/len)
#
#def stability(nMinutes = 1440):
#  """Repeatedly average 15 sec. of measurements at 0 and then max attenuation
#  Write a line in the file with elapsed time, min attenuation average,
#  max atenaution average in the file stab.out after each pair of measurements"""
#
#  outFile = open("stab.out", 'w')
#  length = 820*15
#  start =  time.time()
#  for i in range(nMinutes*4):
#    high = average(length, 0.0)
#    low = average(length, 2.0)
#    print >> outFile, "%.2f %.2f %.2f" % (time.time()-start, high, low)
#    outFile.flush()
#
#def sweep(fStart=2, fStop=20, df=0.025):
#  """ Do a frequency sweep from fStart to fStop reading the ADC at each
#  frequency. Put the measured values in the global array vals and
#  the frequencies in the array freqs.
#  freqs and vals are stored in the file sweep.txt"""
#
#  global vals, freqs
#
#  nSamp = int((fStop-fStart)/df)
#  vals = np.empty(nSamp)
#  freqs = np.empty(nSamp)
#  freq = fStart
#  adc0.set_continuous_mode(0,1)
##  adc0.set_one_shot_mode()
#  yig0.set_freq(freq)
#  time.sleep(.01)
#  start =  time.time()
#  for i in range(nSamp):
#    vals[i] = adc0.read(0,1)
#    freqs[i] = freq
#    freq += df
#    yig0.set_freq(freq)
#  print time.time() - start
##  savetxt('sweep.txt', c_[freqs, vals], fmt = "%.3f %d")
#
#def plotSweep():
#  """PLot vals vs freqs from the last sweep"""
#  plt.plot(freqs, vals)
#  plt.show(block = False)
#
#def clearPlots():
#  """Close all plots.  To clear the most recent plot and leave the window
#  open, use clf()"""
#  close("all")
#
#def sqWave(f1 = 5.0, f2 = 6.4):
#  """ switch the frequency back and forth between f1 and f2, recording
#  16 samples at each frequency in the global variable vals.
#  You msy plot the resultswith the ommand 'plot(vals)'"""
#
#  global vals
#
#  nSamp = 64
#  vals = np.empty(nSamp)
#  f = f2
#  for i in range(nSamp):
#    if(i &15 == 0):
#      if f == f2:
#        f = f1
#      else:
#        f = f2
#      yigV(v(f))
#    vals[i] = readADC(0)
#
#def Spectrometer():
#  sweep()
#  plotSweep()
#  plt.show(block = False)
#  plt.draw()
#  sweep_count = 0
#  start =  time.time()
#  for i in range(1,10):
#    sweep()
#    plt.clf()
#    plotSweep()
#    plt.draw()
#    sweep_count += 1
#    print time.time() - start, sweep_count
#    time.sleep(3)
##    print "Plot", i
#  #  time.sleep(0.1)


def hot():
  global hotVals

  spec0.sweep()
  hotVals = spec0.vals
  plt.clf()
  spec0.plotSweep()

def cold():
  global coldVals

  spec0.sweep()
  coldVals = spec0.vals
  spec0.plotSweep()

def zero():
  global zeroVals

  sweep()
#  zeroVals = vals
#  plotSweep()
  fit = np.polyfit(spec0.freqs,spec0.vals,1)
  zeroVals = polyval(fit, spec0.freqs)
#  fit_fn = np.poly1d(fit)
  plt.plot(spec0.freqs,spec0.vals, spec0.freqs, zeroVals)
  print std(spec0.vals-zeroVals)

def Y():
  global hotVals, coldVals, zeroVals
  
  try:
    zeroVals
  except NameError:
    zeroVals = np.zeros(np.size(spec0.freqs))
  Y = (hotVals - zeroVals)/(coldVals - zeroVals)
  np.savetxt('/home/smauser/Y.txt', np.c_[spec0.freqs, hotVals, coldVals, Y], fmt = "%.3f %d %d %.3f")
  plt.clf()
  plt.plot(spec0.freqs, Y)
  plt.draw()
