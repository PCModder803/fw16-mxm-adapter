#!/usr/bin/env python3
"""Generate the printed bottom frame MOCKUP (not for print yet) from Framework's graphics-module model.

It takes the stock plastic bottom frame (IFGP6_DIS_FRAME_BTM) out of FW_GRAPHICS_MODULE_REF_00-1.stp,
keeps its outside, and changes the inside for the MXM adapter (FRAME_PLAN.md). Then it checks the
result against the adapter board, the MXM socket and the card, and writes STEP and STL files.

Needs Python 3.11+ with the OpenCascade bindings (no KiCad):
    python -m venv cadenv && cadenv/Scripts/python -m pip install cadquery-ocp
    cadenv/Scripts/python generate_frame.py
and Framework's STEP at reference/FW_GRAPHICS_MODULE_REF_00-1.stp (FrameworkComputer/ExpansionBay, CC BY
4.0; not in this repo because of its size). The frame it writes is a modified version of Framework's
part and carries the same CC BY 4.0 licence, credited to Framework Computer.

Coordinates: u across the bay, v toward the laptop edge, h above the adapter board's underside
(layout.py). The output keeps the STEP's own world coordinates, so it overlays Framework's assembly.
"""
import os, sys
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_Label
from OCP.OCP.collections import Sequence_TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.TCollection import TCollection_ExtendedString
from OCP.TopLoc import TopLoc_Location
from OCP.Interface import Interface_Static
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.gp import gp_Pnt, gp_Dir, gp_Ax2, gp_Vec
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse, BRepAlgoAPI_Common
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakePrism
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
import layout as L

HERE = os.path.dirname(os.path.abspath(__file__))
STEP_IN = os.path.join(HERE, "reference", "FW_GRAPHICS_MODULE_REF_00-1.stp")
OUT_DIR = os.path.join(HERE, "mechanical")
FRAME_PART = "IFGP6_DIS_FRAME_BTM"

# bay coordinates -> the STEP's world coordinates (RESEARCH_TODO item 7b)
DX, DY, DZ = 7.325, -11.606, 70.55
def W(u, v, h): return (u + DX, h + DY, v + DZ)

# ------------------------------------------------------------------ frame dimensions (from the model)
FLOOR_TOP, FLOOR_BOTTOM = -2.7, -4.2        # plastic floor behind the aluminium plate, at the rear
REAR_WALL_TOP = 10.6                        # rear wall: inner face v -89.15, outer face -90.75
REAR_OUTER = -90.75
WALL = 1.6                                  # wall thickness used for the new pocket (stock rear wall 1.3-1.6)
STOCK_COVER_BOSSES = [(-61.8, -65.6, 3.0), (50.0, -65.6, 3.3)]   # u, v, cut radius (boss r 2.4 + its web)
BOSS_R, BOSS_TOP, INSERT_R, INSERT_DEPTH = 3.0, 5.0, 1.6, 4.0      # M2 heat-set insert (dia 3.2 x 4)
POCKET_TOP = 8.0                            # socket top is h 6.7 (board 1.2 + S55B 5.5)
# Frame pins that run through Framework's own board model at board level (its board must have holes
# there that the model leaves out); the adapter is located by the interposer screws and posts instead.
BOARD_PINS = [(32.5, 3.7), (-35.9, 3.7)]

# ------------------------------------------------------------------ OpenCascade helpers
def box(u0, v0, h0, u1, v1, h1):
    a, b = W(u0, v0, h0), W(u1, v1, h1)
    return BRepPrimAPI_MakeBox(gp_Pnt(*map(min, a, b)), gp_Pnt(*map(max, a, b))).Shape()
def cyl(u, v, h0, h1, r):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(*W(u, v, h0)), gp_Dir(0, 1, 0)), r, h1 - h0).Shape()
def prism(loop, h0, h1):
    mp = BRepBuilderAPI_MakePolygon()
    for u, v in loop: mp.Add(gp_Pnt(*W(u, v, h0)))
    mp.Close()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(mp.Wire()).Face(), gp_Vec(0, h1 - h0, 0)).Shape()
def _op(cls, a, b):
    op = cls(a, b); op.Build()
    if not op.IsDone(): raise RuntimeError(cls.__name__ + " failed")
    return op.Shape()
def cut(a, b): return _op(BRepAlgoAPI_Cut, a, b)
def fuse(a, b): return _op(BRepAlgoAPI_Fuse, a, b)
def common(a, b): return _op(BRepAlgoAPI_Common, a, b)
def volume(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def bbox(s):
    b = Bnd_Box(); BRepBndLib.Add_s(s, b); p, q = b.CornerMin(), b.CornerMax()
    return (p.X() - DX, q.X() - DX), (p.Z() - DZ, q.Z() - DZ), (p.Y() - DY, q.Y() - DY)
def solids(s):
    out, ex = [], TopExp_Explorer(s, TopAbs_SOLID)
    while ex.More(): out.append(ex.Current()); ex.Next()
    return out

def load_part(path, name):
    doc = TDocStd_Document(TCollection_ExtendedString("doc"))
    r = STEPCAFControl_Reader(); r.SetNameMode(True)
    if r.ReadFile(path) != 1: raise SystemExit(f"cannot read {path}")
    r.Transfer(doc)
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    found = []
    def label_name(lab):
        a = TDataStd_Name()
        return a.Get().ToExtString() if lab.FindAttribute(TDataStd_Name.GetID_s(), a) else ""
    def walk(lab, loc):
        ref = TDF_Label()
        if st.IsReference_s(lab) and st.GetReferredShape_s(lab, ref):
            walk(ref, loc.Multiplied(st.GetLocation_s(lab))); return
        if label_name(lab) == name: found.append(st.GetShape_s(lab).Moved(loc))
        if st.IsAssembly_s(lab):
            kids = Sequence_TDF_Label(); st.GetComponents_s(lab, kids)
            for i in range(1, kids.Length() + 1): walk(kids.Value(i), loc)
    roots = Sequence_TDF_Label(); st.GetFreeShapes(roots)
    for i in range(1, roots.Length() + 1): walk(roots.Value(i), TopLoc_Location())
    if len(found) != 1: raise SystemExit(f"expected one {name}, found {len(found)}")
    return found[0]

# ------------------------------------------------------------------ the edits
def modify(frame):
    u0, v_pocket, u1, _ = L.REAR_POCKET
    # 1. Rear pocket behind the socket: open the rear wall, then add a box behind it with its own floor,
    #    walls and roof. The outside moves from v -90.75 to -(92.85 + 1.6) = -94.45 over this width.
    frame = cut(frame, box(u0, REAR_OUTER - 0.2, FLOOR_TOP, u1, -89.0, POCKET_TOP))
    shell = cut(box(u0 - WALL, v_pocket - WALL, FLOOR_BOTTOM, u1 + WALL, REAR_OUTER + 0.25, REAR_WALL_TOP),
                box(u0, v_pocket, FLOOR_TOP, u1, -89.0, POCKET_TOP))
    frame = fuse(frame, shell)
    # 2. Cover-screw bosses: remove the stock ones (they meet the socket housing and the card) down to the
    #    floor, and add new ones outboard with an M2 heat-set insert hole.
    for u, v, r in STOCK_COVER_BOSSES:
        frame = cut(frame, cyl(u, v, FLOOR_TOP + 0.1, BOSS_TOP + 1.0, r))
    for u, v in L.COVER_BOSSES:
        frame = fuse(frame, cyl(u, v, FLOOR_BOTTOM + 0.5, BOSS_TOP, BOSS_R))
        frame = cut(frame, cyl(u, v, BOSS_TOP - INSERT_DEPTH, BOSS_TOP + 0.1, INSERT_R))
    # 3. Rear-wall ribs: trim them back so they stop 0.25 mm behind the card's rear edge.
    cu0, cv0, cu1, _ = L.CARD
    frame = cut(frame, box(cu0 - 0.5, cv0 - 0.25, 7.5, cu1 + 0.5, cv0 + 1.0, REAR_WALL_TOP + 0.5))
    # 4. Pins through the board, and a small lip at the front-left where the socket's front ear lands.
    for u, v in BOARD_PINS:
        frame = cut(frame, cyl(u, v, -0.9, 2.0, 1.3))
    frame = cut(frame, box(-54.2, -1.3, -0.9, -51.4, -0.1, 1.5))
    # 5. The locating pin in the rear notch at (17.4, -86.0) stands 0.46 mm above the board top: cut it
    #    flush with the board top so nothing reaches into the card gap.
    frame = cut(frame, cyl(17.4, -86.0, L.BOARD_THICKNESS, L.BOARD_THICKNESS + 1.0, 1.4))
    return frame      # (merging coplanar faces afterwards leaves four faces that fail to mesh)

# ------------------------------------------------------------------ fit check
def keepouts():
    """What must stay clear of the frame: the adapter board, the socket, the card and the space above it."""
    J3_BODY = (-59.0, L.J3_V - 44.45, -49.6, L.J3_V + 44.45)       # housing back to front, body 88.9 long
    J3_PADS = (-57.62, L.J3_V - 45.5, -52.47, L.J3_V + 45.5)        # ear pads (Foxconn layout)
    top = L.BOARD_THICKNESS
    return [
        ("adapter board", prism(L.outline_polygon(), 0.02, top - 0.02)),
        ("MXM socket body (S55B)", box(J3_BODY[0], J3_BODY[1], top, J3_BODY[2], J3_BODY[3], top + 5.5)),
        ("MXM socket ear pads", box(*J3_PADS[:2], top, *J3_PADS[2:], top + 1.8)),
        ("MXM card and the space above it", box(L.CARD[0], L.CARD[1], top, L.CARD[2], L.CARD[3], 16.5)),
    ]

def check(frame):
    bad = 0
    for label, tool in keepouts():
        hits = [s for s in solids(common(frame, tool)) if volume(s) > 0.01]
        print(f"  {label}: {'clear' if not hits else f'{len(hits)} overlaps'}")
        for s in hits:
            (a, b), (c, d), (e, f) = bbox(s)
            print(f"     {volume(s):7.2f} mm3 at u {a:.2f}..{b:.2f}, v {c:.2f}..{d:.2f}, h {e:.2f}..{f:.2f}")
        bad += len(hits)
    return bad

def write(shape, stem):
    os.makedirs(OUT_DIR, exist_ok=True)
    Interface_Static.SetCVal_s("write.step.schema", "AP214IS")
    Interface_Static.SetCVal_s("write.step.product.name", "printed_bottom_frame_mockup")
    w = STEPControl_Writer(); w.Transfer(shape, STEPControl_AsIs); w.Write(os.path.join(OUT_DIR, stem + ".step"))
    BRepMesh_IncrementalMesh(shape, 0.05, False, 0.3, True)
    sw = StlAPI_Writer(); sw.ASCIIMode = False
    sw.Write(shape, os.path.join(OUT_DIR, stem + ".stl"))

def main():
    if not os.path.exists(STEP_IN): raise SystemExit(f"missing {STEP_IN} (get it from FrameworkComputer/ExpansionBay)")
    stock = load_part(STEP_IN, FRAME_PART)
    print("stock frame: check against the adapter layout")
    check(stock)
    frame = modify(stock)
    print("printed frame mockup: check against the adapter layout")
    bad = check(frame)
    (a, b), (c, d), (e, f) = bbox(frame)
    print(f"frame: {len(solids(frame))} solid(s), {volume(frame) / 1000:.1f} cm3, "
          f"u {a:.1f}..{b:.1f}, v {c:.1f}..{d:.1f}, h {e:.1f}..{f:.1f}")
    write(frame, "printed_frame_mockup")
    print("wrote", os.path.join(OUT_DIR, "printed_frame_mockup.step"), "and .stl")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
