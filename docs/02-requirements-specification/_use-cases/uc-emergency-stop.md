# Use Case: Emergency Stop

**Use Case ID:** UC-EMG-001  
**Version:** 1.0  

---

## 1. Description
The rover shall execute an immediate safe stop upon detecting a critical fault or receiving an emergency command.

## 2. Actors
- Safety Monitor (primary)
- Navigation Module
- Power Module
- Ground Control Station

## 3. Preconditions
- Rover is in operational state

## 4. Trigger Conditions
- Ground command received
- Critical sensor failure detected
- Collision imminent
- Power level critical
- Thermal limit exceeded

## 5. Basic Flow

| Step | Actor | Action |
|------|-------|--------|
| 1 | Safety Monitor | Detect emergency condition |
| 2 | Navigation | Halt all movement commands |
| 3 | Power | Disable non-essential systems |
| 4 | Thermal | Activate thermal protection |
| 5 | Comms | Transmit emergency alert to GCS |
| 6 | System | Enter safe mode |

## 6. Postconditions
- All motion stopped
- Non-essential systems disabled
- GCS notified of emergency
- System in safe mode

## 7. Recovery
- Wait for GCS command
- System diagnostic upon request
- Resume operation only after GCS authorization

## 8. Success Criteria
- Stop within 1 second of trigger
- No damage to systems
- GCS notification within 2 minutes
- Safe mode entered successfully
