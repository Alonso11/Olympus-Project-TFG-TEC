# Requirements Specification - Olympus Project

**Document ID:** SRS-001  
**Version:** 1.0  
**Date:** [Insert Date]  
**Author:** Fabián Alonso Gómez Quesada  
**Standard:** ISO/IEC/IEEE 29148:2018  

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) document provides a complete description of the autonomous Mars rover system. It specifies the functional and non-functional requirements, interface requirements, and performance criteria.

### 1.2 Scope
The Olympus Project encompasses the design and development of an autonomous rover system capable of:
- Autonomous surface navigation
- Obstacle detection and avoidance
- Scientific data collection
- Earth communication relay

### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|------------|
| rover | Autonomous planetary surface vehicle |
| GCS | Ground Control Station |
| ADCS | Attitude Determination and Control System |
| EPS | Electrical Power System |
| OBC | On-Board Computer |
| TTC | Telemetry, Tracking, and Command |

### 1.4 References
- ISO/IEC/IEEE 29148:2018
- ECSS-E-ST-10C - Systems Engineering
- NASA Mars Exploration Rover Mission Documentation

---

## 2. Overall Description

### 2.1 Product Perspective

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MARS ROVER SYSTEM                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│    ┌─────────────┐      ┌─────────────┐      ┌─────────────┐          │
│    │  Scientific │      │  Navigation │      │ Communication│          │
│    │  Payload    │      │  & Mobility │      │   Subsystem  │          │
│    └──────┬──────┘      └──────┬──────┘      └──────┬──────┘          │
│           │                    │                    │                  │
│           └────────────────────┼────────────────────┘                  │
│                                │                                         │
│                    ┌───────────▼───────────┐                           │
│                    │   On-Board Computer   │                           │
│                    │        (OBC)          │                           │
│                    └───────────┬───────────┘                           │
│                                │                                         │
│           ┌────────────────────┼────────────────────┐                  │
│           │                    │                    │                  │
│    ┌──────▼──────┐      ┌──────▼──────┐      ┌──────▼──────┐          │
│    │  Power &    │      │   Thermal   │      │  Mechanical │          │
│    │  Distribution│      │   Control   │      │   Structure │          │
│    └─────────────┘      └─────────────┘      └─────────────┘          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 User Characteristics

| User Class | Description | Technical Level |
|------------|-------------|-----------------|
| Mission Operators | Ground control team | High |
| Scientists | Data analysis users | Medium-High |
| System Engineers | Maintenance/updates | High |
| Autonomy System | Self-operating | N/A |

### 2.3 Assumptions and Dependencies

- Communication delay: 4-20 minutes (Earth-Mars)
- Power source: Solar panels with battery backup
- Operating environment: Mars surface (-80°C to 20°C)
- Mission duration: 90 sols (Martian days)

---

## 3. Functional Requirements

### 3.1 Autonomous Navigation

| ID | Requirement | Priority | Verification |
|----|-------------|----------|--------------|
| FR-001 | The system shall navigate autonomously from waypoint A to waypoint B | Must | Test |
| FR-002 | The system shall detect obstacles within 5 meters | Must | Test |
| FR-003 | The system shall replan path around detected obstacles | Must | Test |
| FR-004 | The system shall operate at speeds up to 0.1 m/s | Should | Test |
| FR-005 | The system shall localize position with 1m accuracy | Must | Test |

### 3.2 Scientific Payload

| ID | Requirement | Priority | Verification |
|----|-------------|----------|--------------|
| FR-010 | The system shall capture images with minimum 12MP resolution | Must | Test |
| FR-011 | The system shall analyze soil composition | Should | Analysis |
| FR-012 | The system shall collect and store rock samples | Could | Demonstration |
| FR-013 | The system shall transmit scientific data to GCS | Must | Test |

### 3.3 Communication

| ID | Requirement | Priority | Verification |
|----|-------------|----------|--------------|
| FR-020 | The system shall communicate with Earth via X-band | Must | Test |
| FR-021 | The system shall buffer data during communication outages | Must | Test |
| FR-022 | The system shall report status every 15 minutes | Should | Test |

### 3.4 Power Management

| ID | Requirement | Priority | Verification |
|----|-------------|----------|--------------|
| FR-030 | The system shall manage power consumption based on available energy | Must | Test |
| FR-031 | The system shall enter low-power mode when battery < 20% | Must | Test |
| FR-032 | The system shall maximize solar panel efficiency | Should | Analysis |

---

## 4. Non-Functional Requirements

### 4.1 Performance

| ID | Requirement | Metric | Target |
|----|-------------|--------|--------|
| NFR-001 | Path planning cycle time | Latency | < 5 seconds |
| NFR-001 | Obstacle detection response | Latency | < 500 ms |
| NFR-003 | Image processing throughput | Images/minute | ≥ 2 |
| NFR-004 | System startup time | Duration | < 60 seconds |

### 4.2 Reliability

| ID | Requirement | Metric | Target |
|----|-------------|--------|--------|
| NFR-010 | System availability | Uptime | ≥ 95% |
| NFR-011 | Mean Time Between Failures | MTBF | ≥ 1000 hours |
| NFR-012 | Fault detection coverage | Coverage | ≥ 90% |

### 4.3 Safety

| ID | Requirement | Category |
|----|-------------|----------|
| NFR-020 | System shall not collide with obstacles | Collision avoidance |
| NFR-021 | System shall maintain safe temperature range | Thermal |
| NFR-022 | System shall fail to a safe state | Fault tolerance |

### 4.4 Security

| ID | Requirement | Category |
|----|-------------|----------|
| NFR-030 | Commands shall be authenticated | Command validation |
| NFR-031 | Data shall be protected from corruption | Data integrity |

### 4.5 Maintainability

| ID | Requirement | Metric | Target |
|----|-------------|--------|--------|
| NFR-040 | Software update capability | Update method | Remote upload |
| NFR-041 | Mean Time to Repair | MTTR | < 30 minutes |

---

## 5. Interface Requirements

### 5.1 External Interfaces

#### 5.1.1 Ground Control Station Interface

| Interface | Protocol | Data Rate |
|-----------|----------|-----------|
| Uplink | X-band | 2 kbps |
| Downlink | X-band | 256 kbps |
| Emergency | UHF | 8 kbps |

#### 5.1.2 User Interfaces
- Command console for mission operators
- Data visualization dashboard for scientists
- Alert system for anomalies

### 5.2 Internal Interfaces

| Interface | Description |
|-----------|-------------|
| OBC ↔ Sensors | SPI/I2C |
| OBC ↔ Actuators | CAN Bus |
| Subsystem ↔ EPS | Power bus |

---

## 6. Data Requirements

### 6.1 Data Types

| Data Category | Format | Storage |
|---------------|--------|---------|
| Images | JPEG/RAW | 32 GB |
| Telemetry | Binary | 1 GB |
| Science Data | CSV/JSON | 5 GB |
| Logs | Text | 500 MB |

---

## 7. Appendix

### A. Requirements Traceability Summary
[Link to traceability matrix](./_traceability-matrix.md)

### B. Glossary
- **Sol:** Martian day (24 hours, 39 minutes)
- **Waypoint:** Designated navigation target
- **Attitude:** Orientation in space

---

## 8. Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | [Date] | [Author] | Initial draft |
| 1.0 | [Date] | [Author] | Baseline release |
