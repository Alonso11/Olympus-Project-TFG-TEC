# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Repository structure with ISO/IEC/IEEE 29148 compliance folders
- GitHub issue templates (requirement, stakeholder, compliance)
- CI/CD workflow for documentation quality checks
- Use cases for autonomous navigation, obstacle avoidance, emergency stop
- Mermaid diagrams for system context, navigation flow, safety architecture

### Planned
- Requirements traceability matrix automation
- GitHub Releases for SRS milestones

---

## [1.0.0] - YYYY-MM-DD

### Added
- Project Charter (00-project-charter.md)
- Requirements Framework (01-requirements-framework.md)
- Requirements Specification (02-requirements-specification/index.md)
- Traceability Matrix (02-requirements-specification/_traceability-matrix.md)
- Architecture Design Document (03-architecture-design.md)
- Validation Plan and Report (04-validation.md, validation-report.md)
- Stakeholder Analysis (05-stakeholder-analysis.md)
- Implementation Roadmap (06-implementation-roadmap.md)
- Mars Rover Case Studies (references/mars-rover-case-studies.md)
- SRS and Traceability Templates (templates/)

### Documentation
- README.md with complete repository structure
- Project Kanban board integration

---

## Template Usage

### Adding New Requirements
1. Create GitHub Issue using `requirement` template
2. Get requirement ID assigned (FR-XXX, NFR-XXX)
3. Add to SRS (02-requirements-specification/index.md)
4. Update Traceability Matrix
5. Link to design and validation items

### Document Versioning
- Major changes: New release (v1.0, v2.0)
- Minor changes: Update within release
- Use GitHub Releases for milestones
