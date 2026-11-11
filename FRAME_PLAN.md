# Printed bottom frame: plan

Status: plan only (2026-11-10). Nothing here is modelled yet.

The stock graphics-module shell is too small for an MXM Type B card plus its socket (`RESEARCH_TODO.md`
item 7b). This plan replaces the shell's plastic bottom frame with a printed one. The outside is copied
from Framework's model; only the inside changes.

Coordinates are the ones used everywhere in this repo: u across the bay, v toward the laptop edge, the
origin midway between the interposer screws, heights (h) above the adapter board's underside. They come
from Framework's graphics-module STEP (FrameworkComputer/ExpansionBay, CC BY 4.0; not redistributed
here).

## What the frame is

Framework's model splits the shell into these parts. Only the first is replaced.

| Part in the STEP | What it is | Plan |
|---|---|---|
| IFGP6_DIS_FRAME_BTM | Plastic bottom frame, 356.6 x 100.3 x 24.1 mm. Spans the whole width of the laptop; holds the board, the fans and the other parts | **Print a modified copy** |
| IFGP6_DIS_FRAME_BTM_R | A second part under the frame | Reuse if it comes off the stock frame; otherwise merge into the print |
| IFGP6_DIS_FRAME_TOP_A | Top piece over the rear strip (v -90.75..-58.3), screwed to the two cover-screw bosses | Replaced by the printed cover, which then fastens wherever the new frame puts its bosses |
| IFGP6_MXM_BOX_AL | 1 mm aluminium floor plate under the front half of the board (v -51.6..4.3), 3.34 mm below the board | Reuse; keep its two screw points (below) |
| IFGP6_DIS_SUPP_FRAME_L / _R | End supports at the far ends of the bay | Reuse; keep their mounting features unchanged |
| Fans, heatsink, meshes | The 7700S cooling | Cooler is still open; keep the fan mounts so the stock fans stay usable |

## The socket height has to change too

The printed frame alone is not enough with the 5.5 mm socket (S55B). With S55B the card underside is
2.7 mm above the board, below the interposer stiffener (4.45 mm), so the card's front edge must stay
behind v -5.75. The card is centred in the socket, so the socket's rear end then lands at v -90.75 (body)
and its rear ear pad at v -92.25. The frame's rear wall is only 1.3-1.6 mm thick: inner face v -89.15,
outer face v -90.75, which is also the laptop's rear surface. A copied outside cannot make that room
without a bulge at the rear left corner.

Foxconn's drawing (AS series, one sheet for all heights) gives the lengths along the socket:
- pegs 82.00 apart; the card is centred between them;
- ear pads 3.00 x 5.15, centred 3.00 past each peg, so copper spans 91.0 mm;
- socket body 88.9 mm overall.

With the 7.8 mm socket (S78B) the card underside should be about 5.0 mm up (unconfirmed, see step 1),
clear of the stiffener (4.45 mm). The card can then sit over the stiffener, and everything fits along
the left edge:

| v | What |
|---|---|
| -89.15 | Rear wall, inner face (unchanged) |
| -88.85 | Board rear edge (0.3 mm from the wall) |
| -88.55 | Rear ear pad end (0.3 mm copper to edge) |
| -43.05 | Socket centre |
| -84.05 .. -2.05 | Card |
| -0.80 | Spring-screw tip edge (5.16 mm high; the card stays 1.25 mm behind it) |
| +2.45 | Front ear pad end |
| 0 .. 5.2 | Stock left fan cable path (u < -46.1): has to move, see below |

Margins: 0.55 mm between the card's underside and the stiffener top, if the 5.0 mm gap holds; 1.25 mm to
the spring screws. The cost is about 2.3 mm less height above the card for the cooler.

Across, the inner walls are 131.9 mm apart (u -73.29..58.64). Card (u -54.3..50.7) plus socket housing
(back at u -59.0) fit once the cover-screw bosses move (below).

## Inside features (from the STEP)

Features at board level and under the board. A feature is kept where its position is fixed by the
laptop, and moved or removed where it only served the stock 7700S board or blocks the card.

**Keep unchanged (laptop interface)**
- Interposer insert pockets at (-8.3, 0) and (8.3, 0), dia 5.6/6.8.
- Shell posts through the board notches at (-20.8, 2.9) and (20.2, 2.9), dia 3.2 hole in a dia 5.2 post.
  The adapter board copies the stock notches (r 3.0).
- Everything outside the inner walls: the outer skin, the rear face and its openings, the end-support
  mounts, the fan mounts.
- Aluminium floor plate screw points at (-77.5, -47.9) and (62.8, -47.9).

**Remove or move (stock 7700S board / blocks the card)**
- Cover-screw bosses at (-61.8, -65.6) and (50.0, -65.6) (ledge with an M2 nut, 1.4-5.0 mm high): the
  right one sits under the card's end (card to u 50.7). Move both outboard, about u -66 and +55. The
  printed cover uses the new positions.
- Front-left ledge at board level (u -62..-51, v > -3.3): remove. The socket's front end sits there.
- Board support pin at (-56.0, -72.2) (dia 1.8/3.0, under the board): under the socket; remove.
- Board support pin at (45.1, -72.2): under the card area but below the board; keep only if the adapter
  board has no bottom-side parts there.
- Support post at (-40.8, 2.9) (dia 3.2/5.2, under the board): keep as a board support if it lands clear
  of the adapter's bottom-side parts.
- Stock board fixings: screw boss at (44.7, -6.1), rear boss at (2.7, -83.6) (in a 2.8 mm board notch)
  and rear insert pocket at (-17.3, -83.6). The adapter can keep using them (the draft does), or the
  frame can put new ones where the layout wants them.
- Rear-wall ribs at h ~9.75 near v -87.3 (u around -38, -28, 10, 27): above the board; check them
  against the card and cooler once the cooler is chosen.

**Add**
- Card hold-down standoffs: the card screws to the adapter board at the two Foxconn hold-down points
  (66 mm from the socket's peg line, +-37.5 mm). If the frame should take the load instead, add M2
  bosses under those two points.
- Left fan cable path: the socket's front end blocks the stock path (v 0..5, u < -46.1). Move the fan
  connector J4 outboard of the socket (board extended to about u -66 at the front left), so the cable
  never crosses the socket. Check the cable's reach on the real fan.
- Ribs to stiffen the frame where the moulded original relies on thin walls (inside only).

## Printing

- Size: one piece is 356.6 x 100.3 x 24.1 mm.
  - Desktop printers (256 mm or 250 x 210 mm beds) need it split. Both halves stay under 250 mm for a
    joint anywhere in u -79.3..64.7. Keeping it clear of the card and the interposers leaves
    u -79.3..-59.4 or u 51..64.7, through a side-wall region. Use a lap joint with screws or adhesive.
  - A large-format printer (360 mm class) or a print service can do it in one piece. JLCPCB's 3D-printing
    service (MJF nylon or SLA resin) is the simplest, since the PCB is going there anyway. Check its
    current maximum part size before ordering.
- Material: not PLA (softens at ~55-60 C, too close to a GPU). PETG, ASA, nylon (PA12 MJF) or PA-CF.
- Fit first: print test coupons before the whole frame:
  - the interposer region with the two posts and insert pockets, to check alignment in the laptop;
  - the rear left corner, to check the socket and board clearance to the rear wall.

## Steps

1. **Confirm the S78B card gap.** The Foxconn sheet gives the three socket heights (4.3/5.5/7.8) but not
   each one's card gap. Sources: Foxconn's per-height drawing, a 3D model of the S78B, or measuring a
   socket. It needs to be at least ~4.95 mm (stiffener 4.45 + 0.5).
2. **Check the card's underside** along its long edge nearest the laptop (middle ~45 mm, first ~3.5 mm
   from the edge): that strip sits over the stiffener with ~0.55 mm to spare, so any part there must be
   flatter than that. Photo or measurement of the X-Vision card.
3. **Confirm the height budget**: card top at about h 7.4 (board 1.2 + gap 5.0 + card 1.2), plus the
   GPU and the cooler, against the bay's top limit (Framework's ExpansionBay drawings) and the printed
   cover.
4. **Extract the frame** from Framework's STEP as its own solid (FreeCAD can open the assembly and
   export one body), then make the inside edits above.
5. **Update the PCB draft** to the printed-frame layout: S78B in `generate_pcb.py`, socket centre
   v -43.05, rear board edge -88.85, J4 outboard, keep-outs from the new frame. Same footprint (the pads
   are identical across heights).
6. **Test coupons**, then the full frame.

## Licensing

Framework's model is CC BY 4.0, which allows derived parts. A printed frame published here must credit
Framework and say it was modified. The rest of the repo stays CERN-OHL-S v2.
