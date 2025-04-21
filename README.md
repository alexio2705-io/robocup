# robocup

this is a repo of russian team IVEB

The basic logic is based on multi-processing, the program is built as a state machine that switches between such actions as: driving through the cage, U-turns, issuing rescue kits in one direction or another, etc., depending on the data coming from the sensors. The robot uses 5 VL53L0X laser rangefinders connected via I2C Hub, Dynamixel AX12-A, RPI5, RPI Cameras, Neopixel LEDS motors.
