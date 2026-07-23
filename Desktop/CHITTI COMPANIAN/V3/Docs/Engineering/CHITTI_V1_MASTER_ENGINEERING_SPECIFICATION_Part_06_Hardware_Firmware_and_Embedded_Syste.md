# CHITTI V1 MASTER ENGINEERING SPECIFICATION

# Part 6
# Hardware, Firmware & Embedded System

---

# 1. Objective

This document defines the embedded hardware architecture, firmware layers, communication interfaces, power management, and deterministic control systems used by CHITTI V1.

The embedded subsystem provides reliable sensing, motion, audio, and device control while remaining independent from desktop AI services.

---

# 2. Embedded Architecture

CHITTI consists of two embedded controllers.

Head Unit

• ESP32-S3
• Audio
• Sensors
• Display
• Connectivity
• Intent Execution

↓

UART

↓

Body Unit

• ESP8266
• Motion Control
• Servo Driver
• Safety Controller

---

# 3. Head Unit Responsibilities

The ESP32-S3 manages:

- Display
- Sensors
- Audio Capture
- Audio Playback
- Wake Word
- Local Voice Commands
- Wi-Fi
- BLE (future)
- UART Master
- Device Configuration
- Logging

---

# 4. Body Unit Responsibilities

The ESP8266 manages only motion.

Responsibilities:

- Pan Servo
- Tilt Servo
- Motion Interpolation
- Angle Limits
- UART Slave
- Servo Safety

Body MCU never performs AI processing.

---

# 5. Sensor Platform

Supported sensors include:

Ambient Light Sensor

Provides:

- Brightness
- Day/Night Detection

IMU

Provides:

- Orientation
- Motion
- Gesture Detection

RTC

Provides:

- Time
- Scheduling
- Offline Clock

Touch Sensor

Provides:

- Tap
- Long Press
- Wake Interaction

ToF Sensor

Provides:

- Presence Detection
- Distance
- Gesture
- User Approach

Future sensors remain modular.

---

# 6. Audio System

Input

- Dual MEMS Microphones

Output

- MAX98357 Audio Amplifier
- Speaker

Supports:

- Wake Word
- Speech Recognition
- Voice Feedback
- Sound Effects

---

# 7. Display System

Primary UI:

OLED Display

Displays:

- Status
- Settings
- Notifications
- Expressions
- Diagnostics

Display rendering remains isolated from business logic.

---

# 8. Motion System

Motion consists of:

Pan Servo

Tilt Servo

Features:

- Speed Control
- Easing Curves
- Angle Clamping
- Idle Motion
- Expression Motion
- Safety Limits

Motion requests originate only from Behavior Runtime.

---

# 9. Communication Interfaces

Internal:

I²C

Devices:

- RTC
- IMU
- Light Sensor
- OLED

UART

Used for:

- Head ↔ Body Communication

USB

Used for:

- Programming
- Diagnostics
- Firmware Updates

Wi-Fi

Used only for:

- Desktop Companion
- AI Services
- OTA

---

# 10. Firmware Architecture

Firmware Layers

Hardware Drivers

↓

Device Managers

↓

Communication Layer

↓

Service Layer

↓

Intent Execution

↓

Behavior Engine

↓

Motion Dispatcher

Each layer communicates through defined interfaces.

---

# 11. FreeRTOS Task Model

Primary Tasks

Wake Task

Audio Task

Intent Task

Servo Task

Logger Task

Communication Task

All tasks communicate using:

- Queues
- Event Groups
- Mutexes

Blocking operations are prohibited.

---

# 12. Power System

Battery:

Single Cell Li-Ion

Charging:

BQ24070

Power Regulation:

3.3V LDO

Features:

- Load Sharing
- Thermal Protection
- USB Charging
- Battery Monitoring

---

# 13. Safety

Safety overrides include:

Low Battery

Charging State

Servo Disconnect

Communication Timeout

Critical Error

Safe Mode

Safety always overrides user commands.

---

# 14. Logging

Embedded firmware logs:

- Boot Events
- Errors
- Sensor Status
- Voice Sessions
- Motion Commands
- Crash Reports
- Battery Events

Logs stored on SD Card.

---

# 15. Firmware Design Rules

Rule 1

Firmware remains deterministic.

Rule 2

Hardware modules remain isolated.

Rule 3

No blocking delays.

Rule 4

All hardware accessed through HAL.

Rule 5

Motion never bypasses safety checks.

Rule 6

AI never directly controls peripherals.

---

# 16. Future Expansion

Reserved support for:

- Additional Sensors
- Camera Module
- BLE
- CAN Bus
- Docking Station
- Battery Expansion
- New Motion Axes

---

# Part 6 Summary

The embedded platform provides a modular, deterministic, safety-first hardware foundation that cleanly separates physical control from higher-level AI reasoning.