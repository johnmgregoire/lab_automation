# Lab automation with python

## Task servers
Independent services, synchronization handled by client
- Motion
  - Report position
  - Move to position
  - Abort motion
  - Check status (ready, moving, locked)
- Measurement
  - Signal input / output
  - Data aquisition
  - Potentiostat control
  - Broadcast live data
  - Check status (idle, measuring)
- Display
  - Dashboard
  - Live measurement view
  - Saved data inspection

## Automation setup (client)
- Handles motion calibration
- Generates ordered sample / position list for measurement
- Generates technique list and parameters
- Defines pre/post/maintenance actions
- Writes automation parameters to disk

## Automation scheduler (client)
- Executes experiment techniques in order
- Control (start, stop now, stop after sample)
- Writes scheduler state to disk
- Packages data (rcp, exp, ana)