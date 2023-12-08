# Description #

This repository contains the configuration for kernel drivers that are required for the CAN-Zero board.

# PWM #

## Configuration for kernel 4.9 ##

1. Add the following line to the `/boot/config.txt` file:
    ```
    dtoverlay=pwm-2chan,pin=12,func=4,pin2=13,func2=4
    ```
2. Restart the device:
    ```
    $ sudo reboot
    ```
    
## Configuration for kernel 4.4 ##

1. Install the device tree compiler:
    ```
    sudo apt install device-tree-compiler
    ```
2. Download `pwm-2chan-with-clk-overlay.dts` from this repository.
3. Compile the device tree:
    ```
    sudo dtc -@ -I dts -O dtb -o pwm-2chan-with-clk-overlay.dtbo pwm-2chan-with-clk-overlay.dts
    ```
4. Copy the new file to `/boot/overlays/`:
    ```
    sudo cp pwm-2chan-with-clk-overlay.dtbo /boot/overlays/
    ```
5. Add the following line to the `/boot/config.txt` file:
    ```
    dtoverlay=pwm-2chan-with-clk-overlay,pin=12,func=4,pin2=13,func2=4
    ```
6. Restart the device:
    ```
    $ sudo reboot
    ```


## Test the configuration ##

1. Give every user access to the PWM controls:
    ```
    $ sudo chmod -R 0666 /sys/class/pwm/pwmchip0/export
    $ sudo chmod -R 0666 /sys/class/pwm/pwmchip0/unexport
    ```

2. Create pwm0 and pwm1:
	```
	echo 0 > /sys/class/pwm/pwmchip0/export
	echo 1 > /sys/class/pwm/pwmchip0/export
	```

3. Give every user access to the PWM:
	```
	chmod -R 0666 /sys/class/pwm/pwmchip0/*
	```

	Or alternatively to 1-3 add to `/etc/rc.local` the following lines:
	```
	sudo chmod -R 0666 /sys/class/pwm/pwmchip0/export
	echo 0 > /sys/class/pwm/pwmchip0/export
	echo 1 > /sys/class/pwm/pwmchip0/export
	```

4. Use pwm0.\
   4.1. Set period (in ns):
     ```
     echo 20000000 > /sys/class/pwm/pwmchip0/pwm0/period
     ```
    
   4.2. Set duty cycle (in ns):
     ```
     echo 5000000 > /sys/class/pwm/pwmchip0/pwm0/duty_cycle
     ```
    
   4.3. Enable pwm0:
     ```
     echo 1 > /sys/class/pwm/pwmchip0/pwm0/enable
     ```
 5. Remove pwm0:
     ```
     echo 0 > /sys/class/pwm/pwmchip0/unexport
     ```
 
 # CAN Bus #
 
 ## Configuration (kernel 5.15) ##
    dtparam=spi=on 
    dtoverlay=spi1-1cs,cs0_spidev=off
    dtoverlay=mcp2515,spi1-0,oscillator=16000000,interrupt=25   
 ## Configuration (both kernel 4.4 and 4.9) ##
 
1. Install the device tree compiler:
    ```
    sudo apt install device-tree-compiler
    ```
2. Download `mcp2515-can2-overlay.dts` from this repository.
3. Compile the device tree:
    ```
    sudo dtc -@ -I dts -O dtb -o mcp2515-can2-overlay.dtbo mcp2515-can2-overlay.dts
    ```
4. Copy the new file to `/boot/overlays/`:
    ```
    sudo cp mcp2515-can2-overlay.dtbo /boot/overlays/
    ```
5. Add the following lines to the `/boot/config.txt` file:
    ```
    dtparam=spi=on
    dtoverlay=spi1-1cs,cs0_spidev=off
    dtoverlay=mcp2515-can2-overlay,oscillator=16000000,interrupt=25
    ```
6. Add the following lines to the `/etc/network/interfaces` file:
    ```
    auto can0
    allow-hotplug can0
    iface can0 inet manual
        pre-up /bin/ip link set can0 up type can restart-ms 100 bitrate 500000
        down /bin/ip link set can0 down
    ```
7. Install can-utils:
    ```
    sudo apt install can-utils
    ```
8. Restart the device:
    ```
    $ sudo reboot
    ```
9. Check if the can0 interface is up:
    ```
    ifconfig | grep can0
    ```
    
# I2C and Serial #

## Configuration (both kernel 4.4 and 4.9) ##
## last kernel 6.1 use sudo raspi-config ##

1. Add the following lines to the `/boot/config.txt` file:
    ```
    enable_uart=1
    dtparam=i2c_arm=on
	dtparam=i2c1=on
	dtparam=i2c1_baudrate=1000000
    dtoverlay=pi3-disable-bt
    ```
2. Install i2c-tools:
    ```
    sudo apt install i2c-tools
    ```
3. Restart the device:
    ```
    $ sudo reboot
    ```
4. Check I2C:
    ```
    i2cdetect -y 1
    ```

## build Ardupilot

	git clone --recurse-submodules https://github.com/karu2003/ardupilot	
	cd ardupilot	
	git checkout docker_rpi	
	docker build . -t ardupilot

#### for Raspberry Pi 1, Zero

	docker build . -f Dockerfile_rpi1_zero -t ardupilot_rpi

#### for Raspberry Pi 2, 3

	docker build . -f Dockerfile_rpi2_3 -t ardupilot_rpi

#### for Raspberry Pi 3A+, 3B+, 4

	docker build . -f Dockerfile_rpi3b_4 -t ardupilot_rpi

git checkout master

docker run --rm -it -v \`pwd\`:/ardupilot ardupilot_rpi:latest bash -c "./waf clean && ./waf configure --board=canzero --static && ./waf build"
