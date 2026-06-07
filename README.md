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
- **Ground Station**: Desktop application based on Python/PyQt for real-time telemetry visualization, manual control, and system monitoring.

---

## Repository Structure

```
olympus-project/
├── 📄 README.md                          # This file - project overview and navigation
├── 📄 CHANGELOG.md                       # Document version history and changes
├── .github/workflows/                    # CI/CD for documentation quality
│   └── markdown-check.yml
│
├── 📂 ground_station/                    # Telemetry and control GUI application
│   ├── 📄 olympus_gui.py                 # PyQt Main Interface
│   └── 📄 olympus_station.py             # Communication and protocol logic
│
├── 📂 docs/                              # Project documentation
│   ├── 📂 srs_latex/                     # **CORE SRS SOURCE (LaTeX)**
│   │   ├── 📄 main.tex                   # Main document structure
│   │   ├── 📂 sections/                  # SRS sections (ISO/IEC/IEEE 29148)
│   │   ├── 📂 figures/                   # System diagrams and architecture
│   │   └── 📂 icd/                       # Interface Control Documents
│   │
│   └── 📄 validation_results.md          # Summary of V&V activities
│
├── 📂 ground_station/                    # Telemetry and control GUI application
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
