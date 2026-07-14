#!/usr/bin/env python3
# olympus_gui.py — Estacion de tierra Olympus (corre en el PORTATIL).
#
# Una sola ventana:
#   - Boton Manual / Autonomo.
#   - Siempre la vista de la camara (lo que ve el rover); en Autonomo dibuja las
#     cajas YOLO encima (lo que ve el modelo) + lineas de zona.
#   - El comando actual en grande.
#   - Toda la telemetria de sensores.
#
# Arquitectura: la GUI se conecta por SSH a la Pi, sube y lanza olympus_station.py
# (camara + control del Mega + inferencia YOLO + telemetria), y luego habla por TCP:
#   5005 video [len][jpeg]   ·   5006 control/telemetria/detecciones (texto).
# Se usa TCP porque el WiFi del campus bloquea UDP.
#
# Requisitos en el portatil: PyQt5 + ssh/scp del sistema (usa tu clave/agente).
# La decodificacion JPEG y el overlay se hacen con QImage/QPainter (sin OpenCV).

import os
import re
import socket
import struct
import subprocess
import sys
import time

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Nota: usamos el ssh/scp del SISTEMA (subprocess), no paramiko, para reutilizar
# el mismo agente/clave que ya funciona en la terminal (evita el fallo de auth
# de paramiko con claves RSA frente a servidores OpenSSH nuevos).

PI_HOST_DEFAULT = "172.21.255.241"
PI_USER_DEFAULT = "root"
VIDEO_PORT = 5005
CTRL_PORT = 5006
# (Consolidación A) Ya no se sube/corre olympus_station.py; el botón Start lanza
# el paquete instalado: python3 -m olympus_hlc --mode station. Ver start_station().
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

# safety -> numero (las filas del CSV deben ser numericas para el dashboard V&V)
_SAFETY_N = {"NORMAL": 0, "WARN": 1, "LIMIT": 2, "FAULT": 3}
# columnas del CSV — SOLO sensores realmente conectados (ACS712 x6, NTC x4, TF02,
# encoders). Omitidos: VL53L0X, INA3221, LM335, MPU6050, ntc5/6 (no conectados).
_CSV_COLS = ("t_ms,safety,stall,i_fr,i_fl,i_cr,i_cl,i_rr,i_rl,"
             "ntc1,ntc2,ntc3,ntc4,hc_mm,tf_mm,enc_l,enc_r,unix_ms")


def _num(s):
    """Extrae el entero (con signo) de un campo TLM que puede traer unidades."""
    m = re.match(r"-?\d+", s.strip())
    return m.group(0) if m else "0"


# Tema "mission control" estilo SpaceX: oscuro, minimalista, monospace, acentos neon.
ACCENT = "#5aa9ff"   # azul frio
OKC = "#00d488"      # verde
WARNC = "#ffb000"    # ambar
DANGER = "#ff4d4d"   # rojo
QSS = """
QWidget { background: #0a0e14; color: #e6edf3;
          font-family: 'Inter','Roboto','Segoe UI','DejaVu Sans',sans-serif; font-size: 12px; }
QGroupBox { background: #11161d; border: 1px solid #1f2933; border-radius: 10px;
            margin-top: 16px; padding-top: 8px; font-weight: 600; }
QGroupBox::title { subcontrol-origin: margin; left: 14px; padding: 0 6px; color: #5aa9ff;
                   font-size: 11px; font-weight: 700; }
QPushButton { background: #161c24; color: #e6edf3; border: 1px solid #2a3441;
              border-radius: 6px; padding: 9px 14px; font-weight: 600; }
QPushButton:hover { background: #1f2731; border: 1px solid #5aa9ff; }
QPushButton:pressed { background: #5aa9ff; color: #0a0e14; }
QPushButton:disabled { background: #11151b; color: #3a434f; border: 1px solid #1a2129; }
QPushButton:checked { background: #00d488; color: #03110b; border: 1px solid #00d488; }
QLineEdit { background: #0d1218; color: #e6edf3; border: 1px solid #2a3441;
            border-radius: 6px; padding: 6px; selection-background-color: #5aa9ff; }
QTextEdit { background: #06090d; color: #6ee7b7; border: 1px solid #1f2933; border-radius: 8px;
            font-family: 'JetBrains Mono','DejaVu Sans Mono',monospace; font-size: 11px; }
QSlider::groove:horizontal { height: 4px; background: #2a3441; border-radius: 2px; }
QSlider::handle:horizontal { background: #5aa9ff; width: 16px; border-radius: 8px; margin: -7px 0; }
QSlider::sub-page:horizontal { background: #5aa9ff; border-radius: 2px; }
QStatusBar { background: #06090d; color: #8b9aad; border-top: 1px solid #1f2933; }
QLabel { color: #e6edf3; }
QLabel#banner { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #06090d, stop:1 #11161d);
                color: #ffffff; font-size: 19px; font-weight: 800; letter-spacing: 4px;
                padding: 14px; border: 1px solid #1f2933; border-radius: 10px; }
QScrollBar:vertical { background: #0a0e14; width: 10px; }
QScrollBar::handle:vertical { background: #2a3441; border-radius: 5px; }
"""


# ─────────────────────────────────────────────────────────────────────────────
# Hilo de video: recibe frames JPEG por TCP y los emite como QImage.
# ─────────────────────────────────────────────────────────────────────────────
class VideoThread(QThread):
    frame = pyqtSignal(QImage)
    status = pyqtSignal(str)

    def __init__(self, host):
        super().__init__()
        self._host = host
        self._run = True

    def run(self):
        while self._run:
            try:
                s = socket.create_connection((self._host, VIDEO_PORT), timeout=8)
                self.status.emit("video: conectado")
            except OSError as e:
                self.status.emit(f"video: sin conexion ({e})")
                time.sleep(2)
                continue
            try:
                while self._run:
                    hdr = self._recvn(s, 4)
                    if hdr is None:
                        break
                    ln = struct.unpack(">I", hdr)[0]
                    data = self._recvn(s, ln)
                    if data is None:
                        break
                    img = QImage.fromData(data, "JPG")
                    if not img.isNull():
                        self.frame.emit(img)
            except OSError:
                pass
            finally:
                s.close()
            time.sleep(1)

    def _recvn(self, s, n):
        d = b""
        while len(d) < n:
            try:
                c = s.recv(n - len(d))
            except OSError:
                return None
            if not c:
                return None
            d += c
        return d

    def stop(self):
        self._run = False


# ─────────────────────────────────────────────────────────────────────────────
# Hilo de control/telemetria: lee lineas TLM/CMD/DET/EVT y permite enviar comandos.
# ─────────────────────────────────────────────────────────────────────────────
class CtrlThread(QThread):
    tlm = pyqtSignal(str)
    cmd = pyqtSignal(str)
    dets = pyqtSignal(list)       # [(x1,y1,x2,y2,conf)]
    evt = pyqtSignal(str)
    status = pyqtSignal(str)

    def __init__(self, host):
        super().__init__()
        self._host = host
        self._run = True
        self._sock = None
        self._lock = __import__("threading").Lock()

    def run(self):
        while self._run:
            try:
                s = socket.create_connection((self._host, CTRL_PORT), timeout=8)
                with self._lock:
                    self._sock = s
                self.status.emit("control: conectado")
            except OSError as e:
                self.status.emit(f"control: sin conexion ({e})")
                time.sleep(2)
                continue
            try:
                f = s.makefile("r")
                for line in f:
                    if not self._run:
                        break
                    line = line.strip()
                    if line.startswith("TLM:"):
                        self.tlm.emit(line)
                    elif line.startswith("CMD:"):
                        self.cmd.emit(line[4:])
                    elif line.startswith("DET:"):
                        self.dets.emit(self._parse_dets(line[4:]))
                    elif line.startswith("EVT:"):
                        self.evt.emit(line[4:])
            except OSError:
                pass
            finally:
                with self._lock:
                    self._sock = None
                s.close()
            time.sleep(1)

    def _parse_dets(self, payload):
        out = []
        for tok in payload.split(";"):
            if not tok:
                continue
            try:
                x1, y1, x2, y2, conf = (float(v) for v in tok.split(","))
                out.append((x1, y1, x2, y2, conf))
            except ValueError:
                pass
        return out

    def send(self, command):
        with self._lock:
            if self._sock:
                try:
                    self._sock.sendall((command + "\n").encode())
                except OSError:
                    pass

    def stop(self):
        self._run = False


# ─────────────────────────────────────────────────────────────────────────────
# Ventana principal
# ─────────────────────────────────────────────────────────────────────────────
class OlympusStation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.video = None
        self.ctrl = None
        self._csv = None
        self._csv_path = None
        self._comm = None             # log de comunicación (comandos/eventos)
        self._comm_path = None
        self.auto = False
        self.last_frame = None        # QImage
        self.last_dets = []
        self.last_cmd = "STB"
        self._last_logged_cmd = None  # para loguear CMD solo al cambiar
        self._init_ui()
        # timer que reenvia el comando de manejo mientras un boton esta presionado
        self._drive_cmd = None
        self._drive_timer = QTimer(self)
        self._drive_timer.setInterval(250)
        self._drive_timer.timeout.connect(self._tick_drive)

    # ── UI ────────────────────────────────────────────────────────────────────
    def _init_ui(self):
        self.setWindowTitle("Olympus — Estacion de Tierra")
        if os.environ.get("VNC") == "1":
            self.showMaximized()
        else:
            self.setGeometry(80, 80, 1100, 720)
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # Banner (branding alineado con el dashboard V&V)
        banner = QLabel("◆  OLYMPUS ROVER  ·  GROUND CONTROL")
        banner.setObjectName("banner")
        banner.setAlignment(Qt.AlignCenter)
        root.addWidget(banner)

        # Conexion
        conn = QGroupBox("Conexion")
        cl = QHBoxLayout(conn)
        cl.addWidget(QLabel("Pi host:"))
        self.host_in = QLineEdit(PI_HOST_DEFAULT)
        cl.addWidget(self.host_in)
        cl.addWidget(QLabel("user:"))
        self.user_in = QLineEdit(PI_USER_DEFAULT)
        self.user_in.setMaximumWidth(90)
        cl.addWidget(self.user_in)
        cl.addWidget(QLabel("pass (vacio=key):"))
        self.pass_in = QLineEdit()
        self.pass_in.setEchoMode(QLineEdit.Password)
        self.pass_in.setMaximumWidth(120)
        cl.addWidget(self.pass_in)
        self.start_btn = QPushButton("Iniciar estacion")
        self.start_btn.clicked.connect(self.start_station)
        cl.addWidget(self.start_btn)
        self.stop_btn = QPushButton("Detener")
        self.stop_btn.clicked.connect(self.stop_station)
        self.stop_btn.setEnabled(False)
        cl.addWidget(self.stop_btn)
        root.addWidget(conn)

        # Centro: camara | panel
        mid = QHBoxLayout()
        root.addLayout(mid, 1)

        # Camara
        cam_box = QGroupBox("Vista del rover")
        cbl = QVBoxLayout(cam_box)
        self.cam_label = QLabel("Sin video")
        self.cam_label.setAlignment(Qt.AlignCenter)
        self.cam_label.setMinimumSize(640, 480)
        self.cam_label.setStyleSheet("background:#06090d; color:#3a434f; border:1px solid #1f2933; border-radius:8px;")
        cbl.addWidget(self.cam_label)
        self.cmd_label = QLabel("CMD —")
        self.cmd_label.setAlignment(Qt.AlignCenter)
        self.cmd_label.setStyleSheet("font-family:'JetBrains Mono','DejaVu Sans Mono',monospace; font-size:22px; font-weight:bold; padding:8px; letter-spacing:2px; color:#8b9aad;")
        cbl.addWidget(self.cmd_label)
        mid.addWidget(cam_box, 2)

        # Panel derecho
        panel = QWidget()
        pl = QVBoxLayout(panel)
        mid.addWidget(panel, 1)

        # Modo
        mode_box = QGroupBox("Modo")
        ml = QHBoxLayout(mode_box)
        self.mode_btn = QPushButton("◉ MANUAL")
        self.mode_btn.setCheckable(True)
        self.mode_btn.setStyleSheet("font-size:16px; font-weight:bold; padding:8px;")
        self.mode_btn.clicked.connect(self.toggle_mode)
        ml.addWidget(self.mode_btn)
        pl.addWidget(mode_box)

        # Modelo de visión (YOLO vs lunar — TFG Carlos Alfaro)
        model_box = QGroupBox("Modelo de visión")
        mol = QHBoxLayout(model_box)
        self.model_sel = QComboBox()
        self.model_sel.addItem("YOLOv8n — detección de objetos", "YOLO")
        self.model_sel.addItem("Lunar — segmentación de terrain", "LUNAR")
        self.model_sel.currentIndexChanged.connect(self._on_model_changed)
        mol.addWidget(self.model_sel)
        pl.addWidget(model_box)

        # Nivel de seguridad — gobierna los overrides autónomos del HLC
        safe_box = QGroupBox("Nivel de seguridad")
        sl = QHBoxLayout(safe_box)
        self.safety = QComboBox()
        self.safety.addItem("Plena — todos los overrides", "FULL")
        self.safety.addItem("Asistida — sin retroceso auto", "ASSIST")
        self.safety.addItem("Manual — control total", "MANUAL")
        self.safety.currentIndexChanged.connect(self._on_safety_changed)
        sl.addWidget(self.safety)
        pl.addWidget(safe_box)

        # Manejo
        self.drive_box = QGroupBox("Manejo (manten presionado)")
        dl = QGridLayout(self.drive_box)
        self.btn_fwd = self._mk_drive("▲", "fwd")
        self.btn_back = self._mk_drive("▼", "back")
        self.btn_left = self._mk_drive("◄", "left")
        self.btn_right = self._mk_drive("►", "right")
        self.btn_stop = QPushButton("■ STOP")
        self.btn_stop.setStyleSheet("background:#ff4d4d; color:#1a0000; font-size:16px; font-weight:bold; padding:10px; border:1px solid #ff4d4d; border-radius:6px;")
        self.btn_stop.clicked.connect(self._emergency_stop)
        dl.addWidget(self.btn_fwd, 0, 1)
        dl.addWidget(self.btn_left, 1, 0)
        dl.addWidget(self.btn_stop, 1, 1)
        dl.addWidget(self.btn_right, 1, 2)
        dl.addWidget(self.btn_back, 2, 1)
        dl.addWidget(QLabel("Velocidad:"), 3, 0)
        self.speed = QSlider(Qt.Horizontal)
        self.speed.setRange(15, 99)
        self.speed.setValue(25)
        self.speed_lbl = QLabel("25%")
        self.speed.valueChanged.connect(lambda v: self.speed_lbl.setText(f"{v}%"))
        dl.addWidget(self.speed, 3, 1)
        dl.addWidget(self.speed_lbl, 3, 2)
        self.rst_btn = QPushButton("RST (limpiar FAULT)")
        self.rst_btn.clicked.connect(lambda: self._send("RST"))
        dl.addWidget(self.rst_btn, 4, 0, 1, 3)
        pl.addWidget(self.drive_box)

        # Telemetria
        VAL = "font-family:'JetBrains Mono','DejaVu Sans Mono',monospace; color:#e6edf3; font-weight:600;"
        DIM = "color:#8b9aad; font-size:11px;"
        MONO = "font-family:'JetBrains Mono','DejaVu Sans Mono',monospace; color:#6ee7b7;"
        tlm_box = QGroupBox("TELEMETRÍA")
        tg = QGridLayout(tlm_box)
        self.tlm_labels = {}
        scal = [("safety", "ESTADO"), ("stall", "STALL FR..RL"), ("tick", "TICK ms"),
                ("dist_tof", "PROX HC-SR04 mm"), ("dist_tf02", "LiDAR TF02 mm"),
                ("enc_L", "ENC IZQ"), ("enc_R", "ENC DER")]
        row = 0
        for key, lbl in scal:
            dl = QLabel(lbl); dl.setStyleSheet(DIM)
            tg.addWidget(dl, row, 0)
            v = QLabel("—"); v.setStyleSheet(VAL)
            self.tlm_labels[key] = v
            tg.addWidget(v, row, 1)
            row += 1
        # corrientes por rueda (6)
        hdr = QLabel("CORRIENTES POR RUEDA (mA)"); hdr.setStyleSheet(DIM)
        tg.addWidget(hdr, row, 0, 1, 2); row += 1
        self.cur_labels = {}
        cur_w = QWidget(); cur_g = QGridLayout(cur_w); cur_g.setContentsMargins(0, 0, 0, 0)
        for i, w in enumerate(["FR", "FL", "CR", "CL", "RR", "RL"]):
            cell = QVBoxLayout()
            wl = QLabel(w); wl.setStyleSheet("color:#5aa9ff; font-size:10px; font-weight:700;")
            wl.setAlignment(Qt.AlignCenter)
            vv = QLabel("—"); vv.setStyleSheet(VAL); vv.setAlignment(Qt.AlignCenter)
            self.cur_labels[w] = vv
            cell.addWidget(wl); cell.addWidget(vv)
            holder = QWidget(); holder.setLayout(cell)
            cur_g.addWidget(holder, i // 3, i % 3)
        tg.addWidget(cur_w, row, 0, 1, 2); row += 1
        # ntc bateria (4)
        nl = QLabel("NTC BATERÍA (°C)"); nl.setStyleSheet(DIM)
        tg.addWidget(nl, row, 0)
        self.ntc_label = QLabel("—"); self.ntc_label.setStyleSheet(MONO)
        tg.addWidget(self.ntc_label, row, 1)
        pl.addWidget(tlm_box)
        pl.addStretch(1)

        # Log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(120)
        root.addWidget(self.log)

        self.statusBar().showMessage("Desconectado")
        self._set_controls_enabled(False)

    def _mk_drive(self, text, kind):
        b = QPushButton(text)
        b.setStyleSheet("font-size:20px; padding:12px;")
        b.pressed.connect(lambda: self._drive_start(kind))
        b.released.connect(self._drive_stop)
        return b

    # ── SSH / arranque de la estacion ───────────────────────────────────────────
    def _ssh_opts(self):
        return ["-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new",
                "-o", "ConnectTimeout=10"]

    def start_station(self):
        host = self.host_in.text().strip()
        user = self.user_in.text().strip()
        target = f"{user}@{host}"
        opts = self._ssh_opts()
        # Consolidación (A): la HLC real es la única dueña del Mega. Ya NO se sube
        # ni se corre olympus_station.py (daemon viejo de doble función). Se lanza
        # el paquete olympus_hlc instalado en la Pi con --mode station (sirve TCP
        # 5006 control / 5005 video + YOLO a bordo, y abre el Mega vía rover_bridge).
        # Desplegar/actualizar el paquete con: olympus-hlc-rpi5/deploy-hlc-ssh.sh
        # busybox pkill -f NO mata fiable en el Yocto de la Pi -> matar por /proc/cmdline.
        launch = (
            "for p in $(pgrep python3); do "
            "grep -aqE 'olympus_station|olympus_hlc' /proc/$p/cmdline 2>/dev/null && kill -9 $p; done; "
            "pkill -9 rpicam-vid 2>/dev/null; "
            "for p in $(fuser /dev/ttyACM0 5005/tcp 5006/tcp 2>/dev/null); "
            "do kill -9 $p 2>/dev/null; done; sleep 3; "
            "setsid python3 -u -m olympus_hlc --mode station </dev/null >/tmp/station.log 2>&1 & "
            "sleep 6; cat /tmp/station.log"
        )
        try:
            r = subprocess.run(["ssh"] + opts + [target, launch],
                               capture_output=True, text=True, timeout=45)
            self._logmsg("station.log:\n" + (r.stdout or r.stderr))
        except Exception as e:
            QMessageBox.critical(self, "SSH", f"Error lanzando HLC --mode station: {e}")
            return
        # conectar TCP
        self._connect_streams(host)
        # abrir CSV de telemetria (formato vv_dashboard)
        try:
            os.makedirs(LOG_DIR, exist_ok=True)
            self._csv_path = os.path.join(
                LOG_DIR, "tlm_" + time.strftime("%Y%m%d_%H%M%S") + ".csv")
            self._csv = open(self._csv_path, "w")
            self._csv.write("# csv_cols=" + _CSV_COLS + "\n")
            self._csv.flush()
            self._logmsg(f"grabando telemetria -> {self._csv_path}")
        except OSError as e:
            self._logmsg(f"no se pudo abrir CSV: {e}")
            self._csv = None
        # log de comunicación (comandos/eventos/seguridad) — evidencia, análogo al CSV
        try:
            self._comm_path = os.path.join(
                LOG_DIR, "comm_" + time.strftime("%Y%m%d_%H%M%S") + ".log")
            self._comm = open(self._comm_path, "w")
            self._comm.write("# unix_ms,kind,payload   (kind: CMD|EVT|SAFE)\n")
            self._comm.flush()
            self._logmsg(f"grabando comunicacion -> {self._comm_path}")
        except OSError as e:
            self._logmsg(f"no se pudo abrir comm log: {e}")
            self._comm = None
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self._set_controls_enabled(True)
        self.statusBar().showMessage(f"Estacion activa — {host}")

    def _connect_streams(self, host):
        self.video = VideoThread(host)
        self.video.frame.connect(self.on_frame)
        self.video.status.connect(self._logmsg)
        self.video.start()
        self.ctrl = CtrlThread(host)
        self.ctrl.tlm.connect(self.on_tlm)
        self.ctrl.cmd.connect(self.on_cmd)
        self.ctrl.dets.connect(self.on_dets)
        self.ctrl.evt.connect(self._on_evt)
        self.ctrl.status.connect(self._on_ctrl_status)
        self.ctrl.start()

    def stop_station(self):
        self._send("STB")
        if self._csv:
            try:
                self._csv.close()
            except OSError:
                pass
            self._logmsg(f"telemetria guardada: {self._csv_path}")
            self._csv = None
        if self._comm:
            try:
                self._comm.close()
            except OSError:
                pass
            self._logmsg(f"comunicacion guardada: {self._comm_path}")
            self._comm = None
        if self.video:
            self.video.stop(); self.video.wait(1500)
        if self.ctrl:
            self.ctrl.stop(); self.ctrl.wait(1500)
        host = self.host_in.text().strip()
        user = self.user_in.text().strip()
        try:
            # busybox no tiene pkill -f fiable → matar por /proc/cmdline.
            # Incluye olympus_station por si quedó un daemon viejo corriendo.
            subprocess.run(["ssh"] + self._ssh_opts() + [f"{user}@{host}",
                           "for p in $(pgrep python3); do "
                           "grep -aqE 'olympus_hlc|olympus_station' /proc/$p/cmdline 2>/dev/null "
                           "&& kill -9 $p; done; pkill -9 rpicam-vid 2>/dev/null"],
                           capture_output=True, timeout=10)
        except Exception:
            pass
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self._set_controls_enabled(False)
        self.statusBar().showMessage("Detenido")

    # ── Modo ────────────────────────────────────────────────────────────────────
    def toggle_mode(self):
        self.auto = self.mode_btn.isChecked()
        if self.auto:
            self.mode_btn.setText("◉ AUTÓNOMO")
            self.mode_btn.setStyleSheet("font-size:16px; font-weight:bold; padding:8px; background:#00d488; color:#03110b; border-radius:6px;")
            self._send("MODE:AUTO")
            self.drive_box.setEnabled(False)
        else:
            self.mode_btn.setText("◉ MANUAL")
            self.mode_btn.setStyleSheet("font-size:16px; font-weight:bold; padding:8px;")
            self._send("MODE:MANUAL")
            self.drive_box.setEnabled(True)

    # ── Manejo manual ────────────────────────────────────────────────────────────
    def _drive_start(self, kind):
        if self.auto:
            return
        s = self.speed.value()
        t = max(15, int(s * 0.8))
        cmds = {
            "fwd": f"EXP:{s}:{s}",
            "back": f"EXP:{-s}:{-s}",
            "left": f"EXP:{-t}:{t}",
            "right": f"EXP:{t}:{-t}",
        }
        self._drive_cmd = cmds[kind]
        self._send(self._drive_cmd)
        self._drive_timer.start()

    def _tick_drive(self):
        if self._drive_cmd:
            self._send(self._drive_cmd)

    def _drive_stop(self):
        self._drive_timer.stop()
        self._drive_cmd = None
        self._send("STB")

    def _emergency_stop(self):
        # Paro de emergencia. La station, al recibir STB, SALE de AUTO (desarma la
        # autonomía); reflejamos lo mismo en la UI para que el botón de modo no
        # mienta y el rover no reanude solo. En AUTO el STB no frenaba porque el
        # lazo de YOLO ignoraba la cola de comandos (fix en station.py).
        self._send("STB")
        if self.mode_btn.isChecked():
            self.mode_btn.setChecked(False)
            self.toggle_mode()        # → MANUAL: actualiza self.auto/texto/estilo

    def _send(self, command):
        if self.ctrl:
            self.ctrl.send(command)

    def _on_safety_changed(self):
        lvl = self.safety.currentData()
        self._send("SAFE:" + lvl)
        self._logmsg(f"nivel de seguridad → {lvl}")
        self._comm_write("SAFE", lvl)

    def _on_model_changed(self):
        m = self.model_sel.currentData()
        self._send("MODEL:" + m)
        self._logmsg(f"modelo de visión → {m}")
        self._comm_write("MODEL", m)

    def _on_ctrl_status(self, msg):
        # Al (re)conectar el control, re-sincronizar el nivel de seguridad: la
        # station resetea a PLENA por cada cliente nuevo, así que enviamos el que
        # tiene seleccionado el operador para que coincidan.
        self._logmsg(msg)
        if "conectado" in msg:
            self._send("SAFE:" + self.safety.currentData())
            self._send("MODEL:" + self.model_sel.currentData())

    def _on_evt(self, e):
        # Eventos del HLC (overrides con razón, cambios de modo, link, etc.).
        self._logmsg(f"EVT: {e}")
        self._comm_write("EVT", e)

    def _comm_write(self, kind, payload):
        # Persistir comunicación a archivo (evidencia), análogo al CSV de TLM.
        if not self._comm:
            return
        try:
            self._comm.write(f"{int(time.time() * 1000)},{kind},{payload}\n")
            self._comm.flush()
        except OSError:
            pass

    # ── Recepcion ────────────────────────────────────────────────────────────────
    def on_frame(self, img):
        self.last_frame = img
        self._render()

    def on_dets(self, dets):
        self.last_dets = dets

    def on_cmd(self, cmd):
        self.last_cmd = cmd
        color = OKC if cmd.startswith("EXP") else (DANGER if cmd in ("STB", "FLT") else WARNC)
        self.cmd_label.setText(f"CMD  {cmd}")
        self.cmd_label.setStyleSheet(f"font-family:'JetBrains Mono','DejaVu Sans Mono',monospace; font-size:22px; font-weight:bold; padding:8px; letter-spacing:2px; color:{color};")
        # Loguear el comando REAL (con override) solo al cambiar, para evidencia
        # sin inundar el panel (se echa una vez por frame TLM ~1 Hz).
        if cmd != self._last_logged_cmd:
            self._last_logged_cmd = cmd
            self._logmsg(f"CMD → {cmd}")
            self._comm_write("CMD", cmd)

    def on_tlm(self, line):
        f = line.split(":")
        if len(f) < 26:
            return
        try:
            self.tlm_labels["safety"].setText(f[1])
            self.tlm_labels["stall"].setText(f[2])
            self.tlm_labels["tick"].setText(_num(f[3]))
            self.tlm_labels["dist_tof"].setText(_num(f[19]))    # HC-SR04 (proximidad, f[19]=dist_mm)
            self.tlm_labels["dist_tf02"].setText(_num(f[25]))   # TF02 LiDAR
            self.tlm_labels["enc_L"].setText(f[20])
            self.tlm_labels["enc_R"].setText(f[21])
            for i, w in enumerate(["FR", "FL", "CR", "CL", "RR", "RL"]):  # ACS712 x6
                self.cur_labels[w].setText(f[6 + i])
            self.ntc_label.setText("  ".join(f[13:17]))         # NTC x4
            sev = f[1]
            col = {"NORMAL": OKC, "WARN": WARNC,
                   "LIMIT": "#ff8c1a", "FAULT": DANGER}.get(sev, "#8b9aad")
            self.tlm_labels["safety"].setStyleSheet(f"font-family:'JetBrains Mono','DejaVu Sans Mono',monospace; font-weight:bold; color:{col};")
        except (IndexError, ValueError):
            pass
        # grabar fila al CSV (numerica, para el dashboard)
        if self._csv:
            try:
                row = [_num(f[3]), _SAFETY_N.get(f[1], -1), f[2]]  # t_ms, safety, stall
                row += [_num(f[i]) for i in range(6, 12)]     # corrientes (ACS712)
                row += [_num(f[i]) for i in range(13, 17)]    # ntc1..4
                row += [_num(f[19]), _num(f[25]),             # hc_mm (HC-SR04), tf_mm (TF02)
                        _num(f[20]), _num(f[21])]             # enc_l, enc_r
                row += [int(time.time() * 1000)]               # unix_ms
                self._csv.write(",".join(str(v) for v in row) + "\n")
                self._csv.flush()
            except (IndexError, ValueError, OSError):
                pass

    # ── Render camara + overlay ──────────────────────────────────────────────────
    def _render(self):
        if self.last_frame is None:
            return
        pix = QPixmap.fromImage(self.last_frame).scaled(
            self.cam_label.width(), self.cam_label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation)
        w, h = pix.width(), pix.height()
        p = QPainter(pix)
        if self.auto:
            # lineas de zona (1/3, 2/3) — azul acento
            p.setPen(QPen(QColor(90, 169, 255, 110), 1, Qt.DashLine))
            p.drawLine(int(w / 3), 0, int(w / 3), h)
            p.drawLine(int(2 * w / 3), 0, int(2 * w / 3), h)
            # cajas de detecciones — verde neon
            neon = QColor(0, 212, 136)
            p.setPen(QPen(neon, 2))
            f = p.font(); f.setPointSize(9); f.setBold(True); p.setFont(f)
            for x1, y1, x2, y2, conf in self.last_dets:
                rx, ry = int(x1 * w), int(y1 * h)
                rw, rh = int((x2 - x1) * w), int((y2 - y1) * h)
                p.drawRect(rx, ry, rw, rh)
                p.fillRect(rx, ry - 15, 46, 15, neon)
                p.setPen(QColor(3, 17, 11))
                p.drawText(rx + 3, ry - 3, f"{conf:.2f}")
                p.setPen(QPen(neon, 2))
        p.end()
        self.cam_label.setPixmap(pix)

    # ── Util ──────────────────────────────────────────────────────────────────────
    def _set_controls_enabled(self, on):
        self.mode_btn.setEnabled(on)
        self.drive_box.setEnabled(on)

    def _logmsg(self, msg):
        self.log.append(msg)

    def closeEvent(self, ev):
        try:
            self.stop_station()
        except Exception:
            pass
        ev.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    win = OlympusStation()
    win.show()
    sys.exit(app.exec_())
