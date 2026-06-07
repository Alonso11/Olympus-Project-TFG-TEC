# Olympus Project - TFG

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Systems Engineering](https://img.shields.io/badge/Focus-Systems%20Engineering-blue.svg)](#)

## Overview

This repository contains the development of the Final Graduation Project (TFG) for the Olympus Project. The project is based on the application of Systems Engineering methodologies for the design, analysis, and execution of complex technological solutions.

The main focus lies on requirements traceability, modular architecture design, and systematic validation processes to ensure system integrity.

---

## Systems Engineering Methodology

The development cycle is governed by the following engineering pillars:
- **Stakeholder Analysis**: Identification and management of critical needs.
- **Requirements Engineering**: Rigorous definition of functional and technical specifications.
- **Architecture Design**: Modular structuring following industry standards.
- **Validation**: Systematic validation procedures to ensure quality and stakeholder needs are met.

## System Sub-components

The project is divided into several specialized repositories that handle different layers of the system:

- **[Rover Low-Level Controller](https://github.com/Alonso11/rover-low-level-controller)**: Firmware developed in Rust for the ATmega2560. Manages motor control (BTS7960), encoders, ACS712 current sensors, and low-level safety logic.
- **[Olympus HLC (High-Level Controller)](https://github.com/Alonso11/olympus-hlc-rpi5)**: Embedded Linux system (Yocto Project) for the Raspberry Pi 5. Handles GNC (Guidance, Navigation, and Control), computer vision, traversability analysis, and high-level communications.

---

## Repository Structure

```
olympus-project/
├── 📄 README.md                          # This file - project overview and navigation
├── 📄 CHANGELOG.md                       # Document version history and changes
├── .github/workflows/                    # CI/CD for documentation quality
│   └── markdown-check.yml
│
├── 📂 docs/                              # Main documentation folder
│   ├── 📄 00-project-charter.md          # Project vision, scope, objectives, stakeholders
│   ├── 📄 01-requirements-framework.md   # Complete ISO/IEC/IEEE 29148 framework
│   ├── 📄 02-requirements-specification/ # **CORE SRS FOLDER**
│   │   ├── 📄 index.md                   # Main SRS document
│   │   ├── 📄 _traceability-matrix.md    # Live requirements traceability matrix
│   │   ├── 📂 _use-cases/                # Detailed operational scenarios
│   │   │   ├── uc-autonomous-navigation.md
│   │   │   ├── uc-obstacle-avoidance.md
│   │   │   └── uc-emergency-stop.md
│   │   └── 📂 _diagrams/                 # System architecture and flow diagrams
│   │       ├── system-context.mmd
│   │       ├── navigation-flow.mmd
│   │       └── safety-architecture.mmd
│   │
│   ├── 📄 03-architecture-design.md      # System and software architecture
│   ├── 📄 04-validation.md               # Validation procedures and results
│   ├── 📄 05-stakeholder-analysis.md     # Detailed stakeholder requirements mapping
│   └── 📄 06-implementation-roadmap.md   # Project execution plan
│
├── 📂 templates/                         # Reusable document templates
│   ├── srs-template.md
│   └── traceability-template.md
│
├── 📂 project_management/                # Meeting notes, decisions, task tracking
│   ├── meeting-notes/
│   ├── stakeholder-interviews/
│   └── project-kamban.md
│
└── 📂 references/                        # Supporting documents and research
    ├── mars-rover-case-studies.md
    └── [additional-reference-files.md]
```

---

## Standards and Compliance

This project follows:
- **ISO/IEC/IEEE 29148:2018** - Systems and Software Engineering - Requirements Engineering
- **ISO/IEC/IEEE 12207** - Software Life Cycle Processes
- **ISO/IEC/IEEE 15288** - System Life Cycle Processes

---

## License

This project is distributed under the MIT License. See the LICENSE file for details.

---

## Author

Fabián Alonso Gómez Quesada     
Instituto Tecnológico de Costa Rica (TEC)        
School of Electronics Engineering           
SETEC Lab – Space Systems Laboratory                  
