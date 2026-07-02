# Olympus Project — TFG

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Systems Engineering](https://img.shields.io/badge/Focus-Systems%20Engineering-blue.svg)](#)

## Overview

This repository contains the systems-engineering documentation for the **Olympus Project**
(Final Graduation Project, TFG): the design, integration, and verification of a CPU-only
rover platform built to enable the **physical validation of the ELANaV navigation
software**, previously stalled in simulation (TRL-3).

The work raises the platform to **TRL-4** (subsystems and interfaces integrated in the
laboratory) under real constraints — CPU-only compute, budget, and safety — while keeping
every design decision traceable to a formal SRS.

The engineering priorities, in order, are:
**(1) safety/determinism → (2) formal traceability → (3) honest realism (no over-promising).**

---

## Technical Highlights

- **Dual HLC/LLC architecture** — separates neural compute (Raspberry Pi 5, YOLOv8n-seg,
  ≤2 s cycle) from hard real-time control (low-level controller, Rust `no_std`, 20 ms loop)
  so a software fault cannot compromise physical safety.
- **Reactive navigation** (YOLOv8n-seg); SLAM deferred (CPU-only budget).
- **Formal requirements flow** (IEEE 29148): ConOps → Use Cases → RF/RNF →
  traceability matrix across 7 subsystems.
- **Verification status:** 2 verified / 8 partial / 2 descoped over 12 system requirements.

---

## System Sub-components

The system is split across specialized repositories, one per architectural layer:

- **[Rover Low-Level Controller (LLC)](https://github.com/Alonso11/rover-low-level-controller)** — Firmware in Rust for the ATmega2560. Manages motor control (BTS7960), encoders, ACS712 current sensors, and low-level safety logic.
- **[Olympus HLC (High-Level Controller)](https://github.com/Alonso11/olympus-hlc-rpi5)** — Embedded Linux (Yocto Project) for the Raspberry Pi 5. Handles GNC (Guidance, Navigation, and Control), computer vision, traversability analysis, and high-level communications.
- **Ground Station** — Desktop application (Python/PyQt) for real-time telemetry visualization, manual control, and system monitoring.

---

## Repository Structure

```
Olympus-Project-TFG-TEC/
├── 📄 README.md                       # This file
├── 📄 CHANGELOG.md                    # Version history
├── 📄 LICENSE                         # MIT
├── .github/workflows/                 # CI for documentation quality
│
├── 📂 docs/
│   └── 📂 srs_latex/                  # **SOFTWARE REQUIREMENTS SPECIFICATION (LaTeX)**
│       ├── main.tex                   #   IEEE 29148 SRS document
│       ├── main.pdf                   #   Compiled SRS
│       ├── sections/                  #   s01–s13 (context, ConOps, requirements…)
│       ├── icd/                       #   Interface Control Documents (CSP, UART/LLC)
│       ├── vv/                        #   Verification & Validation procedures
│       ├── figures/
│       └── references.bib
│
├── 📂 templates/                      # Reusable document templates
├── 📂 project_management/             # Meeting notes, decisions, task tracking
└── 📂 references/                     # Supporting research
```

---

## Standards and Compliance

- **ISO/IEC/IEEE 29148:2018** — Requirements Engineering
- **ECSS** (E-ST-10-02C, E-ST-70-11) — referenced for verification and autonomy levels

---

## License

Distributed under the MIT License. See the `LICENSE` file for details.

---

## Author

Fabián Alonso Gómez Quesada
Instituto Tecnológico de Costa Rica (TEC)
School of Electronics Engineering
SETEC Lab — Space Systems Laboratory
