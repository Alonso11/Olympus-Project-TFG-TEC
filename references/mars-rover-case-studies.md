# Mars Rover Case Studies - Reference Material

This document compiles relevant case studies from Mars rover missions for the Olympus Project requirements analysis.

---

## 1. NASA Mars Exploration Rovers (MER)

### 1.1 Mission Overview
- **Vehicles:** Spirit (MER-A), Opportunity (MER-B)
- **Launch:** 2003
- **Landing:** January 2004
- **Duration:** Spirit: 2009 days | Opportunity: 5498 days

### 1.2 Key Technical Specifications

| Parameter | Specification |
|-----------|---------------|
| Mass | ~185 kg |
| Dimensions | 1.6m × 2.3m × 1.5m |
| Speed | 0.05 m/s (max) |
| Power | 140W (solar array) |
| Communications | X-band, UHF |

### 1.3 Lessons Learned

| Lesson | Application |
|--------|-------------|
| Dust accumulation on panels | Implement cleaning strategies |
| Wheel motor failures | Redundancy in actuators |
| Flash memory wear | Wear-leveling algorithms |
| Thermal management | Passive cooling design |

---

## 2. NASA Curiosity (MSL)

### 2.1 Mission Overview
- **Vehicle:** Curiosity (Mars Science Laboratory)
- **Launch:** 2011
- **Landing:** August 2012
- **Status:** Operational

### 2.2 Key Technical Specifications

| Parameter | Specification |
|-----------|---------------|
| Mass | 899 kg (rover) |
| Dimensions | 3.0m × 2.7m × 2.2m |
| Speed | 0.14 m/s (max) |
| Power | RTG (110W continuous) |
| Computer | RAD750 (110 MHz) |

### 2.3 Autonomous Capabilities

| Capability | Description |
|------------|-------------|
| Autonomous Navigation | Stereo vision for obstacle detection |
| Target Selection | Laser-induced breakdown spectroscopy |
| Terrain Assessment | Visual odometry |

---

## 3. NASA Perseverance (Mars 2020)

### 3.1 Mission Overview
- **Vehicle:** Perseverance
- **Launch:** July 2020
- **Landing:** February 2021
- **Status:** Operational

### 3.2 Key Technical Specifications

| Parameter | Specification |
|-----------|---------------|
| Mass | 1025 kg |
| Dimensions | 3.0m × 2.7m × 2.2m |
| Speed | 0.15 m/s (max) |
| Power | RTG (110W continuous) |
| Computer | PowerPC RAD750 |

### 3.3 Advanced Autonomy

| Feature | Description |
|---------|-------------|
| Terrain-Relative Navigation | Visual landmark matching |
| AutoNav | End-to-end autonomous driving |
| Sample Caching | Autonomous sample collection |
| Ingenuity Helicopter | Aerial reconnaissance |

---

## 4. ESA ExoMars Rover (Rosalind Franklin)

### 4.1 Mission Overview
- **Vehicle:** Rosalind Franklin
- **Planned Launch:** 2028
- **Partner:** ESA, Roscosmos

### 4.2 Key Technical Specifications

| Parameter | Specification |
|-----------|---------------|
| Mass | ~300 kg |
| Dimensions | 2.5m × 2.2m × 1.8m |
| Speed | 0.07 m/s (max) |
| Power | Solar + Battery |
| Drill Depth | 2 meters |

---

## 5. Comparative Analysis

### 5.1 Autonomy Comparison

| Feature | Spirit/Opportunity | Curiosity | Perseverance |
|---------|-------------------|-----------|--------------|
| AutoNav | Basic | Advanced | Full |
| Visual Odometry | Yes | Yes | Enhanced |
| Local Navigation | 2m lookahead | 10m lookahead | 50m+ |
| Decision Speed | Hours | Minutes | Real-time |

### 5.2 Communication Systems

| System | MER | MSL | Mars 2020 |
|--------|-----|-----|-----------|
| Primary | X-band | X-band | X-band |
| Direct-to-Earth | Yes | Yes | Yes |
| Relay (MRO) | UHF | UHF | UHF |
| Relay (Maven) | - | UHF | UHF |
| Helicopter Comm | - | - | Wi-Fi |

---

## 6. Requirements Derivation

### 6.1 From Case Studies to Requirements

| Case Study Finding | Derived Requirement |
|--------------------|---------------------|
| Dust accumulation impact | Power management under dust |
| Wheel failures | Actuator redundancy |
| Communication delays | Autonomous operation capability |
| Scientific payload needs | Modular instrument bay |
| Landing precision | Terrain-relative navigation |

### 6.2 Recommended Best Practices

1. **Modular Architecture**: Enable payload interchangeability
2. **Redundancy**: Critical systems should have backups
3. **Autonomy Level**: Design for 15+ minute communication delays
4. **Fault Detection**: Implement comprehensive health monitoring
5. **Power Budget**: Plan for 50% power degradation over mission life

---

## 7. References

- NASA Mars Exploration Rovers: https://mars.nasa.gov/mer/
- NASA Curiosity: https://mars.nasa.gov/msl/
- NASA Perseverance: https://mars.nasa.gov/perseverance/
- ESA ExoMars: https://www.esa.int/exomars/

---

## 8. Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | [Date] | [Author] | Initial case study compilation |
