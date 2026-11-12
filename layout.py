"""Layout decisions shared by generate_pcb.py (the adapter board) and generate_frame.py (the printed
bottom frame). Pure Python, no KiCad or CAD imports, so both tools can use it.

Coordinates: u across the bay, v toward the laptop edge, origin midway between the two interposer
screws, heights h above the adapter board's underside (RESEARCH_TODO item 7b).
"""
import csv, math, os

HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ placement decisions (all in u, v)
BOARD_THICKNESS = 1.2          # Framework's board and inserts (RESEARCH_TODO item 6)
COPPER_LAYERS = 6              # placeholder until a JLCPCB impedance stackup is chosen
# Stiffener over the interposers, module side: u -21.2..21.2, v -5.25..0.3, 4.45 mm above the board top.
STIFFENER = (-21.2, -5.25, 21.2, 0.3)
CARD_GAP = 2.7                 # S55B, PCB to card underside
# MXM card 105 x 82: front edge kept behind the stiffener with 0.5 mm clearance.
CARD_V_FRONT = STIFFENER[1] - 0.5
# J3's housing reaches 4.7 mm behind the card's finger edge (Foxconn side view: 8.90 deep, 4.20 on the
# card side of the pegs). Finger edge at u -54.3: housing back at -59.0, card to u 50.7. The printed frame
# moves the cover-screw bosses outboard of both (FRAME_PLAN.md).
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
# Printed bottom frame (FRAME_PLAN.md; generate_frame.py builds it). Framework's frame lengthened by
# REAR_STRETCH just in front of its rear wall, over the full width: the whole rear wall moves back
# (inner face v -89.15 -> -92.85, the laptop's rear face -90.75 -> -94.45). Inner side walls at board
# level stay at u -73.29 / +58.64.
REAR_STRETCH = 3.7
REAR_STRETCH_AT = -88.0        # plane the frame is split and lengthened at (only floor, side walls, ribs)
REAR_INNER = -89.15 - REAR_STRETCH
WALLS = [(-73.29, 5.2), (-73.29, REAR_INNER), (58.64, REAR_INNER), (58.64, 5.2)]
# Cover-screw bosses moved outboard (stock: (-61.8, -65.6) and (50.0, -65.6), which met the socket
# housing and the card); M2 heat-set insert in a dia 6.0 boss up to 5.0 mm above the board's underside.
COVER_BOSSES = [(-66.0, -65.6), (55.0, -65.6)]
KEEPOUTS = [
    ((-73.29, 0.0, -46.08, 5.2), "FAN FPC / CABLE"),
    ((36.03, 0.0, 58.64, 5.2), "FAN FPC / CABLE"),
]

# ------------------------------------------------------------------ outline
def outline_edges():
    rows = []
    with open(os.path.join(HERE, "reference", "fw_7700s_board_outline.csv")) as fh:
        for r in csv.reader(l for l in fh if not l.startswith("#")):
            rows.append(r)
    # Replace the stock left side (from the rear edge at u -13.125 round to the front notch at u -51.025)
    # with an extension that takes the MXM socket and its ear pads (v -92.25..-1.25): out to u -59.3,
    # back to v -92.55 (the lengthened frame's rear wall is at -92.85), and forward to v -0.5 (the stock frame's front-left
    # ledge, which the printed frame leaves out). 0.3 mm copper to edge at both ends.
    i0 = next(i for i, r in enumerate(rows) if r[0] == "line" and float(r[1]) == -13.125 and float(r[2]) == -87.25)
    i1 = next(i for i, r in enumerate(rows) if r[0] == "line" and float(r[1]) == -51.025 and float(r[4]) == 4.75)
    ext = [["line", -13.125, -87.25, -48.0, -87.25], ["line", -48.0, -87.25, -48.0, -92.55],
           ["line", -48.0, -92.55, -58.3, -92.55], ["arc", -58.3, -92.55, -59.3, -91.55, -58.3, -91.55, 1.0],
           ["line", -59.3, -91.55, -59.3, -1.5], ["arc", -59.3, -1.5, -58.3, -0.5, -58.3, -1.5, 1.0],
           ["line", -58.3, -0.5, -51.025, -0.5], ["line", -51.025, -0.5, -51.025, 4.75]]
    return rows[:i0] + ext + rows[i1 + 1:]

def arc_mid(a, b, c, prev_end, prev_dir):
    """Midpoint of the outline arc a -> b about c. The CSV gives no direction, so take the short arc;
    for a half circle (the U-notches round the shell posts and rear pins) continue the direction of the
    edge that leads into it, so the notch cuts into the board."""
    rad = math.hypot(a[0] - c[0], a[1] - c[1])
    a0 = math.atan2(a[1] - c[1], a[0] - c[0]); a1 = math.atan2(b[1] - c[1], b[0] - c[0])
    d = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    if abs(abs(d) - math.pi) < 1e-3:
        assert prev_end and math.dist(prev_end, a) < 1e-3, "half-circle arc must follow its lead-in edge"
        n = math.hypot(*prev_dir)
        return (c[0] + rad * prev_dir[0] / n, c[1] + rad * prev_dir[1] / n)
    return (c[0] + rad * math.cos(a0 + d / 2), c[1] + rad * math.sin(a0 + d / 2))

def outline_shapes():
    """Outline as ("line", a, b) / ("arc", a, mid, b) in u, v."""
    out, prev_end, prev_dir = [], None, None
    for r in outline_edges():
        a = (float(r[1]), float(r[2])); b = (float(r[3]), float(r[4]))
        if r[0] == "line":
            out.append(("line", a, b)); prev_dir = (b[0] - a[0], b[1] - a[1])
        else:
            m = arc_mid(a, b, (float(r[5]), float(r[6])), prev_end, prev_dir)
            out.append(("arc", a, m, b)); prev_dir = (b[0] - m[0], b[1] - m[1])
        prev_end = b
    return out

def outline_polygon(seg_deg=10.0):
    """The outline as one closed list of (u, v) points, arcs split into short chords."""
    pts = []
    for sh in outline_shapes():
        if sh[0] == "line":
            seg = [sh[1], sh[2]]
        else:
            a, m, b = sh[1:]
            # circle through a, m, b
            ax, ay = a; bx, by = m; cx, cy = b
            d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
            ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / d
            uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / d
            r = math.hypot(ax - ux, ay - uy)
            t0, tm, t1 = (math.atan2(p[1] - uy, p[0] - ux) for p in (a, m, b))
            sweep = (t1 - t0) % (2 * math.pi)
            if (tm - t0) % (2 * math.pi) > sweep: sweep -= 2 * math.pi      # go the way through m
            n = max(2, int(abs(math.degrees(sweep)) / seg_deg) + 1)
            seg = [(ux + r * math.cos(t0 + sweep * k / n), uy + r * math.sin(t0 + sweep * k / n)) for k in range(n + 1)]
        if pts:
            assert math.dist(pts[-1], seg[0]) < 1e-3, (pts[-1], seg[0])
            seg = seg[1:]
        pts += seg
    assert math.dist(pts[0], pts[-1]) < 1e-3
    return pts[:-1]
