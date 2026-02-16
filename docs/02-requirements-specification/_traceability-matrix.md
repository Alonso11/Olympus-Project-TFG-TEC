# Traceability Matrix - Olympus Project

**Document ID:** TM-001  
**Version:** 1.0  
**Standard:** ISO/IEC/IEEE 29148  

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✓ | Directly Traced |
| ↔ | Mutually Dependent |
| ← | Derived From |

---

## 1. Stakeholder Requirements to System Requirements

| SR ID | SR Title | SyR ID | SyR Title | Traceability |
|-------|----------|--------|-----------|--------------|
| SR-001 | Autonomous Navigation | SyR-NAV-001 | Navigation Subsystem | ✓ |
| SR-001 | Autonomous Navigation | SyR-NAV-002 | Obstacle Detection | ✓ |
| SR-001 | Autonomous Navigation | SyR-NAV-003 | Path Planning | ✓ |
| SR-002 | Scientific Data Collection | SyR-SCI-001 | Imaging System | ✓ |
| SR-002 | Scientific Data Collection | SyR-SCI-002 | Sample Collection | ↔ |
| SR-003 | Earth Communication | SyR-COM-001 | Communication Subsystem | ✓ |
| SR-003 | Earth Communication | SyR-COM-002 | Data Buffering | ↔ |
| SR-004 | Extended Operation | SyR-PWR-001 | Power Management | ✓ |
| SR-005 | Safety | SyR-SAF-001 | Fault Detection | ✓ |
| SR-005 | Safety | SyR-SAF-002 | Safe Mode | ✓ |

---

## 2. System Requirements to Software Requirements

| SyR ID | SyR Title | SWR ID | SWR Title | Traceability |
|--------|-----------|--------|-----------|--------------|
| SyR-NAV-001 | Navigation Subsystem | SWR-NAV-001 | Navigation Algorithm | ✓ |
| SyR-NAV-001 | Navigation Subsystem | SWR-NAV-002 | Localization Module | ✓ |
| SyR-NAV-002 | Obstacle Detection | SWR-OBS-001 | Sensor Interface | ✓ |
| SyR-NAV-002 | Obstacle Detection | SWR-OBS-002 | Collision Avoidance | ✓ |
| SyR-NAV-003 | Path Planning | SWR-PATH-001 | Path Planner | ✓ |
| SyR-NAV-03 | Path Planning | SWR-PATH-002 | Replanning Engine | ↔ |
| SyR-SCI-001 | Imaging System | SWR-IMG-001 | Camera Driver | ✓ |
| SyR-SCI-001 | Imaging System | SWR-IMG-002 | Image Processing | ✓ |
| SyR-COM-001 | Communication | SWR-COM-001 | Protocol Handler | ✓ |
| SyR-COM-002 | Data Buffering | SWR-COM-002 | Storage Manager | ✓ |
| SyR-PWR-001 | Power Management | SWR-PWR-001 | Power Monitor | ✓ |
| SyR-PWR-001 | Power Management | SWR-PWR-002 | Battery Controller | ✓ |

---

## 3. Requirements to Architecture

| Req ID | Type | Architecture Element | Component |
|--------|------|---------------------|-----------|
| FR-001 | Functional | Navigation Module | Navigator |
| FR-002 | Functional | Perception Module | ObstacleDetector |
| FR-003 | Functional | Planning Module | PathPlanner |
| FR-010 | Functional | Payload Module | Camera |
| FR-011 | Functional | Payload Module | Spectrometer |
| FR-020 | Functional | Comms Module | Radio |
| FR-030 | Functional | Power Module | PowerManager |
| NFR-001 | Non-Functional | Navigation Module | Performance |
| NFR-010 | Non-Functional | All | Reliability |
| NFR-020 | Non-Functional | Safety Module | SafetyMonitor |

---

## 4. Requirements to Test Cases

| Req ID | Req Title | Test Case ID | Test Type | Status |
|--------|-----------|--------------|-----------|--------|
| FR-001 | Autonomous Navigation | TC-NAV-001 | Integration | Pending |
| FR-002 | Obstacle Detection | TC-OBS-001 | Unit | Pending |
| FR-003 | Path Replanning | TC-PATH-001 | Integration | Pending |
| FR-010 | Image Capture | TC-IMG-001 | Unit | Pending |
| FR-011 | Soil Analysis | TC-SCI-001 | System | Pending |
| FR-020 | Earth Communication | TC-COM-001 | Integration | Pending |
| FR-030 | Power Management | TC-PWR-001 | Unit | Pending |
| NFR-001 | Path Planning Time | TC-PERF-001 | Performance | Pending |
| NFR-010 | System Availability | TC-REL-001 | Reliability | Pending |
| NFR-020 | Collision Avoidance | TC-SAF-001 | Safety | Pending |

---

## 5. Verification Method Cross-Reference

| Req ID | Test | Inspection | Analysis | Demonstration |
|--------|------|------------|----------|---------------|
| FR-001 | ✓ | | | |
| FR-002 | ✓ | | | |
| FR-003 | ✓ | | | |
| FR-010 | | ✓ | | |
| FR-011 | | | ✓ | |
| FR-020 | ✓ | | | |
| FR-030 | ✓ | | | |
| NFR-001 | | | ✓ | |
| NFR-010 | | | ✓ | |
| NFR-020 | | | | ✓ |

---

## 6. Coverage Summary

| Category | Total | Traced | Coverage |
|----------|-------|--------|----------|
| Stakeholder Requirements | 5 | 5 | 100% |
| System Requirements | 12 | 12 | 100% |
| Software Requirements | 14 | 14 | 100% |
| Test Cases | 10 | 10 | 100% |

---

## 7. Maintenance Log

| Date | Change | Author |
|------|--------|--------|
| [Date] | Initial matrix creation | [Author] |
