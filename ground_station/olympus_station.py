#!/usr/bin/env python3
# olympus_station.py — daemon de la estacion de tierra Olympus (corre en la RPi5).
#
# Unifica en un proceso: camara (rpicam-vid MJPEG) + control del Mega (rover_bridge)
# + inferencia YOLO (cv2.dnn, NO onnxruntime) + telemetria. La GUI del portatil es
# un cliente delgado que se conecta por TCP (el WiFi del campus bloquea UDP pero no TCP).
#
# Puertos:
#   5005  video    : daemon -> GUI, frames [4 bytes len big-endian][JPEG]
#   5006  control  : bidireccional, texto por lineas
#       GUI -> daemon : "MODE:MANUAL" | "MODE:AUTO" | "EXP:l:r" | "STB" | "RST" | "AVD:L" ...
#       daemon -> GUI : "TLM:<frame>"  "CMD:<cmd>"  "DET:x1,y1,x2,y2,conf;..."  "EVT:..."
#
# Seguridad: keepalive PING al Mega cada 1s; dead-man -> STB si en modo manual la GUI
# deja de mandar EXP/CLB por DEADMAN_S, o si el cliente de control se desconecta.

import os, re, socket, struct, subprocess, threading, time

SERIAL      = "/dev/arduino_mega"
BAUD        = 115200
MODEL       = "/usr/share/olympus/models/yolov8n.onnx"
W, H, FPS   = 640, 480, 10
VIDEO_PORT  = 5005
CTRL_PORT   = 5006
DEADMAN_S   = 1.2
CONF_MIN    = 0.5
AREA_MIN    = 0.05
ZONE_L      = 0.33
ZONE_R      = 0.67
EXP_L, EXP_R = 25, 25
INFER_EVERY = 3          # inferir 1 de cada N frames (aliviar CPU)

import rover_bridge
import cv2
import numpy as np

# ── Conexion al Mega ──────────────────────────────────────────────────────────
rover = rover_bridge.Rover(SERIAL, BAUD)
time.sleep(2.5)                      # el Mega se resetea al abrir el puerto
rlock = threading.Lock()

def rcmd(c):
    with rlock:
        try:
            return rover.send_command(c)
        except Exception as e:
            return "ERR:%s" % e

def rtlm():
    with rlock:
        try:
            return rover.recv_tlm()
        except Exception:
            return None

# ── Estado compartido ─────────────────────────────────────────────────────────
slock = threading.Lock()
state = {
    "mode": "MANUAL",        # MANUAL | AUTO
    "last_drive": 0.0,
    "drive_active": False,
    "latest_jpeg": None,
    "cmd": "STB",
    "dets": [],              # [(x1,y1,x2,y2,conf)] normalizado 0..1
    "tlm": "",               # ultimo frame TLM crudo ("TLM:...")
}

# ── Modelo YOLO (cv2.dnn) ─────────────────────────────────────────────────────
net = cv2.dnn.readNetFromONNX(MODEL)
print("modelo YOLO cargado", flush=True)

def infer(frame):
    """Devuelve (detecciones_norm, comando_MSM) para un frame BGR."""
    blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (640, 640), swapRB=True, crop=False)
    net.setInput(blob)
    out = net.forward()[0].T          # (8400, 84)
    dets = []
    best_area, best_cx = 0.0, None
    for p in out:
        scores = p[4:]
        cid = int(np.argmax(scores))
        conf = float(scores[cid])
        if conf < CONF_MIN:
            continue
        cx, cy, w, h = p[:4]
        af = (w / 640.0) * (h / 640.0)
        if af < AREA_MIN:
            continue
        dets.append(((cx - w / 2) / 640.0, (cy - h / 2) / 640.0,
                     (cx + w / 2) / 640.0, (cy + h / 2) / 640.0, conf))
        if af > best_area:
            best_area = af
            best_cx = cx / 640.0
    if best_cx is None:
        cmd = "EXP:%d:%d" % (EXP_L, EXP_R)
    elif best_cx < ZONE_L:
        cmd = "AVD:R"
    elif best_cx > ZONE_R:
        cmd = "AVD:L"
    else:
        cmd = "RET"
    return dets, cmd

# ── CSV de telemetria + loop de telemetria/keepalive/dead-man (siempre activo) ─
_SAFETY_N = {"NORMAL": 0, "WARN": 1, "LIMIT": 2, "FAULT": 3}
# Solo sensores realmente conectados: ACS712 x6 (corrientes), NTC x4, TF02, encoders.
# Omitidos (no conectados -> irian a 0): VL53L0X (dist_tof), INA3221 (batt_mv/ma),
# LM335 (temp_c), MPU6050 (x/y/theta), ntc5/ntc6.
_CSV_COLS = ("t_ms,safety,i_fr,i_fl,i_cr,i_cl,i_rr,i_rl,"
             "ntc1,ntc2,ntc3,ntc4,tf_mm,enc_l,enc_r,unix_ms")


def _num(s):
    m = re.match(r"-?\d+", s.strip())
    return m.group(0) if m else "0"


def _tlm_row(line):
    f = line.split(":")
    if len(f) < 26:
        return None
    try:
        row = [_num(f[3]), _SAFETY_N.get(f[1], -1)]
        row += [_num(f[i]) for i in range(6, 12)]    # corrientes i_fr..i_rl (ACS712)
        row += [_num(f[i]) for i in range(13, 17)]   # ntc1..ntc4
        row += [_num(f[25]), _num(f[20]), _num(f[21])]  # tf_mm (TF02), enc_l, enc_r
        row += [int(time.time() * 1000)]             # unix_ms
        return ",".join(str(v) for v in row)
    except (IndexError, ValueError):
        return None


def _open_csv():
    for d in ("/var/log/olympus", "/tmp"):
        try:
            os.makedirs(d, exist_ok=True)
            path = os.path.join(d, "station_tlm_%s.csv" % time.strftime("%Y%m%d_%H%M%S"))
            fh = open(path, "w")
            fh.write("# csv_cols=" + _CSV_COLS + "\n")
            fh.flush()
            print("CSV telemetria:", path, flush=True)
            return fh
        except OSError:
            continue
    return None


_csv = _open_csv()


def telemetry_loop():
    last_ping = 0.0
    while True:
        now = time.monotonic()
        with slock:
            da, ld = state["drive_active"], state["last_drive"]
        if da and now - ld > DEADMAN_S:
            rcmd("STB")
            with slock:
                state["drive_active"] = False
                state["cmd"] = "STB"
        if now - last_ping > 1.0:
            rcmd("PING")
            last_ping = now
        t = rtlm()
        if t:
            t = t.strip()
            with slock:
                state["tlm"] = t
            if _csv:
                r = _tlm_row(t)
                if r:
                    try:
                        _csv.write(r + "\n")
                        _csv.flush()
                    except OSError:
                        pass
        time.sleep(0.1)


# ── Captura de camara (+ inferencia en modo AUTO) ─────────────────────────────
def camera_loop():
    while True:
        proc = subprocess.Popen(
            ["rpicam-vid", "--codec", "mjpeg", "--output", "-",
             "--width", str(W), "--height", str(H), "--framerate", str(FPS),
             "--rotation", "180", "--timeout", "0", "--nopreview"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        buf = b""
        n = 0
        try:
            while True:
                chunk = proc.stdout.read(65536)
                if not chunk:
                    break
                buf += chunk
                while True:
                    s = buf.find(b"\xff\xd8")
                    if s == -1:
                        buf = b""
                        break
                    e = buf.find(b"\xff\xd9", s + 2)
                    if e == -1:
                        buf = buf[s:]
                        break
                    jpeg = buf[s:e + 2]
                    buf = buf[e + 2:]
                    with slock:
                        state["latest_jpeg"] = jpeg
                        mode = state["mode"]
                    n += 1
                    if mode == "AUTO" and n % INFER_EVERY == 0:
                        frame = cv2.imdecode(np.frombuffer(jpeg, np.uint8),
                                             cv2.IMREAD_COLOR)
                        if frame is not None:
                            dets, cmd = infer(frame)
                            rcmd(cmd)
                            with slock:
                                state["dets"] = dets
                                state["cmd"] = cmd
                                state["last_drive"] = time.monotonic()
                                state["drive_active"] = (
                                    cmd.startswith("EXP") or cmd in ("AVD:L", "AVD:R"))
        except Exception as ex:
            print("cam err:", ex, flush=True)
        finally:
            try:
                proc.terminate(); proc.wait()
            except Exception:
                pass
        time.sleep(1)                 # rpicam murio: reintentar

# ── Servidor de video (5005) ──────────────────────────────────────────────────
def video_server():
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", VIDEO_PORT)); srv.listen(1)
    print("video en :%d" % VIDEO_PORT, flush=True)
    while True:
        conn, addr = srv.accept()
        print("video viewer:", addr, flush=True)
        try:
            while True:
                with slock:
                    j = state["latest_jpeg"]
                if j:
                    conn.sendall(struct.pack(">I", len(j)) + j)
                time.sleep(1.0 / FPS)
        except OSError:
            pass
        finally:
            conn.close()
            print("video viewer fuera", flush=True)

# ── Servidor de control / telemetria (5006) ───────────────────────────────────
def ctrl_server():
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", CTRL_PORT)); srv.listen(1)
    print("control en :%d" % CTRL_PORT, flush=True)
    while True:
        conn, addr = srv.accept()
        print("ctrl client:", addr, flush=True)
        stop = threading.Event()

        def tx():
            # keepalive/dead-man/TLM viven en telemetry_loop; aqui solo reenviar estado
            while not stop.is_set():
                with slock:
                    tlm = state["tlm"]
                    mode, cmd, dets = state["mode"], state["cmd"], list(state["dets"])
                try:
                    if tlm:
                        conn.sendall((tlm + "\n").encode())
                    conn.sendall(("CMD:" + cmd + "\n").encode())
                    if mode == "AUTO":
                        ds = ";".join("%.4f,%.4f,%.4f,%.4f,%.2f" % d for d in dets)
                        conn.sendall(("DET:" + ds + "\n").encode())
                except OSError:
                    break
                time.sleep(0.1)

        th = threading.Thread(target=tx, daemon=True); th.start()
        try:
            f = conn.makefile("r")
            for raw in f:
                c = raw.strip()
                if not c:
                    continue
                if c.startswith("MODE:"):
                    m = c[5:].upper()
                    is_auto = (m == "AUTO")
                    if not is_auto:
                        rcmd("STB")
                    with slock:
                        state["mode"] = "AUTO" if is_auto else "MANUAL"
                        if not is_auto:
                            state["drive_active"] = False
                            state["cmd"] = "STB"
                            state["dets"] = []
                    continue
                with slock:
                    mode = state["mode"]
                if mode == "MANUAL":
                    rcmd(c)
                    with slock:
                        state["cmd"] = c
                        if c.startswith("EXP:") or c.startswith("CLB:"):
                            state["last_drive"] = time.monotonic()
                            state["drive_active"] = True
                        elif c in ("STB", "RST", "FLT"):
                            state["drive_active"] = False
        except OSError:
            pass
        finally:
            stop.set()
            rcmd("STB")
            conn.close()
            print("ctrl desconectado -> STB", flush=True)

if __name__ == "__main__":
    threading.Thread(target=telemetry_loop, daemon=True).start()
    threading.Thread(target=camera_loop, daemon=True).start()
    threading.Thread(target=video_server, daemon=True).start()
    ctrl_server()
