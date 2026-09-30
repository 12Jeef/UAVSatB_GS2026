# Flight Controller (FC)

Receives commands, performs vital functions, executes low-level flight controlling (PID loops, etc). Includes Kalman filter.

Requires commands

# Onboard Computer

Runs high-level commands and algorithms such as mapping, SLAM, etc.

Connects via Ethernet or USB.

# Sensors

## Cube Orange
- 3 IMUs (accelerometer+gyro)
- 1 Magnetometer (compass)
  - Could be unreliable (magnetic fields)
- 1 Barometer (pressure → altitude)
  - Accurate at standstill/lower speeds
  - No longer accurate at higher speeds

## External
- GPS module (global position navigation)

## Cameras (External)
> Sends data to either/or/both FC or onboard computer

Considerations:
- Sensor size
  - Large = low light performance
  - Small = faster performance
- Resolution
  - Large = precise, data
  - Small = imprecise, fast
- FOV
- Interface (USB, MIPI, HDMI, etc)
- Digital vs. Optical (lens) zoom

# Communications

## Wireless
- RC **T**ransmitter = **T**X
- RC **R**eciever = **R**X

## Wired

### Serial (UART)
Inter-device communication (FC, onboard computer, sensors, etc)

### CAN
Multi-device intercommunication used for motor controllers and complex sensor integration. Includes error correction

### I2C
Low speed, one-device-at-a-time communication. Requires few wires

### SPI
Similar to UART but for multiple devices at once listening to a master

### MAVLink (Micro Air Vehicle Link)
Drone communication protocol, simply a message *format*, not a physical network type. Can be used anywhere. Includes error correctino

### DDS (Data Distribution Service)
Pub-sub pattern for data distribution. Like MAVLink but interdevice onboard the drone. Allows for real-time performance

> Ground station –MAVLink→ FC –DDS→ Onboard Computer

# Software

## Firmware
Not developed by us! Runs PID loops, contains many small configs

Choices:
- ArduPilot
  - USE: Auto missions, mapping, R&D
  - PRO: Lots of features, includes other vehicle types too
  - CON: Heavy codebase, slow to tune
- Betaflight
  - USE: FPV racing, competitive flying
  - PRO: Responsive, fast PID loops, optimized
  - CON: Limited auto, no GPS
- PX4
  - USE: Research, industry standard
  - PRO: Clean, includes simulations, flexible configs
  - CON: Steep learning curve
