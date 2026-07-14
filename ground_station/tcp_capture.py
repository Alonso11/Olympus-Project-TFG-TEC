#!/usr/bin/env python3
"""Captura todo el stream TCP de olympus_hlc --mode station por N segundos.
Registra TLM, CMD, DET y EVT como evidencia.

Uso:
  python3 tcp_capture.py <host> <duracion_s> [comando_inicial]
  python3 tcp_capture.py 192.168.100.1 30 MODE:AUTO
  python3 tcp_capture.py 192.168.100.1 10 PING
"""
import json, socket, sys, time, os, re

CTRL_PORT = 5006
EVIDENCIA_DIR = os.path.expanduser("~/evidencia_tesis")

def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.100.1"
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    cmd_init = sys.argv[3] if len(sys.argv) > 3 else None

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.connect((host, CTRL_PORT))
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print(f"Conectado a {host}:{CTRL_PORT} por {duration}s")
    print("=" * 60)

    # Enviar comando inicial si hay
    if cmd_init:
        print(f">> {cmd_init}")
        s.sendall((cmd_init + "\n").encode())

    # Capturar líneas
    lines = []
    buf = b""
    t_start = time.time()
    while time.time() - t_start < duration:
        try:
            data = s.recv(4096)
            if not data:
                break
            buf += data
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                txt = line.decode("ascii", "replace").strip()
                if txt:
                    elapsed = time.time() - t_start
                    lines.append({"t_s": round(elapsed, 3), "line": txt})
                    # Print summary
                    if txt.startswith("TLM:"):
                        if len(lines) % 5 == 0:
                            print(f"  [{elapsed:.1f}s] TLM #{len(lines)}")
                    else:
                        print(f"  [{elapsed:.1f}s] {txt}")
        except socket.timeout:
            continue

    s.close()

    # Resumen
    tlms = sum(1 for l in lines if l["line"].startswith("TLM"))
    cmds = sum(1 for l in lines if l["line"].startswith("CMD"))
    dets = sum(1 for l in lines if l["line"].startswith("DET"))
    evts = sum(1 for l in lines if l["line"].startswith("EVT"))
    print("\n" + "=" * 60)
    print(f"Resumen: {tlms} TLM, {cmds} CMD, {dets} DET, {evts} EVT en {duration}s")

    if cmds > 0:
        print("\nÚltimos comandos:")
        for l in lines[-10:]:
            if l["line"].startswith("CMD:"):
                print(f"  {l['line']}")

    if dets > 0:
        print(f"\nDetecciones YOLO ({dets} frames):")
        for l in lines:
            if l["line"].startswith("DET:") and l["line"] != "DET:":
                det_data = l["line"][4:]
                n = len(det_data.split(";")) if det_data else 0
                print(f"  [{l['t_s']:.1f}s] {n} detecciones")

    # Guardar
    ts = time.strftime("%Y%m%d_%H%M%S")
    fpath = os.path.join(EVIDENCIA_DIR, f"tcp_auto_capture_{ts}.json")
    os.makedirs(EVIDENCIA_DIR, exist_ok=True)
    with open(fpath, "w") as f:
        json.dump({"host": host, "duration_s": duration, "cmd_init": cmd_init,
                   "lines": lines, "stats": {"tlm": tlms, "cmd": cmds, "det": dets, "evt": evts}},
                  f, indent=2)
    print(f"\nEvidencia guardada: {fpath}")

if __name__ == "__main__":
    main()
