#!/usr/bin/env python3
"""Cliente TCP para interactuar con olympus_hlc --mode station.
Conecta, envía comandos y registra telemetría como evidencia.

Uso:
  python3 tcp_client.py <host> [comandos...]
  python3 tcp_client.py 192.168.100.1 MODE:AUTO MANUAL EXP:40:40 SAFE
  python3 tcp_client.py 192.168.100.1 --auto 10   # 10s en AUTO mode
"""
import json, socket, sys, time, re, os

CTRL_PORT = 5006
EVIDENCIA_DIR = os.path.expanduser("~/evidencia_tesis")

def recv_line(s):
    buf = b""
    while not buf.endswith(b"\n"):
        c = s.recv(1)
        if not c:
            break
        buf += c
    return buf.decode().strip()

def send_cmd(s, cmd):
    s.sendall((cmd + "\n").encode())
    resp = recv_line(s)
    return resp

def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.100.1"
    cmds = sys.argv[2:] if len(sys.argv) > 2 else ["PING"]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect((host, CTRL_PORT))
    except Exception as e:
        print(f"ERROR: no pude conectar a {host}:{CTRL_PORT} — {e}")
        print("¿Está corriendo 'python3 -m olympus_hlc --mode station' en la Pi?")
        sys.exit(1)

    print(f"Conectado a {host}:{CTRL_PORT}")
    print("=" * 60)

    # Leer banner
    try:
        banner = recv_line(s)
        print(f"BANNER: {banner}")
    except:
        pass

    # Modo AUTO con timeout
    auto_time = None
    plain_cmds = []
    for c in cmds:
        if c.startswith("--auto"):
            auto_time = int(c.split("=")[-1]) if "=" in c else 10
        else:
            plain_cmds.append(c)

    evidencia = []
    t_start = time.time()

    for cmd in plain_cmds:
        print(f">> {cmd}")
        for attempt in range(3):
            try:
                resp = send_cmd(s, cmd)
                print(f"<< {resp}")
                evidencia.append({"t": time.time() - t_start, "cmd": cmd, "resp": resp})
                break
            except socket.timeout:
                print(f"   timeout (intento {attempt+1})")

    # Modo AUTO continuo
    if auto_time:
        print(f"\n--- MODO AUTO por {auto_time}s ---")
        send_cmd(s, "MODE:AUTO")
        t_end = time.time() + auto_time
        tlm_log = []
        while time.time() < t_end:
            try:
                line = recv_line(s)
                if line.startswith("TLM") or "TLM" in line:
                    tlm_log.append({"t": time.time() - t_start, "raw": line})
                    if len(tlm_log) % 5 == 0:
                        print(f"  TLM #{len(tlm_log)}")
                elif "YOLO" in line or "AVD" in line or "EXP" in line or "RET" in line:
                    print(f"  DECISION: {line}")
                    tlm_log.append({"t": time.time() - t_start, "raw": line, "type": "decision"})
            except socket.timeout:
                continue
        print(f"  Total TLMs: {len(tlm_log)}")
        evidencia.append({"mode": "AUTO", "duration_s": auto_time, "tlms": len(tlm_log)})

    # Guardar evidencia
    ts = time.strftime("%Y%m%d_%H%M%S")
    fpath = os.path.join(EVIDENCIA_DIR, f"tcp_auto_evidence_{ts}.json")
    os.makedirs(EVIDENCIA_DIR, exist_ok=True)
    with open(fpath, "w") as f:
        json.dump({"host": host, "commands": cmds, "data": evidencia}, f, indent=2)
    print(f"\nEvidencia guardada: {fpath}")

    s.close()

if __name__ == "__main__":
    main()
