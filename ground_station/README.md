# Olympus Ground Station

Desktop application for real-time telemetry visualization, manual control, and system monitoring of the Olympus Rover. Built with **Python** and **PyQt5**.

## Prerequisites

This project uses [**uv**](https://github.com/astral-sh/uv) for fast and reliable Python package management. 

Make sure you have `uv` installed:
```bash
curl -LsSf https://astral-sh.uv.io/install.sh | sh
```

## Setup and Installation

1. **Navigate to the ground station directory**:
   ```bash
   cd ground_station
   ```

2. **Initialize the environment and install dependencies**:
   ```bash
   uv venv
   source .venv/bin/activate  # On Linux/macOS
   # .venv\Scripts\activate  # On Windows
   
   uv pip install pyqt5 opencv-python numpy
   ```

   *Note: If `rover_bridge` is a local or specialized dependency, ensure it is available in your Python path or installed via uv.*

## Running the Application

To start the Ground Station GUI:

```bash
uv run olympus_gui.py
```

## Features

- **Real-time Telemetry**: Monitoring of motor currents, battery levels, and sensor data.
- **Manual Control**: Interface for driving the rover and controlling subsystems.
- **Visual Feedback**: Integration with the HLC camera stream (via OpenCV).
- **Network Discovery**: Automatic connection to the Olympus HLC via CSP/UDP.

## Troubleshooting

- **Qt Platform Issues**: If you encounter issues with the GUI not starting on Linux, ensure you have the necessary X11/Wayland libraries installed.
- **Connection**: Verify that your computer is on the same network as the Olympus Rover HLC.
