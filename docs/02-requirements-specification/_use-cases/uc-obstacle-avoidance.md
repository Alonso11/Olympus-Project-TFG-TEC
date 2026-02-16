# Use Case: Obstacle Avoidance

**Use Case ID:** UC-OBS-001  
**Version:** 1.0  

---

## 1. Description
The rover shall detect and avoid obstacles during autonomous navigation to prevent collisions.

## 2. Actors
- Perception Module (primary)
- Navigation Module
- Obstacle Detection Sensors

## 3. Preconditions
- Rover is in autonomous navigation mode
- Obstacle detection sensors are operational
- Path execution is in progress

## 4. Basic Flow

| Step | Actor | Action |
|------|-------|--------|
| 1 | Sensors | Continuously scan environment |
| 2 | Perception | Process sensor data |
| 3 | Perception | Identify obstacles in path |
| 4 | Navigation | Assess collision risk |
| 5 | Navigation | Execute avoidance maneuver |
| 6 | Navigation | Resume original path |

## 5. Alternative Flows

### 5.1 Unavoidable Obstacle
| Step | Action |
|------|--------|
| 5a | Determine no safe path |
| 5b | Initiate emergency stop |
| 5c | Report to GCS |

### 5.2 Multiple Obstacles
| Step | Action |
|------|--------|
| 4a | Identify all obstacles in range |
| 5a | Compute combined avoidance path |
| 5b | Execute multi-obstacle maneuver |

## 6. Postconditions
- No collision has occurred
- Rover has circumvented obstacle
- Navigation continues toward goal

## 7. Success Criteria
- Zero collisions in 100 test runs
- Detection range ≥ 5 meters
- Response time < 500ms
