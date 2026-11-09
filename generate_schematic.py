#!/usr/bin/env python3
"""Generate fw16_mxm_adapter.kicad_sch (KiCad 7 format) with real symbols, wires and labels.

J1/J2 pin NUMBERS come from github.com/FrameworkComputer/ExpansionBay Electrical/README.md
(Signal Interface / Power Interface tables). J3 pin numbers/names come from the MXM 3.1 connector tables in the ADLINK MXM-AXe and
Advantech SKY-MXM-RTX3000 manuals (same connector as MXM 3.0). Pin NAMES carry the intended function.
"""
import uuid, sys, csv

G = 1.27
def g(v): return round(round(v / G) * G, 4)
def U(): return str(uuid.uuid4())
def n(v):
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s

PROJECT = "fw16_mxm_adapter"
ROOT = U()
FONT = "(font (size 1.27 1.27))"

lib_texts, libpins = {}, {}
placed, wires, labels, texts, ncs = [], [], [], [], []
bom = []
cnt = {"pwr": 0, "flg": 0}

# ---------------------------------------------------------------- lib helpers
def rect(x1, y1, x2, y2):
    return (f"(rectangle (start {n(x1)} {n(y1)}) (end {n(x2)} {n(y2)}) "
            f"(stroke (width 0.254) (type default)) (fill (type background)))")

def poly(*pts):
    p = " ".join(f"(xy {n(x)} {n(y)})" for x, y in pts)
    return f"(polyline (pts {p}) (stroke (width 0.254) (type default)) (fill (type none)))"

def pin(name, num, ptype, x, y, angle, length=5.08, hide=False):
    return (name, num, ptype, x, y, angle, length, hide)

def mk_lib(lib_id, ref, value, body, pins, power=False, pn_hide=False,
           nm_hide=False, val_at=(0, 0), ref_hide=False, desc=""):
    short = lib_id.split(":", 1)[1]
    head = (f'(symbol "{lib_id}" ' + ("(power) " if power else "") +
            ("(pin_numbers hide) " if pn_hide else "") +
            f'(pin_names (offset 0.508){" hide" if nm_hide else ""}) (in_bom yes) (on_board yes)')
    parts = [head,
             f'(property "Reference" "{ref}" (at 0 0 0) (effects {FONT}{" hide" if ref_hide else ""}))',
             f'(property "Value" "{value}" (at {n(val_at[0])} {n(val_at[1])} 0) (effects {FONT}))',
             f'(property "Footprint" "" (at 0 0 0) (effects {FONT} hide))',
             f'(property "Datasheet" "" (at 0 0 0) (effects {FONT} hide))',
             f'(property "Description" "{desc}" (at 0 0 0) (effects {FONT} hide))',
             f'(symbol "{short}_0_1" {body})']
    pp = " ".join(
        f'(pin {pt} line (at {n(x)} {n(y)} {a}) (length {n(L)}){" hide" if h else ""} '
        f'(name "{nm}" (effects {FONT})) (number "{num}" (effects (font (size 1.0 1.0)))))'
        for (nm, num, pt, x, y, a, L, h) in pins)
    parts.append(f'(symbol "{short}_1_1" {pp})')
    lib_texts[lib_id] = "\n    ".join(parts) + ")"
    libpins[lib_id] = {p[1]: p for p in pins}

# power symbols --------------------------------------------------------------
def mk_power(net, kind="up"):
    lid = f"pwr:{net}"
    if kind == "gnd":
        body = poly((0, 0), (0, -1.27), (1.27, -1.27), (0, -2.54), (-1.27, -1.27), (0, -1.27))
        mk_lib(lid, "#PWR", net, body, [pin(net, "1", "power_in", 0, 0, 270, 0, True)],
               power=True, pn_hide=True, nm_hide=True, val_at=(0, -3.81), ref_hide=True)
    else:
        body = (poly((-0.762, 1.27), (0, 2.54)) + " " + poly((0, 0), (0, 2.54)) + " " +
                poly((0, 2.54), (0.762, 1.27)))
        mk_lib(lid, "#PWR", net, body, [pin(net, "1", "power_in", 0, 0, 90, 0, True)],
               power=True, pn_hide=True, nm_hide=True, val_at=(0, 3.81), ref_hide=True)

for net in ("+3V3", "+5V", "VSYS", "PWR_SRC"):
    mk_power(net)
mk_power("GND", "gnd")

mk_lib("pwr:PWR_FLAG", "#FLG", "PWR_FLAG",
       poly((0, 0), (0, 1.27), (1.016, 1.905), (0, 2.54), (-1.016, 1.905), (0, 1.27)),
       [pin("pwr", "1", "power_out", 0, 0, 90, 0, True)],
       power=True, pn_hide=True, nm_hide=True, val_at=(0, 3.81), ref_hide=True)

# passives -------------------------------------------------------------------
mk_lib("fw16:R_V", "R", "R", rect(-1.016, -2.54, 1.016, 2.54),
       [pin("~", "1", "passive", 0, 3.81, 270, 1.27), pin("~", "2", "passive", 0, -3.81, 90, 1.27)],
       pn_hide=True, nm_hide=True)
mk_lib("fw16:R_H", "R", "R", rect(-2.54, -1.016, 2.54, 1.016),
       [pin("~", "1", "passive", -3.81, 0, 0, 1.27), pin("~", "2", "passive", 3.81, 0, 180, 1.27)],
       pn_hide=True, nm_hide=True)
mk_lib("fw16:C_V", "C", "C", poly((-2.032, 0.508), (2.032, 0.508)) + " " + poly((-2.032, -0.508), (2.032, -0.508)),
       [pin("~", "1", "passive", 0, 3.81, 270, 3.302), pin("~", "2", "passive", 0, -3.81, 90, 3.302)],
       pn_hide=True, nm_hide=True)
mk_lib("fw16:C_H", "C", "C", poly((-0.508, 2.032), (-0.508, -2.032)) + " " + poly((0.508, 2.032), (0.508, -2.032)),
       [pin("~", "1", "passive", -3.81, 0, 0, 3.302), pin("~", "2", "passive", 3.81, 0, 180, 3.302)],
       pn_hide=True, nm_hide=True)
mk_lib("fw16:TVS_V", "D", "TVS",
       poly((-1.27, -1.27), (1.27, -1.27), (0, 1.27), (-1.27, -1.27)) + " " + poly((-1.27, 1.27), (1.27, 1.27)),
       [pin("K", "1", "passive", 0, 3.81, 270, 2.54), pin("A", "2", "passive", 0, -3.81, 90, 2.54)],
       pn_hide=True, nm_hide=True)

# ICs ------------------------------------------------------------------------
# The FW16 EC reads the module EEPROM at 0x50 (fallback 0x52) with i2c_read_offset16_block, i.e. 16-bit
# offsets (FrameworkComputer/EmbeddedController zephyr/program/framework/lotus/src/gpu_configuration.c),
# so it must be a >=32 Kbit part. Standard 24xx32 pinout; same part as the community board.
mk_lib("fw16:EEPROM_24xx32", "U", "BR24G32FVT-3GE2", rect(-7.62, 10.16, 7.62, -10.16), [
    pin("A0", "1", "passive", -10.16, 7.62, 0, 2.54), pin("A1", "2", "passive", -10.16, 2.54, 0, 2.54),
    pin("A2", "3", "passive", -10.16, -2.54, 0, 2.54), pin("VSS", "4", "power_in", -10.16, -7.62, 0, 2.54),
    pin("VCC", "8", "power_in", 10.16, 7.62, 180, 2.54), pin("WP", "7", "passive", 10.16, 2.54, 180, 2.54),
    pin("SCL", "6", "passive", 10.16, -2.54, 180, 2.54), pin("SDA", "5", "passive", 10.16, -7.62, 180, 2.54)])

# TI TPS25982 eFuse, VQFN-24 (RGE0024M), pinout from datasheet SLVSEI3D Table 5-1. IN, OUT and GND pins are
# stacked on one point each. The exposed pads are 25 (IN, the large pad next to pins 1-3) and 26 (GND), as
# numbered in TI's RGE0024M package drawing. TI lists TPS25983 (26 V, 20 A) as pin-for-pin.
EF_LEFT = [("IN", ["1", "2", "3", "16", "25"], "power_in"), ("EN/UVLO", ["6"], "passive"),
           ("GND", ["4", "5", "14", "26"], "power_in")]
EF_RIGHT = [("OUT", [str(p) for p in range(17, 25)], "passive"), ("PG", ["13"], "passive"), ("ILIM", ["8"], "passive"),
            ("IMON", ["9"], "passive"), ("dVdT", ["15"], "passive"), ("ITIMER", ["7"], "passive"),
            ("RETRY_DLY", ["10"], "passive"), ("NRETRY", ["11"], "passive"), ("LDSTRT", ["12"], "passive")]
efp = []
for side, x, a in ((EF_LEFT, -15.24, 0), (EF_RIGHT, 15.24, 180)):
    for i, (nm, nums, pt) in enumerate(side):
        for num in nums:
            efp.append(pin(nm, num, pt, x, -i * 5.08, a))
mk_lib("fw16:TPS25982", "U", "TPS25982", rect(-10.16, 5.08, 10.16, -(len(EF_RIGHT) - 1) * 5.08 - 5.08), efp)

# Fintek F75303 (10-MSOP, 3.3 V; 1 local + 2 remote diode channels). Framework's PCIE_THERMAL_3RDPARTY
# descriptor drives the bay fans from an F75303 at 0x4D on the module's ALW I2C bus. Pin numbers from the
# LCFC NM-D471 schematic (sheet 77 "Thermal", US301 F75303M_MSOP10): 1 VCC, 2 DP1, 3 DN1, 4 DP2, 5 DN2,
# 6 GND, 7 THERM#, 8 ALERT#, 9 SDA, 10 SCL. Address: the FW16 mainboard's own UTH1 "F75303M_MSOP10"
# (7040 interface schematic p.9, same pinout) is marked "SMB3_Address 1001_101xb 0x9A" = 7-bit 0x4D.
F75_L = [("VDD", "1"), ("D1+", "2"), ("D1-", "3"), ("D2+", "4"), ("D2-", "5")]
F75_R = [("SCL", "10"), ("SDA", "9"), ("ALERT#", "8"), ("THERM#", "7"), ("GND", "6")]
mk_lib("fw16:F75303", "U", "F75303", rect(-10.16, 5.08, 10.16, -22.86),
       [pin(nm, n, "power_in" if nm == "VDD" else "passive", -15.24, -i * 5.08, 0) for i, (nm, n) in enumerate(F75_L)] +
       [pin(nm, n, "power_in" if nm == "GND" else "passive", 15.24, -i * 5.08, 180) for i, (nm, n) in enumerate(F75_R)])
# Single non-inverting open-drain buffer (TI 74LVC1G07 DBV, SOT-23-5: 1 NC, 2 A, 3 GND, 4 Y, 5 VCC)
mk_lib("fw16:74LVC1G07", "U", "74LVC1G07", rect(-5.08, 5.08, 5.08, -7.62), [
    pin("NC", "1", "no_connect", -10.16, 2.54, 0), pin("A", "2", "input", -10.16, -2.54, 0),
    pin("GND", "3", "power_in", 0, -12.7, 90), pin("Y", "4", "open_collector", 10.16, -2.54, 180),
    pin("VCC", "5", "power_in", 0, 10.16, 270)])
# Single-supply AND gate / level shifter (TI SN74LV1T08 DBV, SOT-23-5: 1 A, 2 B, 3 GND, 4 Y, 5 VCC;
# datasheet SCLS739F Table 5-1, reference/evidence/ti_sn74lv1t08_datasheet.pdf). VIH max 1.37 V at VCC 3-3.3 V.
mk_lib("fw16:SN74LV1T08", "U", "SN74LV1T08", rect(-5.08, 5.08, 5.08, -7.62), [
    pin("A", "1", "input", -10.16, 2.54, 0), pin("B", "2", "input", -10.16, -2.54, 0),
    pin("GND", "3", "power_in", 0, -12.7, 90), pin("Y", "4", "output", 10.16, -2.54, 180),
    pin("VCC", "5", "power_in", 0, 10.16, 270)])
# PNP remote-sense transistor (MMBT3906, SOT-23: 1=B 2=E 3=C), wired as a diode: E -> D+, B+C -> D-
mk_lib("fw16:Q_PNP", "Q", "MMBT3906", rect(-2.54, 2.54, 2.54, -2.54), [
    pin("B", "1", "passive", -7.62, 0, 0), pin("E", "2", "passive", 2.54, 7.62, 270, 5.08),
    pin("C", "3", "passive", 2.54, -7.62, 90, 5.08)], pn_hide=False)

# Fan header: Zhejiang Hefeng AFC58-S04FIA-R1, 0.5 mm FPC, lower contact (repo PCB Reference Design/Datasheets
# J200_J201). Pin order from the FW_EXPANSION_BAY_PCB drawing sheet 2 table: 1 +12V, 2 FAN0_SPEED, 3 FAN0_PWM,
# 4 GND. The Cooler Master fan FPC is numbered the other way (FPC 1 = -, 4 = +), so FPC pin n lands on pin 5-n.
mk_lib("fw16:FAN_4P", "J", "AFC58-S04FIA-R1", rect(-7.62, 5.08, 0, -17.78), [
    pin("12V_FAN", "1", "passive", 5.08, 0, 180), pin("SPEED", "2", "passive", 5.08, -5.08, 180),
    pin("PWM", "3", "passive", 5.08, -10.16, 180), pin("GND", "4", "passive", 5.08, -15.24, 180),
    pin("MP", "MP", "passive", 5.08, -15.24, 180)])

# ---------------------------------------------------------------- pin tables
TX = [f"PCIE_TX{i}_{p}" for i in range(8) for p in "PN"]   # host transmits
RX = [f"PCIE_RX{i}_{p}" for i in range(8) for p in "PN"]   # host receives
CTRL = ["REFCLK_P", "REFCLK_N", "PERST_N", "CLKREQ_N"]   # no WAKE# on either interposer
DP = [f"DP_ML{i}_{p}" for i in range(4) for p in "PN"] + ["DP_AUX_P", "DP_AUX_N", "DP_HPD"]

rows, y = {}, 0.0
for grp in (TX, RX, CTRL, DP):
    for nm in grp:
        rows[nm] = round(y, 4); y += 5.08
    y += 5.08
# ExpansionBay Electrical/README.md, Signal Interface table: generator name -> pin number.
# Repo naming (module-side I/O column): PEX_TX = I to module, PEX_RX = O from module.
J1_NUM = {}
for i, (tp, rp) in enumerate(((2, 26), (5, 29), (8, 32), (11, 35), (14, 38), (17, 41), (20, 44), (23, 47))):
    J1_NUM[f"PCIE_TX{i}_P"], J1_NUM[f"PCIE_TX{i}_N"] = tp, tp + 1      # PEX_TXn / PEX_TXn#
    J1_NUM[f"PCIE_RX{i}_P"], J1_NUM[f"PCIE_RX{i}_N"] = rp, rp + 1      # PEX_RXn / PEX_RXn#
for i, p in enumerate((57, 60, 63, 66)):
    J1_NUM[f"DP_ML{i}_P"], J1_NUM[f"DP_ML{i}_N"] = p, p + 1            # DP_A_Ln / DP_A_Ln#
J1_NUM.update({
    "REFCLK_P": 50, "REFCLK_N": 51,        # PEX_REFCLK / PEX_REFCLK#
    "PERST_N": 53, "CLKREQ_N": 54,         # PEX_RST# / PEX_CLK_REQ#
    "DP_AUX_P": 69, "DP_AUX_N": 70, "DP_HPD": 56,
    "BOARD_ID1": 73,                       # ID1
    "PROCHOT_N": 65,                       # TH_OVERT# ("PROCHOT#")
    "THRM_INT_N": 68,                      # TH_ALERT# ("Thermal interrupt request")
    "GPU_GPIO0": 59,                       # GPIO2_EC ("Connect to GPU GPIO0")
    "EC_GPIO": 74,                         # GPIO3_EC ("Connect to EC GPIO")
    "DGPU_PWM_SEL": 55, "PNL_BL_EN": 62, "PNL_PWR_EN": 71, "PNL_BL_PWM": 72,
})
J1_GND = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49, 52]
# BOARD_ID0 (ID0) and the EEPROM I2C bus (I2C_CLK/DAT_ALW) are on the POWER interposer, so they're on J2.
J1_LEFT = ["BOARD_ID1", "PROCHOT_N", "THRM_INT_N", "GPU_GPIO0", "EC_GPIO",
           "DGPU_PWM_SEL", "PNL_BL_EN", "PNL_PWR_EN", "PNL_BL_PWM"] + ["GND"] * len(J1_GND)
J1_NC = ("EC_GPIO", "DGPU_PWM_SEL")   # GPU_GPIO0 (GPIO2_EC) drives PWR_LEVEL through U2

# ExpansionBay Electrical/README.md, Power Interface table: pin number -> repo signal name.
J2_PINS = {p: "VSYS_GPU" for p in range(1, 15)}
J2_PINS.update({p: "GND" for p in [*range(15, 27), 31, 32, 33, 38, 39, 40, *range(47, 52), 55, 58, 70]})
J2_PINS.update({p: "5V_ALW" for p in range(27, 31)})
J2_PINS.update({p: "3V3_ALW" for p in range(34, 38)})
J2_PINS.update({p: "VADP_GPU" for p in range(41, 47)})
J2_PINS.update({52: "EXT_SSD1_RST#", 53: "EXT_SSD2_RST#", 54: "EXT_SSD2_CLK_REQ#", 56: "USB+", 57: "USB-",
                59: "I2C_INT_ALW", 60: "I2C_CLK_ALW", 61: "I2C_DAT_ALW", 62: "GPIO0_EC", 63: "GPIO1_EC",
                64: "ID0", 65: "12V_FAN", 66: "Fan0_PWM", 67: "Fan1_PWM", 68: "Fan0_SPEED", 69: "Fan1_SPEED",
                71: "DDS_SDA", 72: "PWR_EN", 73: "PWR_GOOD", 74: "DDS_CLK"})
assert sorted(J2_PINS) == list(range(1, 75))
assert sorted(list(J1_NUM.values()) + J1_GND) == list(range(1, 75))
# MXM 3.x connector, pin number -> name, from the MXM 3.1 pin tables in the ADLINK MXM-AXe and
# Advantech SKY-MXM-RTX3000 manuals. Pins 126-132 are the key gap. Pins 10/14/16/31/38-45 carry
# MXM 3.1 names (RSVD/OEM on 3.0 cards); all of them are left unconnected here.
MXM_PINS = dict(t.split(":") for t in """
    1:5V 2:PRSNT_R# 3:5V 4:WAKE# 5:5V 6:PWR_GOOD 7:5V 8:PWR_EN 9:5V 10:27MHZ_REF
    11:GND 12:GND 13:GND 14:LVDS_U_HPD 15:GND 16:JTAG_TESTEN 17:GND 18:PWR_LEVEL 19:PEX_STD_SW# 20:TH_OVERT#
    21:VGA_DISABLE# 22:TH_ALERT# 23:PNL_PWR_EN 24:TH_PWM 25:PNL_BL_EN 26:GPIO0 27:PNL_BL_PWM 28:GPIO1 29:HDMI_CEC 30:GPIO2
    31:LVDS_L_HPD 32:SMB_DAT 33:LVDS_DDC_DAT 34:SMB_CLK 35:LVDS_DDC_CLK 36:GND 37:GND 38:OEM0 39:OEM1 40:OEM2
    41:OEM3 42:OEM4 43:OEM5 44:OEM6 45:OEM7 46:GND 47:GND 48:PEX_TX15# 49:PEX_RX15# 50:PEX_TX15
    51:PEX_RX15 52:GND 53:GND 54:PEX_TX14# 55:PEX_RX14# 56:PEX_TX14 57:PEX_RX14 58:GND 59:GND 60:PEX_TX13#
    61:PEX_RX13# 62:PEX_TX13 63:PEX_RX13 64:GND 65:GND 66:PEX_TX12# 67:PEX_RX12# 68:PEX_TX12 69:PEX_RX12 70:GND
    71:GND 72:PEX_TX11# 73:PEX_RX11# 74:PEX_TX11 75:PEX_RX11 76:GND 77:GND 78:PEX_TX10# 79:PEX_RX10# 80:PEX_TX10
    81:PEX_RX10 82:GND 83:GND 84:PEX_TX9# 85:PEX_RX9# 86:PEX_TX9 87:PEX_RX9 88:GND 89:GND 90:PEX_TX8#
    91:PEX_RX8# 92:PEX_TX8 93:PEX_RX8 94:GND 95:GND 96:PEX_TX7# 97:PEX_RX7# 98:PEX_TX7 99:PEX_RX7 100:GND
    101:GND 102:PEX_TX6# 103:PEX_RX6# 104:PEX_TX6 105:PEX_RX6 106:GND 107:GND 108:PEX_TX5# 109:PEX_RX5# 110:PEX_TX5
    111:PEX_RX5 112:GND 113:GND 114:PEX_TX4# 115:PEX_RX4# 116:PEX_TX4 117:PEX_RX4 118:GND 119:GND 120:PEX_TX3#
    121:PEX_RX3# 122:PEX_TX3 123:PEX_RX3 124:GND 125:GND 133:GND 134:GND 135:PEX_RX2# 136:PEX_TX2# 137:PEX_RX2
    138:PEX_TX2 139:GND 140:GND 141:PEX_RX1# 142:PEX_TX1# 143:PEX_RX1 144:PEX_TX1 145:GND 146:GND 147:PEX_RX0#
    148:PEX_TX0# 149:PEX_RX0 150:PEX_TX0 151:GND 152:GND 153:PEX_REFCLK# 154:PEX_CLK_REQ# 155:PEX_REFCLK 156:PEX_RST# 157:GND
    158:VGA_DDC_DAT 159:JTAG_TDO 160:VGA_DDC_CLK 161:JTAG_TDI 162:VGA_VSYNC 163:JTAG_TCLK 164:VGA_HSYNC 165:JTAG_TMS 166:GND 167:JTAG_TRST#
    168:VGA_RED 169:LVDS_UCLK# 170:VGA_GREEN 171:LVDS_UCLK 172:VGA_BLUE 173:GND 174:GND 175:LVDS_UTX3# 176:LVDS_LCLK# 177:LVDS_UTX3
    178:LVDS_LCLK 179:GND 180:GND 181:LVDS_UTX2# 182:LVDS_LTX3# 183:LVDS_UTX2 184:LVDS_LTX3 185:GND 186:GND 187:LVDS_UTX1#
    188:LVDS_LTX2# 189:LVDS_UTX1 190:LVDS_LTX2 191:GND 192:GND 193:LVDS_UTX0# 194:LVDS_LTX1# 195:LVDS_UTX0 196:LVDS_LTX1 197:GND
    198:GND 199:DP_C_L0# 200:LVDS_LTX0# 201:DP_C_L0 202:LVDS_LTX0 203:GND 204:GND 205:DP_C_L1# 206:DP_D_L0# 207:DP_C_L1
    208:DP_D_L0 209:GND 210:GND 211:DP_C_L2# 212:DP_D_L1# 213:DP_C_L2 214:DP_D_L1 215:GND 216:GND 217:DP_C_L3#
    218:DP_D_L2# 219:DP_C_L3 220:DP_D_L2 221:GND 222:GND 223:DP_C_AUX# 224:DP_D_L3# 225:DP_C_AUX 226:DP_D_L3 227:RSVD
    228:GND 229:RSVD 230:DP_D_AUX# 231:RSVD 232:DP_D_AUX 233:RSVD 234:DP_C_HPD 235:RSVD 236:DP_D_HPD 237:RSVD
    238:RSVD 239:RSVD 240:3V3 241:RSVD 242:3V3 243:RSVD 244:GND 245:RSVD 246:DP_B_L0# 247:RSVD
    248:DP_B_L0 249:RSVD 250:GND 251:GND 252:DP_B_L1# 253:DP_A_L0# 254:DP_B_L1 255:DP_A_L0 256:GND 257:GND
    258:DP_B_L2# 259:DP_A_L1# 260:DP_B_L2 261:DP_A_L1 262:GND 263:GND 264:DP_B_L3# 265:DP_A_L2# 266:DP_B_L3 267:DP_A_L2
    268:GND 269:GND 270:DP_B_AUX# 271:DP_A_L3# 272:DP_B_AUX 273:DP_A_L3 274:DP_B_HPD 275:GND 276:DP_A_HPD 277:DP_A_AUX#
    278:3V3 279:DP_A_AUX 280:3V3 281:PRSNT_L# E1:PWR_SRC E2:PWR_SRC E3:GND E4:GND
""".split())
assert len(MXM_PINS) == 278

# Generator net name -> MXM pin name. MXM lane names are system-relative (PEX_TX = system transmits,
# card receives), so host PEX_TX goes straight to MXM PEX_TX: no crossover by name.
MXM_NAME = {}
for i in range(8):
    for p, sfx in (("P", ""), ("N", "#")):
        MXM_NAME[f"PCIE_TX{i}_{p}"] = f"PEX_TX{i}{sfx}"
        MXM_NAME[f"PCIE_RX{i}_{p}"] = f"PEX_RX{i}{sfx}"
for i in range(4):
    for p, sfx in (("P", ""), ("N", "#")):
        MXM_NAME[f"DP_ML{i}_{p}"] = f"DP_A_L{i}{sfx}"
MXM_NAME.update({"DP_AUX_P": "DP_A_AUX", "DP_AUX_N": "DP_A_AUX#", "DP_HPD": "DP_A_HPD",
                 "REFCLK_P": "PEX_REFCLK", "REFCLK_N": "PEX_REFCLK#", "PERST_N": "PEX_RST#",
                 "CLKREQ_N": "PEX_CLK_REQ#"})
MXM_NUM = {nm: num for num, nm in MXM_PINS.items()}      # only used for names that occur once
# MXM sideband pin -> net label. Thermal and panel pins go to the matching J1 interposer pins (same
# pairing as the community board and a-little-wifi's frmw-16-MXM-E-port). PWR_EN/PWR_GOOD go to J2;
# PWR_EN reaches the card through U6 (1.8 V -> 3.3 V, ANDed with the eFuse PG; MXM 3.1 sec 3.4.1).
J3_SIDE = {"PWR_EN": "MXM_PWR_EN", "PWR_GOOD": "PWR_GOOD", "PRSNT_R#": "PRSNT_R", "PRSNT_L#": "PRSNT_L",
           "PEX_STD_SW#": "PEX_STD_SW", "PWR_LEVEL": "MXM_PWR_LEVEL",
           "TH_OVERT#": "PROCHOT_N", "TH_ALERT#": "THRM_INT_N",
           "PNL_PWR_EN": "PNL_PWR_EN", "PNL_BL_EN": "PNL_BL_EN", "PNL_BL_PWM": "PNL_BL_PWM"}
# MXM SMB_CLK/SMB_DAT stay unconnected: the FW16 mainboard has no SMBus on power pins 52/53 in GPU mode
# (FW16 7040 interface schematic p.3: UC77 routes them to GC6_FB_EN3V3 / FBVDD_PWRGD).
J3_POWER = {"PWR_SRC": "PWR_SRC", "5V": "+5V", "3V3": "+3V3", "GND": "GND"}   # MXM name -> power net
for nm in list(MXM_NAME.values()) + list(J3_SIDE):
    assert list(MXM_PINS.values()).count(nm) == 1, nm

def j3name(nm):
    return MXM_NAME[nm]

# J1 : right-side pin column at x=0, body to the left
p1, tbd, gnd = [], iter(range(1, 100)), iter(J1_GND)
def j1num(nm):
    if nm == "GND": return str(next(gnd))
    return str(J1_NUM[nm]) if nm in J1_NUM else f"TBD{next(tbd):02d}"
for nm, yo in rows.items():
    p1.append(pin(nm, j1num(nm), "passive", 0, -yo, 180))
j1_left = []
for i, nm in enumerate(J1_LEFT):
    j1_left.append((nm, j1num(nm)))
    p1.append(pin(nm, j1_left[-1][1], "passive", -40.64, -i * 5.08, 0))
ymax1 = max(max(rows.values()), (len(J1_LEFT) - 1) * 5.08)
mk_lib("fw16:J1_FW16_ExpBay_Signal", "J", "FW16_ExpBay_Signal", rect(-35.56, 5.08, -5.08, -(ymax1 + 5.08)), p1)

# J3 : left-side pin column at x=0, body to the right. Right side: sideband pins, then each power
# rail with all its pins stacked on one point, then every unused pin (no-connect) at 2.54 pitch.
p3, used3, ry = [], set(), 0.0
for nm, yo in rows.items():
    num = MXM_NUM[j3name(nm)]
    p3.append(pin(j3name(nm), num, "passive", 0, -yo, 0)); used3.add(num)
for mx in J3_SIDE:
    p3.append(pin(mx, MXM_NUM[mx], "passive", 40.64, -ry, 180)); used3.add(MXM_NUM[mx]); ry += 5.08
for mx in J3_POWER:
    for num, nm in MXM_PINS.items():
        if nm == mx:
            p3.append(pin(nm, num, "power_in", 40.64, -ry, 180)); used3.add(num)
    ry += 5.08
ry += 5.08
j3_nc = []
for num, nm in MXM_PINS.items():
    if num not in used3:
        p3.append(pin(nm, num, "passive", 40.64, -ry, 180)); j3_nc.append(num); ry += 2.54
ymax3 = max(max(rows.values()), ry)
mk_lib("fw16:J3_MXM3_Card", "J", "MXM3_Card", rect(5.08, 5.08, 35.56, -(ymax3 + 5.08)), p3)

# J2 : power interposer, pins 1-37 on the right, 38-74 on the left
p2 = [pin(nm, str(p), "passive", 0, -(p - 1) * 5.08, 180) if p <= 37 else
      pin(nm, str(p), "passive", -40.64, -(p - 38) * 5.08, 0) for p, nm in sorted(J2_PINS.items())]
mk_lib("fw16:J2_FW16_ExpBay_Power", "J", "FW16_ExpBay_Power", rect(-35.56, 5.08, -5.08, -(36 * 5.08 + 5.08)), p2)

# ---------------------------------------------------------------- placement
# Footprints: stock KiCad libraries for generic parts; fw16_mxm.pretty (project library, built from the
# community reference board) for the interposers and MXM socket. "" = not chosen yet (see BOM notes).
FP = {"R0402": "Resistor_SMD:R_0402_1005Metric", "R0603": "Resistor_SMD:R_0603_1608Metric",
      "C0402": "Capacitor_SMD:C_0402_1005Metric", "C0603": "Capacitor_SMD:C_0603_1608Metric",
      "C1206": "Capacitor_SMD:C_1206_3216Metric", "SMB": "Diode_SMD:D_SMB",
      "TSSOP8": "Package_SO:TSSOP-8_4.4x3mm_P0.65mm", "CP8": "Capacitor_SMD:CP_Elec_8x10.5",
      "SOT23": "Package_TO_SOT_SMD:SOT-23", "MSOP10": "Package_SO:MSOP-10_3x3mm_P0.5mm",
      "SOT23_5": "Package_TO_SOT_SMD:SOT-23-5",
      "SIG": "fw16_mxm:FW16_FXBeam_Signal", "PWR": "fw16_mxm:FW16_FXBeam_Power",
      "MXM": "fw16_mxm:MXM3_AS0B826-S55B-7H",
      "RGE": "fw16_mxm:TI_RGE0024M_VQFN-24_4x4mm_P0.5mm_2EP",
      "AFC": "fw16_mxm:Hefeng_AFC58-S04F_1x04_P0.5mm_Horizontal", "TBD": ""}

def place(lib_id, ref, value, ox, oy, ref_at=(2.54, -1.27), val_at=(2.54, 1.27),
          hide_text=False, just="left", note="", fp=""):
    ox, oy = g(ox), g(oy)
    ref_ = ref
    if lib_id.startswith("pwr:"):
        hide_text = True
    hid = " hide" if hide_text else ""
    jf = f" (justify {just})" if just else ""
    pins = libpins[lib_id]
    s = (f'(symbol (lib_id "{lib_id}") (at {n(ox)} {n(oy)} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)\n'
         f'    (uuid "{U()}")\n'
         f'    (property "Reference" "{ref_}" (at {n(ox + ref_at[0])} {n(oy + ref_at[1])} 0) (effects {FONT}{jf}{hid}))\n'
         f'    (property "Value" "{value}" (at {n(ox + val_at[0])} {n(oy + val_at[1])} 0) (effects {FONT}{jf}{hid}))\n'
         f'    (property "Footprint" "{fp}" (at {n(ox)} {n(oy)} 0) (effects {FONT} hide))\n'
         f'    (property "Datasheet" "" (at {n(ox)} {n(oy)} 0) (effects {FONT} hide))\n')
    for num in pins:
        s += f'    (pin "{num}" (uuid "{U()}"))\n'
    s += (f'    (instances (project "{PROJECT}" (path "/{ROOT}" (reference "{ref_}") (unit 1)))))')
    placed.append(s)
    if not lib_id.startswith("pwr:"):
        bom.append((ref, value, fp or "TBD", note))
    return {num: (round(ox + p[3], 4), round(oy - p[4], 4)) for num, p in pins.items()}, \
           {p[0]: [] for p in pins.values()}

def pos(lib_id, ox, oy):
    ox, oy = g(ox), g(oy)
    return {num: (round(ox + p[3], 4), round(oy - p[4], 4)) for num, p in libpins[lib_id].items()}

def wire(x1, y1, x2, y2):
    wires.append(f'(wire (pts (xy {n(x1)} {n(y1)}) (xy {n(x2)} {n(y2)})) '
                 f'(stroke (width 0) (type default)) (uuid "{U()}"))')

def label(name, x, y, angle=0):
    just = "left bottom" if angle == 0 else "right bottom"
    labels.append(f'(label "{name}" (at {n(x)} {n(y)} {angle}) (fields_autoplaced) '
                  f'(effects {FONT} (justify {just})) (uuid "{U()}"))')

def note(x, y, msg, size=1.5, bold=False):
    msg = msg.replace('"', "'")
    texts.append(f'(text "{msg}" (at {n(g(x))} {n(g(y))} 0) '
                 f'(effects (font (size {size} {size}){" bold" if bold else ""}) (justify left)) (uuid "{U()}"))')

def stub(pt, d, length=5.08):
    dx, dy = {"L": (-length, 0), "R": (length, 0), "U": (0, -length), "D": (0, length)}[d]
    e = (round(pt[0] + dx, 4), round(pt[1] + dy, 4))
    wire(pt[0], pt[1], e[0], e[1])
    return e

def power_at(net, pt):
    cnt["pwr"] += 1
    ref = f"#PWR{cnt['pwr']:03d}"
    show = net != "GND"
    lid = f"pwr:{net}"
    ox, oy = pt
    vy = (-3.81 if net == "GND" else 3.81)
    s = (f'(symbol (lib_id "{lid}") (at {n(ox)} {n(oy)} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)\n'
         f'    (uuid "{U()}")\n'
         f'    (property "Reference" "{ref}" (at {n(ox)} {n(oy)} 0) (effects {FONT} hide))\n'
         f'    (property "Value" "{net}" (at {n(ox)} {n(oy - vy if net != "GND" else oy - vy)} 0) (effects {FONT}{"" if show else " hide"}))\n'
         f'    (property "Footprint" "" (at {n(ox)} {n(oy)} 0) (effects {FONT} hide))\n'
         f'    (property "Datasheet" "" (at {n(ox)} {n(oy)} 0) (effects {FONT} hide))\n'
         f'    (pin "1" (uuid "{U()}"))\n'
         f'    (instances (project "{PROJECT}" (path "/{ROOT}" (reference "{ref}") (unit 1)))))')
    placed.append(s)

def flag_at(pt):
    cnt["flg"] += 1
    ref = f"#FLG{cnt['flg']:03d}"
    ox, oy = pt
    s = (f'(symbol (lib_id "pwr:PWR_FLAG") (at {n(ox)} {n(oy)} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)\n'
         f'    (uuid "{U()}")\n'
         f'    (property "Reference" "{ref}" (at {n(ox)} {n(oy)} 0) (effects {FONT} hide))\n'
         f'    (property "Value" "PWR_FLAG" (at {n(ox)} {n(oy - 3.81)} 0) (effects {FONT} hide))\n'
         f'    (property "Footprint" "" (at {n(ox)} {n(oy)} 0) (effects {FONT} hide))\n'
         f'    (property "Datasheet" "" (at {n(ox)} {n(oy)} 0) (effects {FONT} hide))\n'
         f'    (pin "1" (uuid "{U()}"))\n'
         f'    (instances (project "{PROJECT}" (path "/{ROOT}" (reference "{ref}") (unit 1)))))')
    placed.append(s)

def to_label(pt, d, name, length=5.08):
    e = stub(pt, d, length)
    label(name, e[0], e[1], 180 if d == "L" else 0)

def to_power(pt, d, net, length=2.54):
    power_at(net, stub(pt, d, length))

def to_flag(pt, d="R", length=5.08):
    flag_at(stub(pt, d, length))

def to_nc(pt):
    ncs.append(f'(no_connect (at {n(pt[0])} {n(pt[1])}) (uuid "{U()}"))')

# ------------------------------------------------------------ main block
J1X, J1Y = g(120), g(60)
J3X, J3Y = g(254), g(60)
CX = g(185)

place("fw16:J1_FW16_ExpBay_Signal", "J1", "FW16_ExpBay_Signal", J1X, J1Y,
      ref_at=(-35.56, -10.16), val_at=(-35.56, -7.62), just="left", fp=FP["SIG"],
      note="Framework Expansion Bay signal interposer. Pinout from FrameworkComputer/ExpansionBay Electrical/README.md; place at the same XY as J2")
place("fw16:J3_MXM3_Card", "J3", "AS0B826-S55B-7H", J3X, J3Y,
      ref_at=(5.08, -10.16), val_at=(5.08, -7.62), just="left", fp=FP["MXM"],
      note="MXM 3.0 Type B socket (target X-Vision RX 6600 XT); S55B chosen against the bay's 9 mm ceiling, 5.5 mm overall, 2.7 mm card gap (confirm on Foxconn drawing). Pinout from ADLINK/Advantech MXM 3.1 tables")
p1 = pos("fw16:J1_FW16_ExpBay_Signal", J1X, J1Y)
p3 = pos("fw16:J3_MXM3_Card", J3X, J3Y)
p1n = {libpins["fw16:J1_FW16_ExpBay_Signal"][num][0]: [] for num in p1}
for num, pnt in p1.items():
    p1n[libpins["fw16:J1_FW16_ExpBay_Signal"][num][0]].append((num, pnt))
p3n = {}
for num, pnt in p3.items():
    p3n.setdefault(libpins["fw16:J3_MXM3_Card"][num][0], []).append((num, pnt))

# Series part per lane, following the community board and a-little-wifi's frmw-16-MXM-E-port:
#   host PEX_TX -> card : 0R link (the host transmitter has its own AC caps); pads take a cap if needed
#   card PEX_RX -> host : 220nF AC coupling for the card's transmitter, placed on the system side
#   DP_A lanes + AUX    : 100nF DC blocking, which MXM puts on the system board (Advantech manual)
#   DP_A_HPD            : DC level, wired straight through (pull-down R14 is DNP)
DP_AC = [nm for nm in DP if nm != "DP_HPD"]
capn, rlink = 10, 20
for nm, yo in rows.items():
    a = p1n[nm][0][1]                       # J1 pin point
    b = p3n[j3name(nm)][0][1]               # J3 pin point
    if nm in TX or nm in RX or nm in DP_AC:
        cy = a[1]
        c1, c2 = (CX - 3.81, cy), (CX + 3.81, cy)
        if nm in TX:
            place("fw16:R_H", f"R{rlink}", "0R", CX, cy, hide_text=True, fp=FP["R0402"],
                  note="Host->card PCIe link: 0R (host TX already AC-coupled); fit 220nF instead if needed")
            rlink += 1
        else:
            val, why = (("220nF", "Card->host PCIe AC-coupling cap (MXM 3.1 sec 3.4.4: both directions on the system board)") if nm in RX else
                        ("100nF", "DP_A DC-blocking cap (MXM: on the system board)"))
            place("fw16:C_H", f"C{capn}", val, CX, cy, hide_text=True, note=why, fp=FP["C0402"])
            capn += 1
        wire(a[0], a[1], c1[0], c1[1]); wire(c2[0], c2[1], b[0], b[1])
        ln = "HOST_" + nm[5:] if nm in TX or nm in RX else nm              # HOST_TX0_P / DP_ML0_P
        label(ln, a[0] + 7.62, cy)
        label("MXM_" + j3name(nm), c2[0] + 5.08, cy)                      # MXM_PEX_TX0 / MXM_DP_A_L0
    elif nm == "PERST_N":
        # PEX_RST# source select: R41 (fitted) = host PEX_RST# (signal pin 53, APU GPIO AND APU_PCIE0_RST#);
        # R42 (DNP, see below) = power pin 52 = EXT_SSD1_RST# from the EC in SSD-mode descriptors.
        cy = a[1]
        c1, c2 = (CX - 3.81, cy), (CX + 3.81, cy)
        place("fw16:R_H", "R41", "0R", CX, cy, hide_text=True, fp=FP["R0402"],
              note="PEX_RST# source: host PEX_RST# (default). Fit R41 OR R42, never both")
        wire(a[0], a[1], c1[0], c1[1]); wire(c2[0], c2[1], b[0], b[1])
        label(nm, a[0] + 7.62, cy)
        label("MXM_PEX_RST", c2[0] + 5.08, cy)
    else:
        wire(a[0], a[1], b[0], b[1])
        label(nm, g(187), a[1])

for nm, num in j1_left:
    pnt = p1[num]
    if nm == "GND":
        to_power(pnt, "L", "GND")
    elif nm in J1_NC:
        to_nc(pnt)
    else:
        to_label(pnt, "L", nm)

for mx, net in J3_SIDE.items():
    to_label(p3[MXM_NUM[mx]], "R", net)
for mx, net in J3_POWER.items():                 # one stub per stacked rail
    to_power(p3[next(num for num, nm in MXM_PINS.items() if nm == mx)], "R", net)
for num in j3_nc:
    to_nc(p3[num])

# ------------------------------------------------------------ support: module detect + pull-ups
SY = g(470)                 # below the bottom of J3's unused-pin column
note(40, SY - 22, "EC MODULE-DETECTION + PULL-UPS (values from forum reports - UNVERIFIED, check against Framework reference design)", 1.8, True)

def vres(ref, val, x, top, bot, notes="", y=None, lib="fw16:R_V", fp=FP["R0603"]):
    pn = place(lib, ref, val, x, SY if y is None else y, note=notes, fp=fp)[0]
    top_pt, bot_pt = pn["1"], pn["2"]
    for pt, spec in ((top_pt, top), (bot_pt, bot)):
        kind, what = spec
        d = "U" if pt is top_pt else "D"
        (to_power if kind == "pwr" else to_label)(pt, d, what) if kind == "pwr" else to_label(pt, d, what, 2.54)

vres("R1", "330k 1%", 60, ("lbl", "BOARD_ID0"), ("pwr", "GND"), "ID0: EC needs BOARD_VERSION_12 on both IDs (= dual interposer device), window 2040-2197 mV; 330k vs host 100k pull-up ~2.16 V if the pull-up rail is ~2.81 V (inferred from the EC's not-installed level)")
vres("R2", "330k 1%", 80, ("lbl", "BOARD_ID1"), ("pwr", "GND"), "ID1: see R1")
vres("R3", "4.7k", 180, ("pwr", "+3V3"), ("lbl", "EXP_SDA"), "I2C pull-up")
vres("R4", "4.7k", 195, ("pwr", "+3V3"), ("lbl", "EXP_SCL"), "I2C pull-up")
vres("R5", "10k", 215, ("pwr", "+3V3"), ("lbl", "CLKREQ_N"), "CLKREQ# pull-up")
vres("R8", "10k", 230, ("pwr", "+3V3"), ("lbl", "PROCHOT_N"), "PROCHOT# pull-up")
vres("R6", "10k", 245, ("pwr", "+3V3"), ("lbl", "PRSNT_R"), "MXM PRSNT_R pull-up")
vres("R7", "10k", 260, ("pwr", "+3V3"), ("lbl", "PRSNT_L"), "MXM PRSNT_L pull-up")
# Power pins 52/53 (JFXB1 F3/G3, EC GPU_1F3_MUX1 / GPU_1G3_MUX2) go through mainboard switch UC77
# (NX3DV221, S = SSD_GPU_SEL = descriptor GPU_PCIE_MUX_SEL). In GPU mode (S low), per the FW16 7040
# interface schematic p.3:
#   pin 52 = GC6_FB_EN3V3 (mainboard output, NVIDIA GC6 framebuffer enable) -> left unconnected
#   pin 53 = FBVDD_PWRGD (mainboard input; 1M pull-down there). Mainboard UC78 ANDs it with DGPU_PWROK
#            (power pin 73) into ALL_GPWRGD to the APU, so it must go high: tie it to PWR_GOOD via R13.
vres("R14", "100k DNP", 305, ("lbl", "DP_HPD"), ("pwr", "GND"), "DNP: not needed - MXM 3.1 Table 3.7: the module carries the 100k DP_A_HPD pull-down; system-side protection only")
vres("R13", "0R", 290, ("lbl", "PWR_GOOD"), ("lbl", "FBVDD_PWRGD"), "PWR_GOOD -> power pin 53 = FBVDD_PWRGD in GPU mode. FW16 mainboard ANDs it with DGPU_PWROK into ALL_GPWRGD (7040 interface schematic p.3, UC77/UC78); left low, ALL_GPWRGD never asserts")
# MXM 3.1 Table 3.6 / 3.11 system-board requirements
vres("R36", "7.15k 1%", 320, ("lbl", "PEX_STD_SW"), ("pwr", "GND"), "PEX_STD_SW# pull-down: MXM 3.1 Table 3.30 requires one for 8 GT/s systems; NC = short channel, 147k = medium, 7.15k / 0R = long. FW16 channel loss unknown: start at 7.15k")
vres("R37", "10k", 335, ("pwr", "+3V3"), ("lbl", "PWR_GOOD"), "PWR_GOOD pull-up: MXM 3.1 Table 3.11 requires 10k on the system board")
vres("R38", "10k", 350, ("pwr", "+3V3"), ("lbl", "THRM_INT_N"), "TH_ALERT# pull-up: MXM 3.1 Table 3.11 requires one on the system board")

# PWR_LEVEL (MXM 3.1 sec 3.4.14): high/open = full power, low = module cuts power >=20% within 50 ms.
# GPIO2_EC follows extpower_is_present() when the EEPROM descriptor sets gpio2 = GPIO_FUNC_ACDC (as in
# Framework's r23m descriptor), so on battery the card drops to its reduced power level. The card's own
# 100k pull-up provides the high level; U2 only ever pulls low.
PLX, PLY = 385, SY + 55
note(PLX - 45, PLY - 22, "PWR_LEVEL: battery -> reduced card power (GPIO2_EC = AC present)", 1.5, True)
pu2 = place("fw16:74LVC1G07", "U2", "74LVC1G07", PLX, PLY, ref_at=(5.08, -6.35), val_at=(5.08, -8.89), fp=FP["SOT23_5"],
            note="TI 74LVC1G07DBVR open-drain buffer: GPIO2_EC low (battery) -> MXM PWR_LEVEL low (reduced power). Leave U2 unfitted for always-full power. Needs descriptor gpio2 = GPIO_FUNC_ACDC / OUTPUT_LOW / POWER_S3")[0]
to_nc(pu2["1"]); to_label(pu2["2"], "L", "GPU_GPIO0"); to_power(pu2["3"], "D", "GND")
to_label(pu2["4"], "R", "MXM_PWR_LEVEL"); to_power(pu2["5"], "U", "+3V3")
vres("R39", "100k", PLX - 40, ("lbl", "GPU_GPIO0"), ("pwr", "GND"), "GPIO2_EC pull-down: if the EC leaves the pin as an input (descriptor not changed), the card runs at reduced power rather than floating", y=PLY)
vres("C44", "100nF", PLX + 25, ("pwr", "+3V3"), ("pwr", "GND"), "U2 VCC bypass", y=PLY, lib="fw16:C_V", fp=FP["C0402"])

U3X = 135
pu3 = place("fw16:EEPROM_24xx32", "U3", "BR24G32FVT-3GE2", U3X, SY, ref_at=(-7.62, -12.7), val_at=(-7.62, -10.16),
            fp=FP["TSSOP8"],
            note="Module EEPROM, 32 Kbit: EC reads 0x50 with 16-bit offsets. A0-A2=GND -> 0x50. WP=GND so the EC can program it. Contents: ExpansionBayConfigurationGenerator PCIE_THERMAL_3RDPARTY with PCIE_MUX_SEL low (keep DP_A AUX) and gpio2 = GPIO_FUNC_ACDC (drives PWR_LEVEL via U2)")[0]
note(40, SY + 20, "EEPROM: blank = EC defaults to dual-SSD (x4x2) and never enables VSYS. Program PCIE_THERMAL_3RDPARTY (PCIE_8X1, VSYS_EN, FAN_EN, 3V_5V_EN, F75303 @0x4D),", 1.5)
note(40, SY + 24, "but set GPU_PCIE_MUX_SEL LOW so DP_A AUX is not rerouted to SSD2 CLK. Note: EC sets GPU_PRESENT (eDP mux path) only for vendor GPU_AMD_R23M.", 1.5)
for nm_num in ("1", "2", "3", "4"):
    to_power(pu3[nm_num], "L", "GND", 5.08)
to_power(pu3["7"], "R", "GND", 5.08)
to_power(pu3["8"], "R", "+3V3", 5.08)
to_label(pu3["6"], "R", "EXP_SCL")
to_label(pu3["5"], "R", "EXP_SDA")

# ------------------------------------------------------------ support: power
PY = g(550)
note(40, PY - 30, "POWER: VSYS -> TVS D1 -> eFuse U1 (TPS25982, ~9.9 A limit) -> PWR_SRC to the MXM card; +5V / +3V3 from host 5V_ALW (2.5A max) / 3V3_ALW (2.0A max)", 1.8, True)

# J2 is 37 rows tall, so it sits in the empty area right of J3 instead of in the power row
J2X, J2Y = g(480), g(80)
note(J2X - 40.64, J2Y - 14, "J2 POWER INTERPOSER (pinout: FrameworkComputer/ExpansionBay)", 1.8, True)
pj2 = place("fw16:J2_FW16_ExpBay_Power", "J2", "FW16_ExpBay_Power", J2X, J2Y,
            ref_at=(-35.56, -10.16), val_at=(-35.56, -7.62), fp=FP["PWR"],
            note="Framework Expansion Bay power interposer - pinout from FrameworkComputer/ExpansionBay Electrical/README.md; place at the same XY as J1")[0]
J2_POWER = {"VSYS_GPU": "VSYS", "GND": "GND", "5V_ALW": "+5V", "3V3_ALW": "+3V3"}
J2_LABEL = {"ID0": "BOARD_ID0", "PWR_EN": "PWR_EN", "PWR_GOOD": "PWR_GOOD",
            "I2C_CLK_ALW": "EXP_SCL", "I2C_DAT_ALW": "EXP_SDA",      # EEPROM bus, as on the community board
            "EXT_SSD2_RST#": "FBVDD_PWRGD",   # pin 53 in GPU mode
            "EXT_SSD1_RST#": "EB_PIN52",      # GC6_FB_EN3V3 in GPU mode, EXT_SSD1_RST# in SSD mode; only R42 (DNP)
            "12V_FAN": "12V_FAN", "Fan0_PWM": "FAN0_PWM", "Fan1_PWM": "FAN1_PWM",
            "Fan0_SPEED": "FAN0_SPEED", "Fan1_SPEED": "FAN1_SPEED"}
for p, nm in J2_PINS.items():
    d = "R" if p <= 37 else "L"
    if nm in J2_POWER:
        to_power(pj2[str(p)], d, J2_POWER[nm], 5.08)
    elif nm in J2_LABEL:
        to_label(pj2[str(p)], d, J2_LABEL[nm])
    else:
        to_nc(pj2[str(p)])

pc1 = place("fw16:C_V", "C1", "EEH-ZA1V101P", 170, PY, fp=FP["CP8"],
            note="VSYS bulk: Panasonic EEH-ZA1V101P 100 uF 35 V hybrid polymer, 27 mOhm, ~2.3 A ripple (distributor data); 8x10.2 mm (Panasonic datasheet) on CP_Elec_8x10.5 pads; ~10.2 mm tall: place outside the card outline")[0]
to_power(pc1["1"], "U", "VSYS"); to_power(pc1["2"], "D", "GND"); to_flag(pc1["1"], "L"); to_flag(pc1["2"], "L")
pd1 = place("fw16:TVS_V", "D1", "SMBJ20A", 195, PY, fp=FP["SMB"],
            note="Littelfuse SMBJ20A: 20 V standoff (= max VSYS), 22.2-24.5 V breakdown, 32.4 V clamp @ 18.6 A, 600 W")[0]
to_power(pd1["1"], "U", "VSYS"); to_power(pd1["2"], "D", "GND")

# eFuse U1 (replaces the old R11 0R placeholder). Values from TPS25982 datasheet SLVSEI3D equations.
EFX = 240
pu1 = place("fw16:TPS25982", "U1", "TPS25982", EFX, PY, ref_at=(-10.16, -7.62), val_at=(-10.16, -10.16), fp=FP["RGE"],
            note="TI TPS25982 eFuse (2.7-24 V, 15 A; abs max IN 30 V). RGE0024M, pad 25 = IN, pad 26 = GND (TI 4223975/B land pattern). TPS25983 is pin-compatible (26 V, 20 A)")[0]
ef = {nm: pu1[nums[0]] for nm, nums, _ in EF_LEFT + EF_RIGHT}
to_power(ef["IN"], "L", "VSYS"); to_label(ef["EN/UVLO"], "L", "EF_EN"); to_power(ef["GND"], "L", "GND")
to_power(ef["OUT"], "R", "PWR_SRC")
for nm, lbl in (("PG", "EFUSE_PG"), ("ILIM", "EF_ILIM"), ("IMON", "EF_IMON"), ("dVdT", "EF_DVDT"),
                ("RETRY_DLY", "EF_RETRY")):
    to_label(ef[nm], "R", lbl)
to_nc(ef["ITIMER"])                              # open = trip with minimum delay (Table 7-1)
to_nc(ef["NRETRY"])                              # open = 4 auto-retries, then latch off (Table 7-5)
to_power(ef["LDSTRT"], "R", "GND")               # "Tie LDSTRT to ground if not needed" (8.2.2.6)
EY = PY + 70
vres("R15", "442k 1%", 200, ("pwr", "VSYS"), ("lbl", "EF_EN"), "UVLO divider: V = 1.2 V x (R15+R16)/R16 = 6.5 V (MXM PWR_SRC min); EN = 3.7 V at 20 V (abs max 7 V)", y=EY)
vres("R16", "100k 1%", 215, ("lbl", "EF_EN"), ("pwr", "GND"), "UVLO divider bottom (see R15)", y=EY)
vres("R17", "147R 1%", 230, ("lbl", "EF_ILIM"), ("pwr", "GND"), "ILIM: R = 1460/I - 0.11 (datasheet Eq 16) -> 147R = 9.9 A, under the host's 14 x 0.75 A = 10.5 A", y=EY)
vres("R18", "1.33k 1%", 245, ("lbl", "EF_IMON"), ("pwr", "GND"), "IMON: R = 3.3 V / (10 A x 246 uA/A) (Eq 18; G_IMON 246 uA/A implied by Eq 18 - confirm in 6.5); 3.27 V at 10 A; test point", y=EY)
vres("R19", "100k", 260, ("lbl", "PWR_EN"), ("pwr", "GND"), "Host PWR_EN pull-down: keeps U6 input A low (card off) while the APU GPIO is unconfigured", y=EY)
vres("C42", "4.7nF", 275, ("lbl", "EF_DVDT"), ("pwr", "GND"), "dVdT: C(pF) = 4600 / SR(V/ms) (Eq 3) -> ~1 V/ms, 20 ms ramp; inrush ~1 A per 1 mF of card input capacitance", y=EY, lib="fw16:C_V", fp=FP["C0603"])
vres("C43", "2.2nF", 290, ("lbl", "EF_RETRY"), ("pwr", "GND"), "RETRY_DLY: C(pF) = t(us)/46.83 - 4 (Eq 31) -> ~100 ms between retries", y=EY, lib="fw16:C_V", fp=FP["C0603"])

# Card PWR_EN = host PWR_EN AND eFuse PG, translated to 3.3 V. The FW16 drives PWR_EN from a 1.8 V APU GPIO
# ("do not pull high to 3.3V", Framework forum t/74018 post 233); MXM PWR_EN gets a 3.3 V push-pull level.
# MXM 3.1 sec 3.4.1: PWR_EN only once all rails are in tolerance, so PWR_SRC (eFuse PG) gates it.
U6X = 345
note(U6X - 40, EY - 24, "PWR_EN: 1.8 V host GPIO AND eFuse PG -> 3.3 V card PWR_EN", 1.5, True)
pu6 = place("fw16:SN74LV1T08", "U6", "SN74LV1T08DBVR", U6X, EY, ref_at=(5.08, -6.35), val_at=(5.08, -8.89), fp=FP["SOT23_5"],
            note="TI SN74LV1T08DBVR single-supply AND / level shifter at VCC 3.3 V: VIH max 1.37 V, so the 1.8 V host PWR_EN reads high; inputs tolerate up to 7 V abs max with VCC off. Y = PWR_EN AND eFuse PG -> MXM PWR_EN (3.3 V push-pull)")[0]
to_label(pu6["1"], "L", "PWR_EN"); to_label(pu6["2"], "L", "EFUSE_PG"); to_power(pu6["3"], "D", "GND")
to_label(pu6["4"], "R", "MXM_PWR_EN"); to_power(pu6["5"], "U", "+3V3")
vres("R40", "10k", U6X - 40, ("pwr", "+3V3"), ("lbl", "EFUSE_PG"), "eFuse PG pull-up (PG is open drain, high once PWR_SRC is in range)", y=EY)
vres("C48", "100nF", U6X + 35, ("pwr", "+3V3"), ("pwr", "GND"), "U6 VCC bypass", y=EY, lib="fw16:C_V", fp=FP["C0402"])
vres("R42", "0R DNP", U6X + 55, ("lbl", "EB_PIN52"), ("lbl", "MXM_PEX_RST"), "DNP: alternative PEX_RST# source = power pin 52 (EXT_SSD1_RST# from the EC in SSD-mode descriptors). For the x8 case where the BIOS drops PEX_RST# after POST (forum t/74018 posts 201-203). Remove R41 when fitting; SSD mode reroutes DP_A AUX (route A only)", y=EY)

pc4 = place("fw16:C_V", "C4", "EEH-ZA1V101P", 300, PY, fp=FP["CP8"], note="PWR_SRC bulk near J3: Panasonic EEH-ZA1V101P 100 uF 35 V hybrid polymer")[0]
to_power(pc4["1"], "U", "PWR_SRC"); to_power(pc4["2"], "D", "GND"); to_flag(pc4["1"], "L")

# +5V / +3V3 are the host ALW rails from J2 (passive pins), so they need their own PWR_FLAGs
pc2 = place("fw16:C_V", "C2", "47uF 10V", 345, PY, fp=FP["C1206"], note="+5V bulk near J3 (host 5V_ALW)")[0]
to_power(pc2["1"], "U", "+5V"); to_power(pc2["2"], "D", "GND"); to_flag(pc2["1"], "L")
pc3 = place("fw16:C_V", "C3", "22uF 10V", 390, PY, fp=FP["C1206"], note="+3V3 bulk near J3 (host 3V3_ALW)")[0]
to_power(pc3["1"], "U", "+3V3"); to_power(pc3["2"], "D", "GND"); to_flag(pc3["1"], "L")

# ------------------------------------------------------------ fan headers (graphics bay)
note(560, 66, "FAN HEADERS - host EC drives 12V_FAN / PWM (5 V) and reads SPEED (5 V OD). Pinout per FW ref PCB drawing.", 1.8, True)
for i, (ref, k) in enumerate((("J4", "0"), ("J5", "1"))):
    pf = place("fw16:FAN_4P", ref, "AFC58-S04FIA-R1", 570, 80 + i * 35, ref_at=(-7.62, -2.54), val_at=(-7.62, -5.08),
               fp=FP["AFC"], note=f"Fan{k}: Zhejiang Hefeng AFC58-S04FIA-R1 (FW ref design J200/J201), 0.5 mm FPC lower contact; 1 +12V, 2 SPEED, 3 PWM, 4 GND (FW_EXPANSION_BAY_PCB sheet 2)")[0]
    to_label(pf["1"], "R", "12V_FAN"); to_power(pf["4"], "R", "GND")
    to_label(pf["2"], "R", f"FAN{k}_SPEED"); to_label(pf["3"], "R", f"FAN{k}_PWM")

# ------------------------------------------------------------ fan-control temperature sensor
TSX, TSY = 470, SY
note(420, TSY - 22, "FAN-CONTROL TEMP SENSOR - F75303 @0x4D on the ALW I2C bus (Framework PCIE_THERMAL_3RDPARTY descriptor). Pins per LCFC NM-D471 sheet 77.", 1.8, True)
pu4 = place("fw16:F75303", "U4", "F75303", TSX, TSY, ref_at=(-10.16, -7.62), val_at=(-10.16, -10.16), fp=FP["MSOP10"],
            note="Fintek F75303M 10-MSOP 3x3. Pinout from LCFC NM-D471 schematic sheet 77 (US301). 0x4D (8-bit 0x9A): FW16 mainboard UTH1, the same F75303M_MSOP10, is marked 1001_101x (7040 interface schematic p.9). ALERT#/THERM# open-drain, unused here (ref design pulls them up 4.7k/10k to 3V3). Descriptor maps local=ambient, remote1=GPU VR, remote2=VRAM")[0]
u4 = {nm: pu4[n] for nm, n in F75_L + F75_R}
to_power(u4["VDD"], "L", "+3V3"); to_power(u4["GND"], "R", "GND")
for nm, lbl in (("D1+", "TS_D1P"), ("D1-", "TS_D1N"), ("D2+", "TS_D2P"), ("D2-", "TS_D2N")):
    to_label(u4[nm], "L", lbl)
to_label(u4["SCL"], "R", "EXP_SCL"); to_label(u4["SDA"], "R", "EXP_SDA")
to_nc(u4["ALERT#"]); to_nc(u4["THERM#"])
vres("C45", "100nF", 445, ("pwr", "+3V3"), ("pwr", "GND"), "U4 VDD bypass", y=TSY + 40, lib="fw16:C_V", fp=FP["C0402"])
for i, (ref, ch, where) in enumerate((("Q1", "1", "GPU VRM / core area"), ("Q2", "2", "VRAM area"))):
    pq = place("fw16:Q_PNP", ref, "MMBT3906", 545 + i * 40, TSY, ref_at=(5.08, -1.27), val_at=(5.08, 1.27), fp=FP["SOT23"],
               note=f"F75303 remote diode {ch}: place at the {where} of the MXM card (thermally coupled)")[0]
    to_label(pq["2"], "U", f"TS_D{ch}P", 2.54); to_label(pq["1"], "L", f"TS_D{ch}N"); to_label(pq["3"], "D", f"TS_D{ch}N", 2.54)
    vres(f"C{46 + i}", "2.2nF", 560 + i * 40, ("lbl", f"TS_D{ch}P"), ("lbl", f"TS_D{ch}N"),
         f"Remote diode {ch} filter cap across D+/D-: 2200pF X7R as CS302/CS303 in LCFC NM-D471 sheet 77", y=TSY + 40, lib="fw16:C_V", fp=FP["C0402"])

# ------------------------------------------------------------ notes
nx, ny = 10, 12
note(nx, ny, "FW16 EXPANSION BAY -> MXM 3.x ADAPTER  |  schematic v4 DRAFT  |  generated + ERC-checked with KiCad 10 (kicad-cli)", 2.5, True)
note(nx, ny + 6, "NOT A MANUFACTURABLE DESIGN. No PCB layout. Every value/pin/footprint marked TBD is an unresolved placeholder (see BOM CSV).", 1.5)
note(nx, ny + 10, "J1/J2 pins: github.com/FrameworkComputer/ExpansionBay Electrical/README.md ; J3: MXM 3.1 connector tables (ADLINK MXM-AXe, Advantech SKY-MXM-RTX3000).", 1.5)
note(nx, ny + 14, "Lanes go straight through by name: host PEX_TX -> MXM PEX_TX (MXM names are system-relative). Confirm against the MXM spec before ordering.", 1.5)
note(nx, ny + 18, "Series parts: host->card PCIe R20-R35 = 0R; card->host PCIe C10-C25 = 220nF; DP_A lanes+AUX C26-C35 = 100nF DC blocking; HPD direct (R14 pull-down DNP).", 1.5)
note(nx, ny + 22, "OPEN: TH_PWM unconnected. J3 = S55B on a 1.2 mm adapter; needs the flat 3D-printed bay cover (15.3 mm inside). Pins 52/53 and the F75303 address per FW16 7040 interface schematic. Checked against MXM 3.1 r1.0.", 1.5)

# ------------------------------------------------------------ write
out = f"""(kicad_sch (version 20230121) (generator fw16_mxm_gen)
  (uuid "{ROOT}")
  (paper "A0")
  (title_block
    (title "Framework 16 Expansion Bay to MXM 3.x Adapter")
    (date "2026-10-30")
    (rev "v4-DRAFT")
    (comment 1 "ERC + netlist checked with KiCad 10 kicad-cli. Not validated electrically. TBD = unresolved.")
  )
  (lib_symbols
    {chr(10).join(lib_texts.values())}
  )
  {chr(10).join(wires)}
  {chr(10).join(ncs)}
  {chr(10).join(labels)}
  {chr(10).join(placed)}
  {chr(10).join(texts)}
  (sheet_instances (path "/" (page "1")))
)
"""
dest = sys.argv[1] if len(sys.argv) > 1 else "fw16_mxm_adapter.kicad_sch"
open(dest, "w").write(out)
with open(dest.replace(".kicad_sch", "_bom_draft.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["Reference", "Value", "Footprint", "Notes"])
    for r in bom: w.writerow(r)
print("wrote", dest, len(out), "bytes;", len(bom), "components")
