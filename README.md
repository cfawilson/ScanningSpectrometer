# ScanningSpectrometer
RPi software for Edward's scanning spectrometer using Brian's analog and digital IO Board

## Notes for setting up an RPi
References on the web which I found useful:

A good guide to apt-get is at https://help.ubuntu.com/community/AptGet/Howto

I2C reference: http://www.instructables.com/id/Raspberry-Pi-I2C-Python/?ALLSTEPS

To change baud rate: http://raspberrypi.stackexchange.com/questions/29422/what-bitrate-can-i-get-from-an-i2c-bus

The site I used to program the ADC and DCAs in C and where I got sampleADS1115.c
http://openlabtools.eng.cam.ac.uk/Resources/Datalog/RPi_ADS1115/

To set up a fresh RPi:
At first ssh pi@raspberrypiu  use password raspberry
To update the distribution:
  sudo apt-get update
  sudo apt-get dist-upgrade

```
sudo adduser rwilson
add rwilson to groups i2c and sudo in /etc/group
cp i2c.conf to /etc/modprobe.d
After editing i2c.conf, issue 'sudo modprobe -r i2c_bcm2708' and then
'sudo modprobe i2c_bcm2708'
sudo modprobe --first-time i2c-dev
sudo apt-get install i2c-tools
enable i2c with raspi-config
in /etc/modules add these two lines:
i2c_bcm2708
i2c_dev
in /boot/config.txt add two lines:
dtparam=i2c1=on
dtparam=i2c_arm=on
if they are not already present
add to .bashrc:
case $TERM in
        xterm|xterms|xterm-256color|vs100s)    PS1="RPi:\W$ \[\033]0;\u@\h:\w\007\]";;
        *)                      PS1="RPi:[\W]\\$ ";;
esac

add ':.' to PATH in .profile
reboot the RPi and login as rwilson
rsync -av the working files to this RPI
copy .ssh/authorized_keys to my home directory
run /usr/sbin/i2cdetect -y 1  to see devices on the i2c bus

cat /proc/modules to see which modules are loaded
dpkg -S fname to see which package fname came from`

For Python also need: python-smbus and python-matplotlib and ipython

To archive RPi files on a computer:  rsync -av "$RPI:SteveBoard/*" .
In the other direction to the RPi  rsync -av SteveBoard/ $RPI:SteveBoard/

To set up the watchdog timer:
sudo apt-get install watchdog  //get the watchdog daemon
add bcm2708_wdog to /etc/modules
sudo update-rc.d watchdog defaults
in /etc/watchdog.conf uncomment:
   #watchdog-device
   #max-load-1 = 24
sudo modprobe bcm2708_wdog
can use lsmod to see if the watchdog module is loaded

Info for installing redis at:
https://www.fullstackpython.com/blog/install-redis-use-python-3-ubuntu-1604.htmlhttp://mjavery.blogspot.com/2016/05/setting-up-redis-on-raspberry-pi.html
```

To seet a sttic IP address, add this to /etc/dhcpcd.conf 
```
interface eth0

static ip_address=131.142.8.61/21
static routers=131.142.8.1
static domain_name_servers=131.142.21.50
```

Adding to /etc/network/interfaces did not seem to work:
```
iface eth0 inet static
  address 131.142.8.61
  netmask 255.255.248.0
  gateway 131.142.8.1
```

/etc/modprobe.d/raspi-blacklist.conf is the place to uncomment the modules for
bluetooth and wifi.

To copy an sd card see instructions: https://computers.tutsplus.com/articles/how-to-clone-raspberry-pi-sd-cards-using-the-command-line-in-os-x--mac-59911

First find its /dev entry by running 'diskutil list', then use dd to make an image file:
```
sudo dd if=/dev/disk4 bs=2m of=rpi3_10_20_17.dmg
dd will print a progress report if you send it a SIGINFO:
sudo kill -INFO 11767
```
