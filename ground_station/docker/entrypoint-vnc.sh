#!/usr/bin/env sh
# entrypoint-vnc.sh — start Xvfb + x11vnc + noVNC, then launch the GUI inside.
#
# Modes:
#   docker run -p 8080:8080 olympus-gs-vnc                 # GUI on :8080 web
#   docker run -p 8080:8080 olympus-gs-vnc capture h 30     # headless capture
#   docker run -p 8080:8080 olympus-gs-vnc client  h "EXP:40:40"
set -e

# Headless modes don't need X at all.
case "${1:-gui}" in
  capture|client)
    cd /app
    if [ "$1" = "capture" ]; then exec python3 tcp_capture.py "$@"; fi
    shift
    exec python3 tcp_client.py "$@"
    ;;
esac

cd /app

# --- Bring up a virtual X server -------------------------------------------
# Xvfb on :1 at the configured resolution.
Xvfb :1 -screen 0 "$RESOLUTION" -nolisten tcp &
XVFB_PID=$!

# Give Xvfb a moment to come up.
sleep 1

# Start x11vnc on :1, mirrored to port 5900 with a password.
mkdir -p /root/.vnc
x11vnc -display :1 -rfbport 5900 -rfbauth <(printf '%s\n' "$VNC_PASSWORD" | x11vnc -storepasswd - 2>/dev/null | awk '{print $NF}') \
       -forever -shared -bg -o /tmp/x11vnc.log -quiet 2>/dev/null || true

# noVNC web client → bridge port 8080 to the VNC port 5900.
websockify --web /usr/share/novnc/ "$NOVNC_PORT" localhost:5900 >/tmp/novnc.log 2>&1 &
WS_PID=$!

# Print connection info to the container log so the user knows where to point a browser.
cat <<EOF
─────────────────────────────────────────────────────────────────
 Olympus Ground Station (VNC variant)
─────────────────────────────────────────────────────────────────
  • Web browser (recommended) : http://localhost:8080/vnc.html
  • VNC viewer (any client)   : localhost:5900
  • VNC password              : $VNC_PASSWORD
─────────────────────────────────────────────────────────────────
EOF

# Run the GUI inside the virtual frame buffer. Block on it; tear down on exit.
python3 olympus_gui.py &
GUI_PID=$!

# Forward signals to the GUI.
trap 'kill $GUI_PID $WS_PID $XVFB_PID 2>/dev/null; exit 0' INT TERM
wait "$GUI_PID"
RC=$?
kill "$WS_PID" "$XVFB_PID" 2>/dev/null || true
exit $RC