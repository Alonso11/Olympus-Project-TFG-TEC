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

To start the Ground Station GUI (using XCB for compatibility with Wayland/Linux environments):

```bash
QT_QPA_PLATFORM=xcb uv run --with PyQt5 python olympus_gui.py
```

*Note: The `--with PyQt5` flag ensures the dependency is available in the ephemeral or project environment during execution.*

## Features

- **Real-time Telemetry**: Monitoring of motor currents, battery levels, and sensor data.
- **Manual Control**: Interface for driving the rover and controlling subsystems.
- **Visual Feedback**: Integration with the HLC camera stream (via OpenCV).
- **Network Discovery**: Automatic connection to the Olympus HLC via CSP/UDP.

## Troubleshooting

- **Qt Platform Issues**: If you encounter issues with the GUI not starting on Linux, ensure you have the necessary X11/Wayland libraries installed.
- **Connection**: Verify that your computer is on the same network as the Olympus Rover HLC.

---

## Running in Docker

The Ground Station is containerized so you don't need to install PyQt5 / OpenCV /
Python on the host. The container runs the same `olympus_gui.py`, reusing your
host's X11 display, SSH agent, and `~/.ssh` keys so it can reach the Pi exactly
like the host can.

**Build the image (from the repo root):**
```bash
docker build -t olympus-gs -f ground_station/Dockerfile .
```

### GUI mode (default)

Allow the container to use your X server once, then run:
```bash
xhost +local:$(id -un)
docker run --rm -it \
  --network host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -v "$SSH_AUTH_SOCK:/ssh-agent" -e SSH_AUTH_SOCK=/ssh-agent \
  -v "$(pwd)/ground_station/logs:/app/logs" \
  olympus-gs gui
```
After you're done you can revoke the X grant: `xhost -local:$(id -un)`.

### Headless telemetry capture (no display needed)

`tcp_capture.py` connects to the running HLC station and records TLM / CMD / DET / EVT
as evidence. The image exposes it via the `capture` mode:
```bash
docker run --rm -it --network host \
  -v "$(pwd)/ground_station/evidencia_tesis:/app/evidencia_tesis" \
  olympus-gs capture 172.21.255.241 30 MODE:AUTO
```

### One-shot TCP client

`tcp_client.py` is the thin interactive client for sending commands:
```bash
docker run --rm -it --network host \
  olympus-gs client 172.21.255.241 EXP:40:40 STB
```

### With Docker Compose

A convenience `docker-compose.yml` lives in `ground_station/docker/`:
```bash
cd ground_station/docker
docker compose run --rm gs gui
docker compose run --rm gs capture 172.21.255.241 30
docker compose run --rm gs client  172.21.255.241 --auto 10
```

### Files written by the container

| Path in container | Host mount (Compose) | Purpose |
|---|---|---|
| `/app/logs`  | `ground_station/logs` | GUI CSV/comm logs |
| `/app/evidencia_tesis` | `ground_station/evidencia_tesis` | Capture-script evidence dir |

### Notes
- `network_mode: host` is used because the GUI talks to the Pi on TCP 5005/5006
  and reuses the host SSH agent for `ssh`/`scp` to the HLC. On macOS/Windows
  (where host networking is not available) you'll need to publish the ports
  and use the bridge network with `--add-host`.
- The image runs as the host UID/GID when invoked via Compose so log files
  written into the mounted volume are owned by you, not root.

---

## Running in Docker (VNC variant — macOS / Windows / headless hosts)

If you're on Docker Desktop, or a host without an X server, the GUI can't
borrow the host display. The **VNC variant** runs a virtual framebuffer
(`Xvfb`) + VNC server (`x11vnc`) + a noVNC web client inside the container,
so you drive the same PyQt5 GUI from any browser.

**Build:**
```bash
docker build -t olympus-gs-vnc -f ground_station/Dockerfile.vnc .
```

**Run — then open <http://localhost:8080/vnc.html> in a browser:**
```bash
docker run --rm -it \
  -p 8080:8080 -p 5900:5900 \
  -v "$(pwd)/ground_station/logs:/app/logs" \
  -v "$(pwd)/ground_station/evidencia_tesis:/app/evidencia_tesis" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  olympus-gs-vnc gui
```
- **Web (recommended):** <http://localhost:8080/vnc.html> — works from any browser.
- **VNC viewer:** `localhost:5900` — password `olympus` (override with `-e VNC_PASSWORD=...`).
- **Resolution:** defaults to `1280x720`; override with `-e RESOLUTION=1920x1080x16`.

The VNC image still supports the same `capture` and `client` headless modes
(no X server involved) — they just bypass the framebuffer:
```bash
docker run --rm olympus-gs-vnc capture 172.21.255.241 30 MODE:AUTO
```

### With Docker Compose (both variants)

`ground_station/docker/docker-compose.yml` defines two services:

| Service | Use case | Command |
|---|---|---|
| `gs` (default) | Linux host with X11 | `docker compose run --rm gs gui` |
| `gsvnc` | Docker Desktop / macOS / Windows / headless | `docker compose --profile vnc up gsvnc` |

The VNC one is opt-in via a Compose `profile` so the default `docker compose up`
won't try to start it. Tunables via env: `GS_RESOLUTION`, `GS_VNC_PASSWORD`.
