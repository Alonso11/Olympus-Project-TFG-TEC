# Stakeholder Analysis - Olympus Project

**Document ID:** SA-001  
**Version:** 1.0  
**Standard:** ISO/IEC/IEEE 29148:2018  

---

## 1. Introduction

### 1.1 Purpose
This document identifies and analyzes all stakeholders, their needs, expectations, and influence on the project.

### 1.2 Scope
- Identify all stakeholder groups
- Capture stakeholder requirements
- Analyze stakeholder influence and interest
- Map requirements to stakeholders

---

## 2. Stakeholder Identification

### 2.1 Stakeholder Register

| ID | Stakeholder | Type | Description |
|----|-------------|------|-------------|
| STK-001 | Academic Institution | Organization | Instituto Tecnológico de Costa Rica |
| STK-002 | Project Director | Individual | Academic advisor and evaluator |
| STK-003 | Development Team | Group | System developers and engineers |
| STK-004 | Scientific Community | Group | End users of rover data |
| STK-005 | Mission Operations | Group | Ground control operators |
| STK-006 | Safety Review Board | Group | Safety certification authority |

---

## 3. Stakeholder Needs Analysis

### 3.1 Needs Matrix

| Stakeholder | Primary Need | Secondary Need | Priority |
|-------------|--------------|-----------------|----------|
| STK-001 | Academic validation | Technical excellence | High |
| STK-002 | Complete documentation | Demonstrable methodology | High |
| STK-003 | Clear requirements | Feasible specifications | Medium |
| STK-004 | Quality scientific data | Reliable operations | High |
| STK-005 | Reliable communication | Autonomous operation | High |
| STK-006 | Safety assurance | Compliance verification | Critical |

---

## 4. Stakeholder Requirements Mapping

### 4.1 Requirements Attribution

| SR ID | Requirement | Source Stakeholder | Priority |
|-------|-------------|---------------------|----------|
| SR-001 | Autonomous Navigation | STK-004, STK-005 | Must |
| SR-002 | Scientific Data Collection | STK-004 | Must |
| SR-003 | Earth Communication | STK-005 | Must |
| SR-004 | Extended Operation | STK-004, STK-005 | Should |
| SR-005 | Safety | STK-006 | Must |

---

## 5. Influence/Interest Grid

```
                        Interest
                    Low         High
              ┌──────────┬──────────┐
       High   │  Monitor  │  Keep     │
   Influence  │           │  Satisfied│
              ├──────────┼──────────┤
       Low    │   Keep   │   Keep    │
              │  Informed │  Involved │
              └──────────┴──────────┘
```

| Stakeholder | Influence | Interest | Strategy |
|-------------|------------|----------|----------|
| STK-001 | High | High | Keep Satisfied |
| STK-002 | High | High | Keep Satisfied |
| STK-003 | Medium | High | Keep Involved |
| STK-004 | Low | High | Keep Informed |
| STK-005 | Medium | High | Keep Involved |
| STK-006 | High | High | Keep Satisfied |

---

## 6. Communication Plan

| Stakeholder | Frequency | Channel | Content |
|-------------|-----------|---------|---------|
| STK-001 | Monthly | Report | Progress, milestones |
| STK-002 | Bi-weekly | Meeting | Technical review |
| STK-003 | Weekly | Meeting | Task updates |
| STK-004 | Monthly | Email | Requirements feedback |
| STK-005 | As needed | Email | Operational scenarios |
| STK-006 | Milestone | Review | Safety assessment |

---

## 7. Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | [Date] | [Author] | Initial draft |
| 1.0 | [Date] | [Author] | Baseline |
