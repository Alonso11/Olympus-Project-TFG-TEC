# syntax=docker/dockerfile:1.7
# Olympus Ground Station — container image
#
# Two launch modes (entrypoint auto-detects the first arg):
#   1) GUI mode    : docker run ... olympus-gs                 (default)
#   container → host X11 via /tmp/.X11-unix + DISPLAY
#   2) Capture     : docker run ... olympus-gs capture <host> <secs> [cmd]
#   3) Raw client  : docker run ... olympus-gs client  <host> [cmds...]
#
# Host networking is recommended (the GUI opens TCP 5005/5006 to the Pi and
# reuses the host's SSH agent/keys).

FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    QT_QPA_PLATFORM=xcb \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

# Runtime: X11 libs for Qt's xcb plugin + dbus (Qt needs a session bus) + fonts
# + openssh-client so the GUI can reuse the host SSH agent/keys for the Pi.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libxkbcommon0 libxkbcommon-x11-0 \
        libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 \
        libxcb-render-util0 libxcb-shape0 libxcb-sync1 libxcb-xfixes0 \
        libxcb-xinerama0 libxcb-xkb1 libxcb-cursor0 \
        libegl1 libgl1 libglib2.0-0 libfontconfig1 libdbus-1-3 \
        fonts-dejavu-core \
        openssh-client \
        xauth \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (better layer caching)
COPY ground_station/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the station code (and helpers)
COPY ground_station/ /app/

# Directory for the CSV/log evidence that the GUI + capture scripts write.
RUN mkdir -p /app/logs /app/evidencia_tesis && \
    ln -s /app/evidencia_tesis /root/evidencia_tesis

COPY ground_station/docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["gui"]