# Printed bottom frame

Status (2026-11-11): a **mockup** exists. `generate_frame.py` builds it from Framework's model and writes
`mechanical/printed_frame_mockup.step` / `.stl`; previews are in `mechanical/preview/`. It passes a fit
check against the adapter board, the MXM socket and the card. It has not been printed or test-fitted,
and the open checks below come first.

The stock graphics-module shell is too small for an MXM Type B card plus its socket (`RESEARCH_TODO.md`
item 7b). The plan is to replace the shell's plastic bottom frame with a printed one. It is Framework's
frame lengthened by 3.7 mm at the rear over its full width, with the inside changed.

Coordinates are the ones used everywhere in this repo (`layout.py`): u across the bay, v toward the
laptop edge, the origin midway between the interposer screws, and h above the adapter board's underside.
They come from Framework's graphics-module STEP (FrameworkComputer/ExpansionBay, CC BY 4.0; not
redistributed here because of its size).

## Decision: keep the 5.5 mm socket and move the rear wall back

- The card has to stay behind the interposer stiffener. With the 5.5 mm socket (S55B) the card underside
  is 2.7 mm above the board, below the stiffener's 4.45 mm, so its front edge stays behind v -5.75.
- The socket's rear end then overruns the rear wall. The card is centred in the socket, so the socket's
  rear ear pad reaches v -92.25 and the board edge -92.55. The stock rear wall's inner face is at
  v -89.15 and its outer face (the laptop's back) at -90.75.
- **Fix:** lengthen the frame by 3.7 mm over its full width, just in front of the rear wall. The whole
  rear wall moves back: inner face -92.85, the laptop's rear face -94.45. This keeps the outside's
  shape (a straight back, the vents and the rounded corners, all as stock) and gives 5.1 mm between the
  card's rear edge and the wall for heat pipes or a heatsink. A first version used a 12.7 mm wide pocket
  behind the socket only; the full-width version replaced it.
- **Why not the 7.8 mm socket (S78B):** it would let the card sit over the stiffener and avoid moving
  the wall, but the card's front hold-down standoff would then land on the right interposer's stiffener
  (u 1.3..21.2, v -5.25..5.25). Clearing that moves the socket back about 2.2 mm anyway, so the rear
  wall would have to move too. S55B also keeps 2.3 mm more height for the cooler, and its 2.7 mm card
  gap is documented, while S78B's is not.

Along the left edge with S55B (socket centre v -46.75):

| v | What |
|---|---|
| -94.45 | Rear face of the laptop (stock -90.75) |
| -92.85 | Rear wall, inner face (stock -89.15) |
| -92.55 | Board rear edge (left extension) |
| -92.25 | Rear ear pad end (0.3 mm copper to edge) |
| -87.75 .. -5.75 | Card |
| -1.25 | Front ear pad end |
| -0.50 | Board front edge (the stock frame's front-left ledge is gone) |
| 0 .. 5.2 | Left fan cable path, unchanged |

Across: card u -54.3..50.7 and socket housing back at u -59.0, between the inner walls at u -73.29 and
+58.64.

## Frame parts

Framework's model splits the shell into these parts. Only the first is replaced.

| Part in the STEP | What it is | Plan |
|---|---|---|
| IFGP6_DIS_FRAME_BTM | Plastic bottom frame, 356.6 x 100.3 x 24.1 mm. Spans the whole width of the laptop; holds the board, the fans and the other parts | **Printed, modified copy** (104.0 mm deep) |
| IFGP6_DIS_FRAME_BTM_R | A second part under the front of the frame (v -56.2 forward) | Reuse; in front of the lengthened part |
| IFGP6_DIS_FRAME_TOP_A | Top piece over the whole rear strip (v -91.2..-58.2, full width), screwed to the two cover-screw bosses | Replaced by a printed cover, 3.7 mm deeper, using the new boss positions (not drawn yet) |
| IFGP6_MXM_BOX_AL | 1 mm aluminium floor plate under the front half of the board (v -51.6..4.3) | Reuse; its screw points are unchanged |
| IFGP6_DIS_SUPP_FRAME_L / _R | End supports in the rear corners (v -89.3..-55.9) | Reuse; their fixings are in front of the stretch and unchanged, but they now stop 3.7 mm short of the rear wall. Print longer copies if they need to bear on it |
| Fans, heatsink, meshes | The 7700S cooling | Cooler still open; the fan mounts are unchanged |

## What the mockup changes (generate_frame.py)

1. **Lengthened at the rear** (`layout.REAR_STRETCH` = 3.7 mm at `layout.REAR_STRETCH_AT` = v -88.0):
   - The frame is split at v -88.0, where the cut only crosses the floor, the end walls, the rear-wall
     ribs and three small webs behind the board.
   - Everything behind the plane (the rear wall, its vents, the corners) moves back 3.7 mm, and the
     cross-section at the plane is extruded to fill the gap.
2. **Cover-screw bosses** (`layout.COVER_BOSSES`):
   - The stock ones at (-61.8, -65.6) and (50.0, -65.6) are removed down to the floor. The right one sat
     under the card; the left one was 0.1 mm from the board edge.
   - New dia 6.0 bosses go at (-66.0, -65.6) and (55.0, -65.6), up to h 5.0 like the stock ledge, each
     with a dia 3.2 x 4 mm hole for an M2 heat-set insert.
3. **Rear-wall ribs** at h ~8.2-10.1 are trimmed back to 0.25 mm behind the card's rear edge.
4. **Two frame pins** at (32.5, 3.7) and (-35.9, 3.7) are removed. In Framework's own model they run
   through its board, so the real board must have holes the model leaves out. The adapter is located by
   the interposer screws and the shell posts instead.
5. **A small lip** at the front-left (u -54..-52, v -1.0..-0.4) is cut. The socket's front ear pad lands
   there.
6. **The locating pin in the rear notch** at (17.4, -86.0) is cut flush with the board top. It stood
   0.46 mm above the board, under the card.

Kept as is:
- the interposer insert pockets;
- the shell posts at (-20.8, 2.9) and (20.2, 2.9), which pass through the board's notches;
- the board supports and fixings under the board;
- everything in front of v -88.0 outside the inner walls (fan bays, end-support fixings).

The board support pin at (-56.0, -72.2) is now under the socket; it is below the board, so it stays
unless the adapter puts bottom-side parts there.

Fit check, run by the script (`generate_frame.py` exits non-zero if any fail):

| Item | Stock frame | Mockup |
|---|---|---|
| Adapter board | rear wall, 2 pins, front lip | clear |
| MXM socket body (S55B) | rear wall | clear |
| MXM socket ear pads | rear wall | clear |
| Card and the space above it (to h 16.5) | right boss, rear ribs, rear pin | clear |

## Open checks before printing

1. **The laptop behind the module.** The whole rear face sits 3.7 mm further back (v -94.45).
   - Check that the lid and hinge clear it at every opening angle.
   - Check that the module still slides in and out of the bay, and that the laptop's own rear edge or
     latch doesn't meet the longer frame.
   - Measure on the laptop before printing.
2. **The height budget.** Check the card, GPU and cooler against the bay's top limit (Framework's
   ExpansionBay drawings) and the printed cover.
3. **The top cover.** IFGP6_DIS_FRAME_TOP_A has to be redrawn 3.7 mm deeper, with screw holes at the new
   boss positions.
4. **Printability.**
   - The copied walls come from an injection-moulded part, so many are only 1-1.6 mm thick.
   - Thicken or rib them for printing where the outside allows.
   - Check overhangs for the chosen print orientation.
5. **Outside fit.** Print test pieces first:
   - the interposer region, with the two posts and insert pockets, to check alignment in the laptop;
   - a rear corner, to check the longer rear against the laptop.

## Printing

- Size: one piece is 356.6 x 104.0 x 24.1 mm.
  - Desktop printers (256 mm or 250 x 210 mm beds) need it split. Both halves stay under 250 mm for a
    joint anywhere in u -79.3..64.7.
  - Keeping the joint clear of the card and the interposers leaves u -79.3..-59.4 or u 51..64.7,
    through a side-wall region. Use a lap joint with screws or adhesive.
  - A large-format printer (360 mm class) or a print service can do it in one piece. JLCPCB's
    3D-printing service (MJF nylon or SLA resin) is the simplest, since the PCB is going there anyway.
    Check its current maximum part size before ordering.
- Material: not PLA (softens at ~55-60 C, too close to a GPU). PETG, ASA, nylon (PA12 MJF) or PA-CF.

## Rebuilding

```
python -m venv cadenv
cadenv/Scripts/python -m pip install cadquery-ocp
cadenv/Scripts/python generate_frame.py
```

It needs Framework's `FW_GRAPHICS_MODULE_REF_00-1.stp` in `reference/`. The adapter's outline and
positions come from `layout.py`, the same module `generate_pcb.py` uses, so the frame follows any layout
change.

## Licensing

The frame is a modified version of Framework Computer's part from FrameworkComputer/ExpansionBay and
is licensed CC BY 4.0, like the original: credit Framework Computer and note the changes. The rest of
the repo stays CERN-OHL-S v2.
