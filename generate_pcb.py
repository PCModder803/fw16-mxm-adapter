#!/usr/bin/env python3
"""Generate fw16_mxm_adapter.kicad_pcb: a MECHANICAL PLACEMENT DRAFT (not for fab).

Run with KiCad's Python (it needs the pcbnew module):
    "C:/Program Files/KiCad/10.0/bin/python.exe" generate_pcb.py

What it does:
  - board outline from reference/fw_7700s_board_outline.csv (Framework's RX 7700S module board, read from
    FW_GRAPHICS_MODULE_REF_00-1.stp), extended on the left and rear for the MXM socket;
  - J1/J2 (interposers), J3 (MXM socket), J4/J5 (fan FPC connectors) and the mounting features placed;
  - every other part from the schematic netlist placed in a staging grid beside the board, with nets,
    so the ratsnest shows;
  - reference drawings on User layers: MXM card outline, interposer-stiffener keep-out, shell walls.
No tracks. Coordinates: u across the bay, v toward the laptop edge, origin midway between the two
interposer screws (RESEARCH_TODO item 7b). KiCad X = X0 + u, Y = Y0 + v (top view, laptop edge at the
bottom of the screen).
"""
import csv, math, os, subprocess, sys, tempfile
import xml.etree.ElementTree as ET
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
KICAD = os.path.dirname(sys.executable)                      # .../KiCad/10.0/bin
STOCK = os.path.join(os.path.dirname(KICAD), "share", "kicad", "footprints")
PROJ_LIB = os.path.join(HERE, "fw16_mxm.pretty")
OUT = os.path.join(HERE, "fw16_mxm_adapter.kicad_pcb")
X0, Y0 = 150.0, 110.0
mm = pcbnew.FromMM

def P(u, v): return pcbnew.VECTOR2I(mm(X0 + u), mm(Y0 + v))

# ------------------------------------------------------------------ placement decisions (all in u, v)
BOARD_THICKNESS = 1.2          # Framework's board and inserts (RESEARCH_TODO item 6)
COPPER_LAYERS = 6              # placeholder until a JLCPCB impedance stackup is chosen
# Stiffener over the interposers, module side: u -21.2..21.2, v -5.25..0.3, 4.45 mm above the board top.
STIFFENER = (-21.2, -5.25, 21.2, 0.3)
CARD_GAP = 2.7                 # S55B, PCB to card underside
# MXM card 105 x 82: front edge kept behind the stiffener with 0.5 mm clearance.
CARD_V_FRONT = STIFFENER[1] - 0.5
# J3's housing reaches 4.7 mm behind the card's finger edge (Foxconn side view: 8.90 deep, 4.20 on the
# card side of the pegs). The left cover-screw boss reaches u -59.43, so the finger edge goes at -54.3
# (housing back at -59.0). The card then ends at u 50.7, past the right boss (from u 47.62): a known
# conflict, drawn below.
CARD_U_LEFT = -54.3
CARD = (CARD_U_LEFT, CARD_V_FRONT - 82.0, CARD_U_LEFT + 105.0, CARD_V_FRONT)
# J3: socket axis along v. Foxconn's drawing: the card is centred between the pegs (82 mm apart), the
# ear pads are centred 3 mm past each peg (copper 91.0 mm overall, body 88.9 mm), and the card
# hold-downs sit 66 mm toward the card.
# The card's finger edge is taken on the peg line (consistent with the 66 mm hold-downs; check against
# the MXM 3.1 mechanical drawing). Footprint +y points toward the card.
J3_U, J3_V = CARD_U_LEFT, (CARD[1] + CARD[3]) / 2
# Fan connectors near where the 7700S board has them (model SP010036Q00_AFC58 at v 1.45), moved 1 mm
# back so the nail pads clear the board edge; orientation not yet checked against the model.
J4_UV, J5_UV = (-46.3, 0.45), (37.22, 0.45)
# Mounting features from the 7700S board: screw into a shell boss; rear insert (same ES00000NY00).
MOUNT_SCREW = (44.675, -6.15)
REAR_INSERT = (-17.325, -83.65)
# Shell inner walls at board level (model): sides u -73.29 / +58.64, rear v -89.15.
WALLS = (-73.29, -89.15, 58.64, 5.2)
# Shell features in the card/socket height band (Framework model, vertex extents, RESEARCH_TODO 7b):
KEEPOUTS = [
    ((-73.29, -70.0, -59.43, -60.0), "LEFT COVER-SCREW BOSS: ledge 1.4-5.0 mm, screw to 7.0 mm"),
    ((47.62, -70.0, 58.64, -60.0), "RIGHT COVER-SCREW BOSS: ledge 1.4-5.0 mm, screw to 7.0 mm"),
    ((-62.0, -3.3, -51.0, 0.0), "FRAME LEDGE AT BOARD LEVEL (why the stock board is notched here)"),
    ((-73.29, 0.0, -46.08, 5.2), "FAN FPC / CABLE"),
    ((36.03, 0.0, 58.64, 5.2), "FAN FPC / CABLE"),
]

# ------------------------------------------------------------------ outline
def outline_edges():
    rows = []
    with open(os.path.join(HERE, "reference", "fw_7700s_board_outline.csv")) as fh:
        for r in csv.reader(l for l in fh if not l.startswith("#")):
            rows.append(r)
    # Replace the stock left side (from the rear edge at u -13.125 round to (-51.025, -2.25)) with an
    # extension that takes the MXM socket: out to u -59.3 (just inside the left boss) and back to v -88.65
    # (0.5 mm inside the rear wall).
    i0 = next(i for i, r in enumerate(rows) if r[0] == "line" and float(r[1]) == -13.125 and float(r[2]) == -87.25)
    i1 = next(i for i, r in enumerate(rows) if r[0] == "arc" and float(r[3]) == -51.025 and float(r[4]) == -2.25)
    ext = [["line", -13.125, -87.25, -48.0, -87.25], ["line", -48.0, -87.25, -48.0, -88.65],
           ["line", -48.0, -88.65, -58.3, -88.65], ["arc", -58.3, -88.65, -59.3, -87.65, -58.3, -87.65, 1.0],
           ["line", -59.3, -87.65, -59.3, -3.25], ["arc", -59.3, -3.25, -58.3, -2.25, -58.3, -3.25, 1.0],
           ["line", -58.3, -2.25, -51.025, -2.25]]
    return rows[:i0] + ext + rows[i1 + 1:]

def add_outline(board):
    for r in outline_edges():
        s = pcbnew.PCB_SHAPE(board)
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1))
        a = (float(r[1]), float(r[2])); b = (float(r[3]), float(r[4]))
        if r[0] == "line":
            s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(P(*a)); s.SetEnd(P(*b))
        else:
            c = (float(r[5]), float(r[6]))
            # midpoint of the short arc between a and b
            a0 = math.atan2(a[1] - c[1], a[0] - c[0]); a1 = math.atan2(b[1] - c[1], b[0] - c[0])
            d = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
            rad = math.hypot(a[0] - c[0], a[1] - c[1])
            m = (c[0] + rad * math.cos(a0 + d / 2), c[1] + rad * math.sin(a0 + d / 2))
            s.SetShape(pcbnew.SHAPE_T_ARC); s.SetArcGeometry(P(*a), P(*m), P(*b))
        board.Add(s)

def rect(board, layer, box, width=0.15):
    u0, v0, u1, v1 = box
    for a, b in (((u0, v0), (u1, v0)), ((u1, v0), (u1, v1)), ((u1, v1), (u0, v1)), ((u0, v1), (u0, v0))):
        s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(layer)
        s.SetWidth(mm(width)); s.SetStart(P(*a)); s.SetEnd(P(*b)); board.Add(s)

def text(board, layer, u, v, msg, size=1.2):
    t = pcbnew.PCB_TEXT(board); t.SetText(msg); t.SetLayer(layer); t.SetPosition(P(u, v))
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(size * 0.15))
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT); board.Add(t)

# ------------------------------------------------------------------ netlist from the schematic
def netlist():
    tmp = os.path.join(tempfile.mkdtemp(), "net.xml")
    subprocess.run([os.path.join(KICAD, "kicad-cli"), "sch", "export", "netlist", "--format", "kicadxml",
                    "--output", tmp, os.path.join(HERE, "fw16_mxm_adapter.kicad_sch")], check=True,
                   stdout=subprocess.DEVNULL)
    root = ET.parse(tmp).getroot()
    comps = {c.get("ref"): (c.findtext("value"), c.findtext("footprint")) for c in root.iter("comp")}
    pinnet = {}
    for n in root.iter("net"):
        for node in n.iter("node"):
            pinnet[(node.get("ref"), node.get("pin"))] = n.get("name")
    return comps, pinnet

def load_fp(fpid):
    lib, name = fpid.split(":")
    path = PROJ_LIB if lib == "fw16_mxm" else os.path.join(STOCK, lib + ".pretty")
    fp = pcbnew.FootprintLoad(path, name)
    if fp is None: raise SystemExit(f"footprint not found: {fpid}")
    fp.SetFPIDAsString(fpid)
    return fp

def main():
    board = pcbnew.BOARD()
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(mm(BOARD_THICKNESS))
    board.SetCopperLayerCount(COPPER_LAYERS)
    tb = board.GetTitleBlock()
    tb.SetTitle("FW16 Expansion Bay to MXM adapter - mechanical placement draft")
    tb.SetRevision("draft-1"); tb.SetDate("2026-11-10")
    tb.SetComment(0, "NOT FOR FAB: placement and fit study only, no routing")
    tb.SetComment(1, "Outline from Framework's RX 7700S module board (FW_GRAPHICS_MODULE_REF_00-1.stp, CC BY 4.0)")
    tb.SetComment(2, "Generated by generate_pcb.py - edit the script, not this file")

    add_outline(board)
    comps, pinnet = netlist()
    nets = {}
    for name in sorted(set(pinnet.values())):
        ni = pcbnew.NETINFO_ITEM(board, name); board.Add(ni); nets[name] = ni

    fixed = {
        "J1": (0.0, 0.0, 0), "J2": (0.0, 0.0, 0),          # same XY: the two halves of one interposer pair
        "J3": (J3_U, J3_V, 90),
        "J4": (J4_UV[0], J4_UV[1], 0), "J5": (J5_UV[0], J5_UV[1], 0),
    }
    stage_u, stage_v, col = 75.0, -85.0, 0
    for ref in sorted(comps, key=lambda r: (r.rstrip("0123456789"), int("0" + "".join(ch for ch in r if ch.isdigit())))):
        value, fpid = comps[ref]
        fp = load_fp(fpid)
        fp.SetReference(ref); fp.SetValue(value or "")
        board.Add(fp)
        if ref in fixed:
            u, v, rot = fixed[ref]
            fp.SetPosition(P(u, v)); fp.SetOrientationDegrees(rot)
        else:
            fp.SetPosition(P(stage_u + (col % 6) * 12.0, stage_v + (col // 6) * 8.0)); col += 1
        for pad in fp.Pads():
            n = pinnet.get((ref, pad.GetNumber()))
            if n: pad.SetNet(nets[n])

    # J3 direction check: the card side of the socket (footprint +y) must face +u.
    j3 = next(f for f in board.GetFootprints() if f.GetReference() == "J3")
    p1 = next(p for p in j3.Pads() if p.GetNumber() == "1")          # footprint y = +3.75 row
    p2 = next(p for p in j3.Pads() if p.GetNumber() == "2")          # footprint y = -3.50 row
    if p1.GetPosition().x < p2.GetPosition().x:
        j3.SetOrientationDegrees(270)

    # MXM card hold-downs (Foxconn drawing: dia 6.8 keepouts at footprint x +-37.5, y +66): M2 standoffs,
    # card gap tall. Positions follow J3's placement.
    for i, lx in enumerate((-37.5, 37.5)):
        t = math.radians(j3.GetOrientationDegrees())      # KiCad: Y down, positive angle = CCW on screen
        qx = lx * math.cos(t) + 66.0 * math.sin(t); qy = -lx * math.sin(t) + 66.0 * math.cos(t)
        pos = pcbnew.VECTOR2I(j3.GetPosition().x + mm(qx), j3.GetPosition().y + mm(qy))
        fp = load_fp("MountingHole:MountingHole_2.2mm_M2"); fp.SetReference(f"H{3 + i}"); fp.SetValue("MXM card hold-down")
        fp.SetPosition(pos); board.Add(fp)
        c = pcbnew.PCB_SHAPE(board); c.SetShape(pcbnew.SHAPE_T_CIRCLE); c.SetLayer(pcbnew.Dwgs_User); c.SetWidth(mm(0.15))
        c.SetCenter(pos); c.SetEnd(pcbnew.VECTOR2I(pos.x + mm(3.4), pos.y)); board.Add(c)

    # mounting features
    for (u, v), fpid, ref in ((MOUNT_SCREW, "MountingHole:MountingHole_2.2mm_M2", "H1"),
                              (REAR_INSERT, "MountingHole:MountingHole_2.7mm", "H2")):
        fp = load_fp(fpid); fp.SetReference(ref); fp.SetPosition(P(u, v)); board.Add(fp)

    # reference drawings
    U1, U2, CM = pcbnew.Dwgs_User, pcbnew.Cmts_User, pcbnew.Eco1_User
    rect(board, U1, CARD, 0.2)
    text(board, U1, CARD[0] + 2, CARD[1] + 4, f"MXM CARD 105 x 82 (underside {CARD_GAP} mm above board, S55B)")
    rect(board, U1, STIFFENER, 0.2)
    text(board, U1, STIFFENER[0], STIFFENER[1] - 1.5, "INTERPOSER STIFFENER: 4.45 mm above board top - card must not overlap", 1.0)
    rect(board, U2, WALLS, 0.3)
    text(board, U2, WALLS[0] + 1, WALLS[1] + 2.5, "SHELL INNER WALLS AT BOARD LEVEL (Framework model)", 1.0)
    for box, label in KEEPOUTS:
        rect(board, U2, box, 0.3)
        text(board, U2, box[0] + 0.5, box[1] - 1.0, label, 0.8)
    text(board, CM, -66, -95, "MECHANICAL PLACEMENT DRAFT - NOT FOR FAB. Parts right of the board are unplaced (staging).", 1.5)
    text(board, CM, -66, -98, "Open issues (RESEARCH_TODO item 7b): with S55B the card is pinned behind the stiffener, so J3 overruns the rear wall;", 1.5)
    text(board, CM, -66, -101, "card + socket need ~109.7 mm across but the cover-screw bosses leave 107.05 mm. Plan: printed frame + S78B (FRAME_PLAN.md).", 1.5)

    board.Save(OUT)
    print("wrote", OUT, "footprints:", len(board.GetFootprints()))

if __name__ == "__main__":
    main()
