# CHANGELOG — SRS Rover Olympus

Registro de cambios significativos al documento SyRS/SRS del Rover Olympus.
Cada entrada documenta **qué se cambió**, **por qué se cambió** y **qué archivo(s) se modificaron**.

---

## Sesión 2026-04-04 — Auditoría SRS vs misiones reales (NASA/ESA/ECSS)

### Motivación general
Se realizó una auditoría completa del SRS comparando la estructura y contenido del
documento contra estándares de misiones espaciales reales:
- **ISO/IEC/IEEE 29148:2018** — Requirements engineering lifecycle
- **ECSS-E-ST-10-06C** — ESA technical requirements specification
- **ECSS-Q-ST-30C** — ESA dependability / FMEA
- **NASA-STD-8739.8B** — Software assurance and criticality
- **NASA SWE-052** — Bidirectional traceability requirements

La auditoría identificó **7 GAPs estructurales** y **6 anti-patterns de calidad de requisitos**
que comprometían la verificabilidad y trazabilidad del documento.

---

### Cambio 1 — FMEA expandida a ECSS-Q-ST-30C
**Archivo:** `sections/s13_appendices.tex`

**Qué:** La FMEA original tenía solo columna de severidad. Se expandió a 8 columnas:
Componente, Modo de Falla, Efecto, **Clase (Critical/Major/Minor)**, **Ocurrencia**,
**Detección**, Mitigación, Requisito. Convertida a `longtable` en orientación landscape.

**Por qué:** ECSS-Q-ST-30C requiere que el análisis de fallas incluya severidad, ocurrencia
y mecanismo de detección para ser un FMEA válido. Sin estos campos, la tabla era una lista
narrativa, no un análisis de confiabilidad. Esto bloqueaba el cierre de RF-005 y RNF-002.

---

### Cambio 2 — RF-004 supersedido por RF-004-R1 (CR-002)
**Archivos:** `s09_system_requirements.tex`, `s11_v_v_acceptance.tex`, `s09a_teamtet_requirements.tex`,
`s11a_teamtet_verification.tex`, `s11b_teamtet_testcases.tex`, `s12_traceability_change.tex`,
`s13_appendices.tex`

**Qué:** RF-004 especificaba compensación de slip mediante EKF (Extended Kalman Filter).
Se marcó `[SUPERSEDED — CR-002]` y se creó RF-004-R1 con criterio encoder-based
(error < 5% vs ground truth físico, 6 ruedas, estado EXP activo).

**Por qué:** El EKF nunca fue implementado en el código de vuelo (LLC/HLC) y el hardware
IMU necesario no está en la configuración de vuelo del TFG. Mantener RF-004 sin cambios
era una **brecha de trazabilidad**: el V&V plan verificaba algo que el sistema no hace.
Conforme a NASA-NPR-7123.1C, los IDs de requisito son inmutables — se usa la práctica
de "supersession" en lugar de borrar el requisito.

---

### Cambio 3 — SYS-FUN-040 dividido en 040a y 040b
**Archivo:** `sections/s09_system_requirements.tex`

**Qué:** SYS-FUN-040 decía "Safe Mode si voltaje < 12V **O** latencia > 5s" (condición OR).
Se dividió en dos requisitos atómicos: 040a (voltaje) y 040b (latencia).

**Por qué:** ISO/IEC/IEEE 29148 §5.2.6 prohíbe requisitos compuestos — un requisito con OR
no es verificable independientemente. Además, cada condición tiene un método de V&V
diferente (INA226 para 040a, timer watchdog para 040b).

---

### Cambio 4 — RNF-007 renombrado a MOD (Minimum Operational Duration)
**Archivos:** `s09_system_requirements.tex`, `s11_v_v_acceptance.tex`, `s13_appendices.tex`

**Qué:** RNF-007 se llamaba "MTBF ≥ 2 horas". Se renombró a
"Duración Operacional Mínima (MOD) ≥ 2 horas en campaña continua UC-01".

**Por qué:** MTBF (Mean Time Between Failures) es una métrica estadística que requiere
múltiples fallos y corridas para calcularse. El criterio de aceptación era una sola
campaña de 2 horas, que no es MTBF — es una duración mínima de operación. Usar
terminología incorrecta invalida el criterio de V&V.

---

### Cambio 5 — Registro ICD formal en §7
**Archivo:** `sections/s07_system_interfaces.tex`

**Qué:** Se añadió tabla formal de ICDs (Interface Control Documents) con dos entradas:
ICD-LLC-001 (C&DH↔GNC UART 115200 bps) e ICD-COMMS-001 (CSP/WiFi/UHF).
Cada ICD referencia la celda N2 correspondiente.

**Por qué:** El documento mencionaba interfaces en texto libre pero no tenía un registro
formal trazable. Sin IDs de ICD, la RTM no puede referenciar interfaces específicas
y los ingenieros de integración no tienen un punto único de verdad.

---

### Cambio 6 — Registro de Necesidades de Stakeholders (StRS layer)
**Archivo:** `sections/s05_stakeholders.tex`

**Qué:** Se añadió tabla formal §5.3 con 8 necesidades de stakeholders (SN-001..SN-008),
prioridad MoSCoW y requisitos derivados. Conforme a ISO 29148 §9.3 (StRS layer).

**Por qué:** El SRS tenía stakeholders descritos en texto pero no formalizaba la
trazabilidad desde necesidad operacional → requisito. Esto es la capa StRS de
ISO 29148 y es necesaria para demostrar que cada requisito tiene origen en una
necesidad real identificada.

---

### Cambio 7 — Requisitos ambientales §9.5 (ENV-REQ-001..005)
**Archivo:** `sections/s09_system_requirements.tex`

**Qué:** Se añadió nueva sección con 5 requisitos ambientales: temperatura operacional
(-10°C a +45°C), polvo/IP4X, humedad relativa ≤90%, pendiente ≤20°, radiación solar.

**Por qué:** ECSS-E-ST-10-06C exige que el SRS incluya el environment envelope del
sistema. Sin requisitos ambientales, no hay base para el diseño mecánico/térmico ni
criterios de aceptación para pruebas en el sitio análogo.

---

### Cambio 8 — Clasificación de criticidad de software §8.x
**Archivo:** `sections/s08_req_org_notation.tex`

**Qué:** Nueva subsección con tabla de criticidad SW conforme a NASA-STD-8739.8B:
- **LLC (Arduino Mega):** Mission-Critical (Class B) — controla actuadores, no hay safety net inferior
- **HLC (RPi5/Yocto):** Mission-Essential (Class B/C) — LLC actúa como safety net

**Por qué:** Sin clasificación de criticidad, los requisitos de V&V no tienen justificación
formal para su rigor diferencial. La separación LLC/HLC justifica por qué la LLC requiere
64 unit tests y code review, mientras HLC se valida con integration tests.

---

### Cambio 9 — Modos operacionales formales §9.4
**Archivo:** `sections/s09_system_requirements.tex`

**Qué:** Tabla landscape con 6 modos (MODE-001..006): STB, EXP, AVD, RET, FLT, SAFE.
Cada modo tiene precondición de entrada, condición de salida y enlace a requisito.

**Por qué:** ISO 29148 §9.4.16 requiere documentar el ciclo de vida operacional del
sistema. Los modos ya existían en el código (state_machine/mod.rs) pero no estaban
formalizados en el SRS — brecha de trazabilidad código↔requisito.

---

### Cambio 10 — RTM expandida (NASA SWE-052)
**Archivo:** `sections/s13_appendices.tex`

**Qué:** RTM reconstruida como longtable landscape con 6 columnas: ID SyRS, Descripción,
Derivado/Referencia, Método V&V, Nivel (S/I/U), Estado (OPEN/CLOSED). ~30 filas,
agrupadas por categoría (RF, SYS-FUN, MODE, RNF, ICD, Calidad).

**Por qué:** NASA SWE-052 exige trazabilidad bidireccional. La RTM anterior era una
tabla simple sin nivel de V&V ni estado de cierre, lo que imposibilitaba saber cuáles
requisitos estaban verificados y a qué nivel.

---

### Cambio 11 — Presupuestos de ingeniería (Apéndice)
**Archivos:** `sections/s13_appendices.tex`, `references.bib`, `main.tex`

**Qué:** Nueva subsección "Engineering Budgets" con tres tablas:
1. **Power Budget** — idle/peak por subsistema, traversal ~44.7W, batería ≥5400 mAh 4S
2. **Mass Budget** — electrónica conocida ~3041g, motores dominantes 2160g, estructura [TBM]
3. **RF Link Budget** — Friis a 50m/2.4GHz, margen +35.8 dB, COMM-REQ-001 CLOSED

Valores marcados [DS] (datasheet), [EST] (estimado) o [TBM] (pendiente medición).
Se añadió `\usepackage{amsmath}` para habilitar `\text{}` y `\tfrac{}` en fórmulas.

**Por qué:** ECSS-E-ST-10-06C e ISO 29148 exigen que el SRS incluya presupuestos de
ingeniería derivados de datos reales. Sin ellos, requisitos como RNF-007 (MOD ≥2h)
y COMM-REQ-001 (50m LoS) no tienen respaldo cuantitativo. Los [TBM] cierran durante
la campaña V&V con mediciones reales.

**Fuentes añadidas a references.bib:**
- `rpi5_brief` — Raspberry Pi 5 Product Brief (Raspberry Pi Ltd, 2023)
- `arduino_mega_ds` — Arduino Mega 2560 Rev3 Datasheet (Arduino LLC, 2012)
- `imx219_ds` — IMX219 CMOS Image Sensor Datasheet (Sony, 2019)
- `friis_1946` — "A Note on a Simple Transmission Formula" (Friis, IRE 1946)
- `ieee_802_11n` — IEEE Std 802.11n-2009 (IEEE, DOI 10.1109/IEEESTD.2009.5307322)

---

## Sesión 2026-04-02 — Auditoría interna SRS vs implementación

### Hallazgos principales
- RF-001/GNC-REQ-001: VisionSource implementado y funcional; brecha = FOV físico lente IMX219
- RF-002/GNC-REQ-002: YOLOv8n-seg implementado; brecha = benchmark ≥95% con dataset real
- RNF-003: Encoders implementados; brecha = calibración y medición vs ground truth físico
- COMM-REQ-002/003: Hardware UHF disponible pero integración postergada (CR-001)

---

## Anti-patterns corregidos

| # | Anti-pattern | Requisito afectado | Corrección |
|---|-------------|-------------------|------------|
| Q-1 | Requisito compuesto (OR) | SYS-FUN-040 | Dividido en 040a + 040b |
| Q-2 | Métrica sin fuente técnica | USA-REQ-001 (luminancia) | Añadida cita AbraxSys + 1000 cd/m² a ≥50000 lux |
| Q-3 | ID de requisito reutilizado | RF-004 | Supersession formal con CR-002, ID inmutable |
| Q-4 | Terminología estadística incorrecta | RNF-007 (MTBF→MOD) | Renombrado con justificación técnica |
| Q-5 | Brechas de trazabilidad código↔req | MODE-001..006 | Tabla formal §9.4 añadida |
| Q-6 | Sin capa StRS | §5 Stakeholders | Registro SN-001..008 añadido |
