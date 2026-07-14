#!/usr/bin/env sh
# entrypoint.sh — auto-selects GUI / capture / client mode.
#
# Usage:
#   docker run ... olympus-gs                       # → GUI (default)
#   docker run ... olympus-gs gui                   # → GUI
#   docker run ... olympus-gs capture <host> <secs> [cmd]
#   docker run ... olympus-gs client  <host> [cmds...]
#   docker run ... olympus-gs sh                    # → interactive shell
set -e

cd /app

case "${1:-gui}" in
  gui)
    exec python3 olympus_gui.py
    ;;
  capture)
    shift
    exec python3 tcp_capture.py "$@"
    ;;
  client)
    shift
    exec python3 tcp_client.py "$@"
    ;;
  sh|bash)
    exec "$@"
    ;;
  *)
    # Treat unknown first arg as if the user ran the GUI with arguments
    # (e.g. passing an alternate PI host). Falls back to GUI.
    exec python3 olympus_gui.py "$@"
    ;;
esac