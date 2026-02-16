# Use Case: Autonomous Navigation

**Use Case ID:** UC-NAV-001  
**Version:** 1.0  

---

## 1. Description
The rover shall autonomously navigate from a starting position to a designated waypoint.

## 2. Actors
- On-Board Computer (primary)
- Navigation Module
- Ground Control Station (secondary)

## 3. Preconditions
- Rover is in operational state
- Waypoint coordinates are known
- Localization system is functioning

## 4. Basic Flow

| Step | Actor | Action |
|------|-------|--------|
| 1 | GCS | Send waypoint coordinates |
| 2 | OBC | Receive and validate waypoint |
| 3 | Navigation | Compute path to waypoint |
| 4 | Navigation | Execute movement commands |
| 5 | Sensors | Monitor position continuously |
| 6 | Navigation | Confirm waypoint arrival |

## 5. Alternative Flows

### 5.1 Obstacle Detected
| Step | Action |
|------|--------|
| 4a | Detect obstacle in path |
| 4b | Replan path around obstacle |
| 4c | Resume navigation |

### 5.2 Communication Loss
| Step | Action |
|------|--------|
| 4a | Continue autonomous operation |
| 4b | Log navigation data |
| 4c | Resume communication when available |

## 6. Postconditions
- Rover has reached waypoint within specified accuracy
- Navigation log is recorded

## 7. Success Criteria
- Arrives within 1m of waypoint
- No collisions occur
- Completion reported to GCS
