# Architecture Design Document - Olympus Project

**Document ID:** ADD-001  
**Version:** 1.0  
**Standard:** ISO/IEC/IEEE 42010  

---

## 1. Introduction

### 1.1 Purpose
This Architecture Design Document (ADD) describes the system architecture for the autonomous Mars rover, defining structural components, their relationships, and design decisions.

### 1.2 Scope
Covers all subsystem architectures: Navigation, Communication, Power, Payload, and Ground Control interfaces.

### 1.3 Definitions

| Term | Definition |
|------|------------|
| OBC | On-Board Computer |
| ADCS | Attitude Determination and Control System |
| EPS | Electrical Power System |
| GCS | Ground Control Station |

---

## 2. Architecture Overview

### 2.1 System Context Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL ENVIRONMENT                               │
│  ┌─────────────────┐              ┌─────────────────┐                      │
│  │  Ground Control │              │   Mars Surface │                      │
│  │    Station      │              │   Environment   │                      │
│  └────────┬────────┘              └────────┬────────┘                      │
└───────────┼──────────────────────────────┼─────────────────────────────────┘
            │                              │
            │                              │
    ════════╪══════════════════════════════╪══════════════════════════════
            │      MARS ROVER SYSTEM       │
            │                              │
    ┌───────▼──────────────────────────────▼──────┐
    │              COMMUNICATION SUBSYSTEM          │
    │         (X-band, UHF, Emergency)              │
    └───────────────────────┬───────────────────────┘
                            │
    ┌───────────────────────▼───────────────────────┐
    │           ON-BOARD COMPUTER (OBC)              │
    │  ┌─────────┐ ┌─────────┐ ┌─────────┐         │
    │  │ Nav     │ │ Payload │ │ Power   │         │
    │  │ Module  │ │ Module  │ │ Module  │         │
    │  └─────────┘ └─────────┘ └─────────┘         │
    └───────────────────────┬───────────────────────┘
                            │
    ┌──────────┬───────────┼───────────┬──────────┐
    │          │           │           │          │
┌───▼───┐ ┌────▼────┐ ┌────▼────┐ ┌────▼────┐ ┌────▼───┐
│Sensor │ │Actuator │ │Power    │ │Thermal  │ │Payload │
│Array  │ │Control  │ │System   │ │Control  │ │Instruments│
└───────┘ └─────────┘ └─────────┘ └─────────┘ └────────┘
```

### 2.2 Architecture Style
- **Primary:** Layered Architecture
- **Secondary:** Component-Based Architecture
- **Pattern:** Publish-Subscribe for inter-subsystem communication

---

## 3. Subsystem Architectures

### 3.1 Navigation Subsystem

```
┌─────────────────────────────────────────┐
│         NAVIGATION SUBSYSTEM            │
├─────────────────────────────────────────┤
│                                          │
│  ┌─────────────┐    ┌─────────────┐     │
│  │   GPS/GNSS  │    │   Stereo    │     │
│  │   Receiver  │───▶│   Vision    │     │
│  └─────────────┘    └──────┬──────┘     │
│                            │            │
│                     ┌──────▼──────┐     │
│                     │   Fusion    │     │
│                     │   Engine    │     │
│                     └──────┬──────┘     │
│                            │            │
│  ┌─────────────────────────┼─────────┐  │
│  │         ┌───────────────┘         │  │
│  │         │                           │  │
│  ▼         ▼                           ▼  │
│ ┌─────────────┐              ┌─────────────┐│
│ │Localization │              │Path Planning││
│ │   Module    │              │   Module    ││
│ └──────┬──────┘              └──────┬──────┘│
│        │                             │       │
│        └──────────┬─────────────────┘       │
│                   │                           │
│            ┌──────▼──────┐                   │
│            │  Navigation │                   │
│            │  Controller │                   │
│            └─────────────┘                   │
│                                          │
└─────────────────────────────────────────┘
```

**Components:**

| Component | Responsibility | Interface |
|-----------|---------------|-----------|
| GPSReceiver | Position determination | SPI |
| StereoVision | Obstacle detection | Ethernet |
| FusionEngine | Sensor data fusion | Internal |
| LocalizationModule | Position estimation | Internal |
| PathPlanningModule | Route computation | Internal |
| NavController | Motor command generation | CAN |

### 3.2 Communication Subsystem

| Component | Function | Protocol |
|-----------|----------|----------|
| X-Band Transceiver | Primary Earth comm | CCSDS |
| UHF Transceiver | Relay comm | Custom |
| Antenna Pointing | Signal tracking | RS-422 |
| Data Buffer | Store-and-forward | Memory |

### 3.3 Power Subsystem

| Component | Function | Interface |
|-----------|----------|-----------|
| Solar Array | Power generation | Analog |
| Battery Pack | Energy storage | I2C |
| Power Distribution | Load management | CAN |
| Power Monitor | Consumption tracking | SPI |

### 3.4 Payload Subsystem

| Instrument | Function | Data Output |
|------------|----------|-------------|
| MastCam | Surface imaging | JPEG/RAW |
| Spectrometer | Composition analysis | Spectrum |
| Drill | Sample collection | Physical |
| Weather Station | Environmental data | CSV |

---

## 4. Design Decisions

### 4.1 Architectural Decisions

| ID | Decision | Rationale | Impact |
|----|----------|-----------|--------|
| AD-001 | Centralized OBC | Simplified integration | Single point of failure |
| AD-002 | CAN Bus for actuators | Proven space-qualified | Limited bandwidth |
| AD-003 | Cold redundancy | Power efficiency | Higher mass |
| AD-004 | Store-and-forward | Communication delays | Buffer sizing |

### 4.2 Quality Attribute Decisions

| Quality Attribute | Solution | Trade-off |
|-------------------|----------|------------|
| Reliability | Watchdog timers | Performance overhead |
| Maintainability | Modular design | Mass increase |
| Performance | Real-time OS | Limited features |
| Safety | Fail-safe modes | Operational complexity |

---

## 5. Interface Definitions

### 5.1 Internal Interfaces

| Interface | Type | Data Format |
|-----------|------|-------------|
| OBC ↔ Navigation | CAN | Binary |
| OBC ↔ Payload | Ethernet | JSON |
| OBC ↔ Power | I2C | Telemetry |
| OBC ↔ Comms | Serial | CCSDS |

### 5.2 External Interfaces

| Interface | Protocol | Purpose |
|-----------|----------|---------|
| GCS ↔ Rover | X-band | Command/Telemetry |
| Relay ↔ Rover | UHF | Data relay |

---

## 6. Component Specifications

### 6.1 On-Board Computer

| Specification | Value |
|---------------|-------|
| Processor | ARM Cortex-A72 |
| Clock Speed | 1.5 GHz |
| Memory | 8 GB RAM |
| Storage | 256 GB SSD |
| Operating System | RTOS (FreeRTOS) |

### 6.2 Sensor Suite

| Sensor | Quantity | Range | Accuracy |
|--------|----------|-------|----------|
| Lidar | 2 | 0.1-50m | ±5cm |
| Stereo Camera | 2 | 0.5-100m | ±10cm |
| IMU | 1 | 360° | 0.1° |
| Wheel Odometer | 6 | N/A | ±1cm |

---

## 7. Appendix

### A. Acronyms
- CAN: Controller Area Network
- CCSDS: Consultative Committee for Space Data Systems
- IMU: Inertial Measurement Unit
- RTOS: Real-Time Operating System

---

## 8. Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | [Date] | [Author] | Initial draft |
| 1.0 | [Date] | [Author] | Baseline |
