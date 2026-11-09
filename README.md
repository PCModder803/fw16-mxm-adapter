# FW16 Expansion Bay -> MXM adapter : schematic v4 (full mock-up, with placeholders)

Open `fw16_mxm_adapter.kicad_pro` in KiCad (built and checked with KiCad 10). The project
footprint library `fw16_mxm.pretty` is registered through `fp-lib-table`.
`fw16_mxm_adapter_schematic.pdf` shows the same schematic (one A0 sheet) with no KiCad needed.
`fw16_mxm_adapter_bom_draft.csv` lists every part with its footprint and notes; "TBD" marks an unresolved choice.

Target: Graphics Module bay, MXM 3.0 Type B card (X-Vision RX 6600 XT): 100 W total board power
(105 W TDP), 82 x 105 mm, 0-55 C operating, supplied bare with no cooler. At 100 W it draws 5.0 A from
VSYS at 20 V (AC) or 6.6 A at 15.2 V (battery), within the eFuse's 9.9 A limit and the host's 10.5 A.

Third-party documents (Framework's PDFs and drawings, datasheets, and the crops in `reference/evidence/`)
are kept locally but not published in this repository; the tables below name each source.
The community board this started from is on the Framework forum (t/74018).

## What is in the schematic
| Block | Parts | Source |
|---|---|---|
| Signal interposer | J1, 74 pins | FrameworkComputer/ExpansionBay Electrical/README.md |
| Power interposer | J2, 74 pins | same |
| MXM 3.0 socket | J3, 278 pins (Foxconn AS0B826-S55B-7H) | MXM 3.1 r1.0 Table 3.2/3.3 (all 278 pins checked); ADLINK MXM-AXe + Advantech SKY-MXM-RTX3000 manuals |
| MXM system-board parts | U6 SN74LV1T08 (card PWR_EN = 1.8 V host PWR_EN AND eFuse PG, at 3.3 V; R19 100k pull-down, R40 PG pull-up, C48); R36 PEX_STD_SW# 7.15k pull-down; R37 PWR_GOOD and R38 TH_ALERT# 10k pull-ups | MXM 3.1 sec 3.4.1, Tables 3.6, 3.11, 3.30 |
| PCIe x8 | R20-R35 0R (host->card), C10-C25 220 nF (card->host) | community board + a-little-wifi frmw-16-MXM-E-port |
| DisplayPort A (internal panel) | C26-C35 100 nF DC blocking; HPD direct, R14 DNP | Advantech manual: DC blocking + HPD conditioning on the system board |
| Card power | D1 SMBJ20A; U1 TPS25982 eFuse: ILIM 147R = 9.9 A, UVLO 6.5 V (442k/100k), IMON 1.33k, dVdT 4.7 nF (~1 V/ms), retry 2.2 nF (~100 ms, 4 retries then latch-off); C1/C4 EEH-ZA1V101P | TI datasheet SLVSEI3D equations; SMBJ20A / EEH-ZA1V101P distributor data |
| 5 V / 3.3 V | host 5V_ALW (2.5 A) / 3V3_ALW (2.0 A), C2/C3 bulk | ExpansionBay README |
| Power control | host PWR_EN (1.8 V APU GPIO) -> U6 -> MXM PWR_EN; MXM PWR_GOOD -> host PWR_GOOD and pin 53 | MXM 3.1 sec 3.4.1; 1.8 V level from Framework forum t/74018 post 233; U6 per TI SCLS739F |
| PEX_RST# source | R41 0R (fitted): host PEX_RST#. R42 0R DNP: power pin 52 (EC's EXT_SSD1_RST# in SSD-mode descriptors). Fit one only | Fallback for the BIOS dropping PEX_RST# with x8 descriptors (forum t/74018 posts 201-203) |
| Thermal / panel | TH_OVERT#, TH_ALERT#, PNL_* straight J1 <-> J3 | community board, a-little-wifi |
| Module EEPROM | U3 BR24G32 (32 Kbit) at 0x50 on I2C_*_ALW | FW EC gpu_configuration.c reads 0x50 with 16-bit offsets |
| Module ID | R1/R2 330k on ID0/ID1 -> BOARD_VERSION_12 on both = "dual interposer device" | FW EC gpu.c + adc.c thresholds (pull-up rail inferred) |
| Power pins 52/53 | R13 0R: PWR_GOOD -> pin 53 (FBVDD_PWRGD in GPU mode); pin 52 (GC6_FB_EN3V3) NC; MXM SMB_CLK/DAT NC | FW16 7040 mainboard interface schematic p.3 (UC77 / UC78) |
| Fans (graphics bay) | J4/J5 Hefeng AFC58-S04FIA-R1: 1 +12V, 2 SPEED, 3 PWM, 4 GND | FW_EXPANSION_BAY_PCB sheet 2 pin table; Hefeng AFC58 drawing; Cooler Master UMA fan spec (FPC 1 = -, 4 = +, mirrored) |
| Fan-control sensor | U4 F75303M (MSOP-10) @0x4D on I2C_*_ALW, remote diodes Q1/Q2 (MMBT3906) on the card's VRM / VRAM, C46/C47 2.2 nF across D+/D- | Framework PCIE_THERMAL_3RDPARTY descriptor; pinout and filter caps from LCFC NM-D471 sheet 77; address 0x4D (8-bit 0x9A) from the FW16 mainboard's own F75303M (7040 interface schematic p.9) |

## Footprints
- Stock KiCad footprints for passives, D1 (D_SMB), U3 (TSSOP-8) and U4 (MSOP-10_3x3mm_P0.5mm).
- U4 F75303M pinout: 1 VCC, 2 DP1, 3 DN1, 4 DP2, 5 DN2, 6 GND, 7 THERM#, 8 ALERT#, 9 SDA, 10 SCL, read
  from the LCFC NM-D471 laptop schematic, sheet 77 (`reference/evidence/lcfc_nmd471_f75303m_pinout.png`).
- `TI_RGE0024M_VQFN-24_4x4mm_P0.5mm_2EP` (U1): TI example board layout 4223975/B. Pads 0.575 x 0.24 at
  0.5 mm, rows at 3.825 mm; pad 25 (IN) 2.7 x 1.45 at y -0.625, pad 26 (GND) 2.7 x 0.85 at y +0.925.
  Paste is not windowed yet; use TI's stencil drawing.
- `Hefeng_AFC58-S04F_1x04_P0.5mm_Horizontal` (J4/J5): Hefeng drawing. Pads 0.30 x 1.10 at 0.5 mm; nail pads
  1.0 x 2.0, inner edge 1.60 from pin 1, top edge 1.60 below the signal pads (read off the drawing; check it).
- Source drawings for both, and for the fan pinout, are in `reference/evidence/`.
- The interposer and MXM footprints in `fw16_mxm.pretty` were built from the community board in `reference/`:
  - `FW16_FXBeam_Signal` / `FW16_FXBeam_Power`: the community interposer footprint split in two, with pads
    renumbered by position to the Framework README pin numbers. This also removes the duplicate PJ1/PJ2/PJ3
    pad bug. Both footprints keep the original origin, so **J1 and J2 must be placed at the same XY**.
    The pad geometry is unverified against the FXBeam drawing.
  - `MXM3_AS0B826-S55B-7H`: the merged power pads are split so every MXM pin has a pad.
    S55B is chosen: 5.5 mm overall with a 2.7 mm gap under the card (Critical Link wiki; confirm on the
    Foxconn drawing). The adapter PCB is 1.2 mm, matching Framework's reference board and its M2 inserts.
  - The 2.7 mm interposer screw holes are 16.65 mm apart, matching Framework's FW_EXPANSION_BAY_PCB_0807
    drawing (`reference/framework_pcb_ref/`). They still need a solder ring for the ES00000NY00 insert.
- Every symbol pin has a matching footprint pad (checked from the netlist); all 78 parts have footprints.

## How the FW16 EC handles the bay (from FrameworkComputer/EmbeddedController, lotus sources)
- The EC reads ID0/ID1 on its ADC. BOARD_VERSION_12 on both is "dual interposer device". The bay only
  powers up while the F_BEAM hatch switch is closed.
- It then turns on the module's 3V/5V and waits 150 ms. Next it reads the EEPROM at 0x50 (fallback 0x52)
  with 16-bit offsets on I2C_PORT_GPU0, the ALW bus.
- **VSYS and the fans are enabled only by the EEPROM descriptor.** A blank EEPROM makes the EC fall back
  to dual-SSD mode (PCIe x4x2) with no GPU power.
- Program the descriptor from ExpansionBayConfigurationGenerator `PCIE_THERMAL_3RDPARTY`. That gives
  PCIE_8X1, VSYS_EN, FAN_EN, 3V_5V_EN and an F75303 at 0x4D for fan control. Two changes:
  - `GPU_PCIE_MUX_SEL` to LOW: the template sets it HIGH, which reroutes DP_A AUX to the SSD2 PCIe clock.
  - `gpio2` (GPU_2A2_GPIO2_EC) to `GPIO_FUNC_ACDC`, `GPIO_OUTPUT_LOW`, `POWER_S3`, as in Framework's r23m
    descriptor. The EC then drives it with `extpower_is_present()` (high on any external power), which
    sets the card's PWR_LEVEL through U2. Left as the template's input, the card stays at reduced power.
- The EC sets `GPU_PRESENT`, which the internal-panel eDP mux path uses, only for vendor `GPU_AMD_R23M`.
  Driving the laptop's own screen from the MXM card may need firmware changes.
- Power pins 52/53 are `GPU_1F3_MUX1` / `GPU_1G3_MUX2` in the EC ("cannot be controlled directly"):
  they go through mainboard switch UC77. With GPU_PCIE_MUX_SEL low they carry GC6_FB_EN3V3 (out) and
  FBVDD_PWRGD (in), and the mainboard ANDs FBVDD_PWRGD with DGPU_PWROK into ALL_GPWRGD (7040 interface
  schematic p.3). The adapter drives pin 53 from PWR_GOOD through R13.
- On Framework's own AMD module, GPIO0_EC is the temperature-fault input, GPIO1_EC is HPD from its PD
  controller, and GPIO2_EC is the AC/DC-mode output. GPIO3_EC is unused.

## Placeholders still in the design (TBD)
- U4 F75303M ALERT#/THERM# are left unconnected; the LCFC design pulls them up (4.7k / 10k to 3V3) only
  because its EC uses them.
- R14 (DNP): not needed. MXM 3.1 puts the 100k DP_A_HPD pull-down on the module.
- Unconnected by choice: TH_PWM, GPIO0/1/3_EC, DGPU_PWM_SEL, WAKE#, MXM SMB_CLK/DAT, power pins 52/54.
- Cover: the stock cover is too low over the card. It needs a 3D-printed replacement whose inside is flat
  at the 15.3 mm level. With S55B on 1.2 mm that leaves ~5 mm over the inductors and ~8.4 mm over the die
  for the cooler. See `RESEARCH_TODO.md` item 6.
- PWR_LEVEL: U2 (74LVC1G07) pulls the card's PWR_LEVEL low whenever GPIO2_EC is low, i.e. on battery.
  The card must then cut power by at least 20% (MXM 3.1 sec 3.4.14); how much the X-Vision VBIOS actually
  cuts is unknown. Leave U2 unfitted for always-full power.

## What was verified (kicad-cli 10)
- ERC: only "symbol library not in library table" warnings, for the symbols embedded by the generator.
  Connector pins are typed passive, so ERC can't catch direction mistakes.
- Netlist: every PCIe/DP lane, sideband net, power rail, eFuse pin and fan net was checked against the
  intended pins.
- Not verified: the drawing's visual layout (no renderer available here), and anything electrical/physical.

## Evidence for the PCIe direction
MXM lane names are system-relative: host PEX_TX -> MXM PEX_TX, MXM PEX_RX -> host PEX_RX.
Sources: a-little-wifi's frmw-16-MXM-E-port and mxm-immobilizer, the community board, and XPModder's IO
module for the Framework side. Confirmed by MXM 3.1 Table 3.6, and on the Framework side by the 7040
interface schematic: host->module lanes are PEG_CTX_C_GRX_* (already AC-coupled on the mainboard), so
R20-R35 stay 0R and the adapter's C10-C25 couple the card's TX.

## Still to do
`RESEARCH_TODO.md` lists everything that needs a document, a measurement or a laptop. After that: write
the EEPROM descriptor, then PCB layout.

`generate_schematic.py` regenerates the schematic (python3 generate_schematic.py out.kicad_sch);
edit it, or have Claude Code edit it, instead of hand-editing the .kicad_sch.

## License
Copyright PCModder803 2026.

This source describes Open Hardware and is licensed under the CERN-OHL-S v2 (see `LICENSE`).
You may redistribute and modify this source and make products using it under the terms of the
CERN-OHL-S v2 (https://ohwr.org/cern_ohl_s_v2.txt). This source is distributed WITHOUT ANY EXPRESS OR
IMPLIED WARRANTY, INCLUDING OF MERCHANTABILITY, SATISFACTORY QUALITY AND FITNESS FOR A PARTICULAR
PURPOSE. Please see the CERN-OHL-S v2 for applicable conditions.
