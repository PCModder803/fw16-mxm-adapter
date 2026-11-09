# What still needs a document, a measurement or a laptop

Open items, plus the findings that resolved earlier ones. Each open item says what it blocks, where to
look, and what to bring back. Files under `reference/evidence/` and `reference/framework_pcb_ref/` and the
two Framework/community files in `reference/` are kept locally and not published in this repository.

## Documents to get

### 1. Fintek F75303M SMBus address (U4): done
- Resolved by the FW16 7040 mainboard interface schematic (`reference/fw16_7040_mainboard_interfaces_schematic.pdf`,
  page 9 "THERMAL SENSOR"). The mainboard's own sensor UTH1 is "F75303M_MSOP10" (Compal PN
  SA000046C00), pinout 1 VCC, 2 DP1, 3 DN1, 4 DP2, 5 DN2, 6 GND, 7 THERM#, 8 ALERT#, 9 SDA, 10 SCL, with
  the note "SMB3_Address 1001_101xb 0x9A".
  8-bit 0x9A = 7-bit 0x4D, which is what the descriptor expects. So the plain F75303M answers at 0x4D.
  (The mainboard sensor is on a different EC bus, SMB3, so there's no conflict with U4 on the ALW bus.)
- The mainboard uses MMBT3904 (NPN) as its remote diodes, with 2200 pF across each pair; MMBT3906 (PNP)
  on the adapter also works, wired as a diode the same way.
- Earlier searches, kept for reference:
- Checked, no help: ic-components.com F75303M listing (2026-11-03). It confirms Fintek / MSOP10 but gives
  no address and no datasheet; it lists F75303MA only as an unlabelled alternate (could be an address
  variant; ask Fintek).
- Checked, no address: Zephyr `fintek,f75303` binding and driver (2026-11-03). The address comes only from
  the board's devicetree; the only one in Zephyr is `reg = <0x70>` in the build-all test, an arbitrary
  placeholder. Useful for bring-up: temperature registers local 0x00/0x29, remote1 0x01/0x10,
  remote2 0x23/0x24 (high/low), 0.125 C per step.
- Also in ExpansionBayConfigurationGenerator: `gn22_newthermal.c` uses the same F75303 at 0x4D as
  `pcie_thermal.c`, so Framework's own GN22 module has an F75303 at 0x4D on its board.

### 2. MXM 3.1 electrical specification: done
- Read MXM Electromechanical Specification v3.1 r1.0 (Scribd viewer). Findings are under "MXM 3.1 spec
  findings" at the end of this file; the schematic was updated to match.

### 3. X-Vision RX 6600 XT MXM card: remaining numbers (sizes the 5 V / 3.3 V rails, J3 height)
- Known (X-Vision): TDP 105 W, total board power 100 W, 82 x 105 mm (standard MXM Type B), operating
  temperature 0-55 C. The card ships bare: no heatsink or heatpipes.
- VSYS budget: 100 W is 5.0 A at 20 V (AC) and 6.6 A at 15.2 V (battery), under the eFuse's 9.9 A limit and
  the host's 10.5 A. The limit trips only if VSYS drops below about 10.1 V at full load.
- 5V / 3V3 / PWR_SRC limits are now settled by the MXM spec (Table 3.5): a compliant module draws at most
  2.5 A on 5V and 2.0 A on 3V3, exactly what the host provides. PWR_SRC is 7-20 V (never below 6.5 V or
  above 22 V peak), up to 10 A.

- Photos: `reference/card_photos/` (board marking EM23G V1.1).
  - Front: AMD Navi 23 with an exposed die inside a metal stiffener frame, and four Micron GDDR6 (D9ZPP).
    The 9-phase VRM runs along the edge opposite the MXM fingers: 9 power stages under STC R15/R33
    inductors, which are the tallest parts on the front. There are smaller regulators with 1R5 inductors
    at the left and right edges (U2301, U2302/U2318).
  - Back: no tall parts. The tallest are the polymer caps (marked "560" and "22") behind the VRM and at the
    left edge, 1.8 mm (caliper). U5 (SOIC-8, right side) is probably the VBIOS SPI flash.
- Bare card overall: 8.2 mm, back-side caps to the tallest front parts (caliper).
- Card plus vapor chamber and heat pipes is about 15 mm, from the lowest back-side component to the top of
  the heatsink (user estimate).

### 3b. Cooler for the bare card (new)
- The card needs a heatsink/heatpipe or vapor-chamber assembly that contacts the GPU die, VRAM and VRM and
  fits under the graphics module's two fans. Its thickness plus the card's sets the J3 stack height (item 6).
- 105 W is in the same class as Framework's own RX 7700S module (100 W) in this shell, so the fans should
  be adequate if the heatsink is comparable.
- Contact areas from the photos:
  - the GPU die (bare die: needs a flat cold plate; the die sits below the stiffener frame);
  - the four GDDR6 chips, with thermal pads;
  - the 9 power stages along the top edge, and the inductors if possible, with pads;
  - the side regulators near U2301 / U2302.
- Planned: Alpha Novatech vapor chamber + heatsink, cooled by the graphics module's two fans.
- Heatpipes (VC to the fin stacks at the fans), starting point:
  - 4 x 6 mm sintered-wick copper pipes, flattened to ~3 mm, 2 per fan; or 3 x 8 mm flattened to ~3.5 mm.
  - Size them so the total rated Qmax, after derating for flattening, bends and length, is at least
    ~150 W (105 W at <=70% of Qmax).
  - Sintered wick only, because the laptop's orientation varies.
- Mounting: use the four holes around the GPU (the standard MXM heatsink pattern) and back it with a
  backplate or spring screws. Nothing on the back of the card is tall enough to block a thin backplate.

### 4. Foxconn AS0B826 drawing (S55B chosen)
- Decision (2026-11-06, revised 2026-11-07): S55B on a 1.2 mm adapter (Framework's reference thickness, for
  the interposer inserts), with a 3D-printed cover that is flat at the high (15.3 mm) level over the whole
  bay. See item 6.
  S78B is dropped. Still confirm the 2.7 mm gap and the pad pattern on the drawing.
- The footprint assumes S55B. Stack heights confirmed by the user (2026-11-03): S55B = 5.5 mm,
  S78B = 7.8 mm. Still to check on the drawing: that the pad pattern and board-lock/peg holes are the same
  for both, so the footprint doesn't change with height.
- Earlier estimate (before the shell arrived): the user's 15 mm runs from the card's lowest back-side component to the top of the heatsink. The stack
  height is measured to the card PCB's underside, and the 1.8 mm back-side caps sit inside that gap. So
  above the stack: 15 - 1.8 = ~13.2 mm.
- CORRECTION (2026-11-06): 5.5 mm is the connector's overall height, not the gap under the card. Critical
  Link's MXM connector wiki lists AS0B826-S55B-7H as 5.5 mm overall with 2.7 mm PCB-to-module spacing. The
  old budget here used 5.5 / 7.8 mm as that spacing and is withdrawn, along with the "5 mm too tall"
  figures first written in item 6. Confirm 2.7 mm on the Foxconn drawing; S78B's spacing is still unknown.
- Lower option checked (2026-11-06): JAE B2 parts are not a dependable choice. JAE bulletin MB-370 (Oct 2020)
  lists MM70-314B2-1-R500 and MM70-314-310B2-1/-2-R500 as discontinued, 4.3 mm overall, "Type B2" footprint,
  card-interface compatible only, so the footprint differs and no B2 drawing was found. DigiKey shows them
  obsolete; the only stock seen is one unverified lot of 84 (Seba Components, via distyparts). The 1.5 mm
  board height comes only from a search summary of Mouser's page. It is less than the card's 1.8 mm back
  caps, so the adapter would need pockets or windows under them. JAE's active replacement,
  MM70-314B1-2-R300, is 6.7 mm overall with 3 mm post height (MB-370 drawing), which is taller, not lower.
- Other parts listed with a 2.7 mm gap: Aces 91781-314xx, 5.2 mm overall (Critical Link wiki). No gain under
  the card. No active socket with a gap under 2.7 mm has been found.
- See item 6 for the fit in the shell.

### 5. C1/C4 clearance (EEH-ZA1V101P)
- Panasonic datasheet confirms 8 x 10.2 mm; the CP_Elec_8x10.5 footprint fits.
- Remaining: measure in the bare shell that there is at least ~10.5 mm from the adapter's top surface to
  the cover beside the card. The caps must sit outside the card outline.
- Shell result (2026-11-06): ~14.1 mm above a 1.2 mm adapter (15.3 mm flat cover) is enough height, but the
  card fills the 107 x ~80 mm usable area, so there is no obvious spot beside it. Look for 8 mm spots in the
  corners next to the fans, or change C1/C4 to low-profile parts that fit under the card (2.7 mm gap with
  S55B, less the card's 1.8 mm back-side caps where they overlap).

## Measurements

### 6. Graphics module internal height (choose the J3 stack height)
- Framework's drawing gives the module as 26.15 mm thick overall. The UMA expansion-bay PCB drawing
  limits components to 5.0 mm on top and 1.4 mm underneath (`reference/evidence/fw_ref_pcb_sheet1_height_limits.png`),
  but that is for the fan shell, not the graphics module.
- Do: open `Mechanical/GraphicsModule/FW_GRAPHICS_MODULE_REF_00-1.stp` (in the ExpansionBay repo) in
  FreeCAD or the KiCad 3D viewer. Measure from the board seating plane to the inside of the top cover,
  then subtract the card's thickness and the cooler you design for it (items 3 and 3b).

- The bare graphics-module shell (on order) answers this directly: measure seating plane to cover with
  calipers. Also check whether it includes the interposer board and fans, and the size of the rear port
  cutout (needed for item 11).

- Shell measured by the user (2026-11-06), photo `reference/card_photos/1000010391.jpg`:
  - Top of standoff to ceiling: 9 mm over the card/heatsink area, 15.3 mm over the fans. (The 15.3 mm was
    first taken as the ceiling everywhere; 9 mm governs the card.)
  - Top of standoff to floor: 3.3 mm. Interior over the card is 12.3 mm floor to ceiling.
  - Card: die top is 1.67 mm above the card PCB. Card PCB 1.35 mm (measured 2026-11-07, below).
  - Interposer location: the laptop-side long edge, circled in `reference/card_photos/1000010392.jpg`.
    That photo also shows raised plastic ribs on the rear third of the floor; their height is unmeasured.
  - USB-C opening: 8.6 x 3.25 mm, centred across the width, bottom 2.4 mm above the standoff.
  - Usable area: 107 mm wide (fan to fan) x ~80 mm deep.
  - Fans: 72.2 mm wide, 10.4 mm tall, 20 mm from fan to rear exhaust vent (space for fin stacks).
- Superseded by the flat-cover decision below; kept for the record.
  Height result against the 9 mm ceiling, adapter on the standoffs, bare card with no cooler. The card's
  tallest front parts are 6.4 mm above its underside (8.2 mm bare - 1.8 mm back caps). Spacing is the
  PCB-to-card gap from item 4:

  | Adapter PCB | Socket spacing | Card underside | Tallest parts | Against 9 mm |
  |---|---|---|---|---|
  | 1.6 mm | 2.7 mm (S55B) | 4.3 mm | 10.7 mm | 1.7 mm over |
  | 1.0 mm | 2.7 mm (S55B) | 3.7 mm | 10.1 mm | 1.1 mm over |
  | 1.6 mm | 1.5 mm (JAE B2, unverified) | 3.1 mm | 9.5 mm | 0.5 mm over |
  | 1.0 mm | 1.5 mm (JAE B2, unverified) | 2.5 mm | 8.9 mm | 0.1 mm clear |

- The planned 13.2 mm card + cooler can't fit under 9 mm in any case. The inductors are the limit, not the
  die: on the last row, about 3.6 mm remains above the die if the card PCB is 1.2 mm (assumed, unmeasured).
- With an active 2.7 mm socket on a 1.0 mm adapter, the inductors need ~1.5 mm of relief in the cover (1.1 mm
  over + ~0.4 mm clearance), and about 2.4 mm remains above the die (card PCB assumed 1.2 mm). Measure the
  cover's thickness over the inductors to see if that relief is possible.
- Measured 2026-11-07, with the card lying loose on the standoffs and the stock cover closed: about 3 mm between
  a 1R5 inductor and the cover, and two R33 inductors almost touching it. So the stock ceiling over the
  inductors is lower than 9 mm. The stock cover can't work even before the socket raises the card.
  Cover: plastic, 1.65 mm thick over the inductors, 6.44 mm from its lowest to highest point.
  Card PCB: 1.35 mm. Front parts above the card PCB: 8.2 - 1.8 - 1.35 = 5.05 mm. Die top: 1.67 mm.
  Floor: the dark grey plastic areas are 1.24 mm above the silver aluminium centre (taken as floor-side, i.e.
  ~2.06 mm below the standoff top if the 3.3 mm was measured to the silver).
- Chosen fix: the user prints a replacement cover with its inside flat at the high level (15.3 mm above the
  standoff) across the bay, keeping the stock outer envelope. With S55B:

  Card underside = adapter + 2.7 mm. Inductor tops = underside + 1.35 + 5.05 = underside + 6.4 mm.
  Die top = underside + 1.35 + 1.67 = underside + 3.02 mm.

  | Adapter PCB | Card underside | Inductor tops | Clear under 15.3 | Die top | Room above die |
  |---|---|---|---|---|---|
  | 1.6 mm | 4.3 mm | 10.7 mm | 4.6 mm | 7.32 mm | ~8.0 mm |
  | 1.2 mm (chosen) | 3.9 mm | 10.3 mm | 5.0 mm | 6.92 mm | ~8.4 mm |
  | 1.0 mm | 3.7 mm | 10.1 mm | 5.2 mm | 6.72 mm | ~8.6 mm |

  1.2 mm is chosen to match Framework's board and inserts (see Consequences below). The cooler gets
  ~8.4 mm over the die and ~5 mm over the inductors.
- User accepts (2026-11-07) that the taller cover may limit how far the screen tilts back.
- The two screw posts at the interposer edge are 35.8 mm apart, centre to centre. They fasten the bay to the
  laptop. The interposer's own threaded inserts (Framework part ES00000NY00, M2, per the ExpansionBay repo)
  and the board outline come from FW_EXPANSION_BAY_PCB_0807 (PDF/DXF) in the ExpansionBay repo (read below).
- Framework reference PCB drawing (`reference/framework_pcb_ref/FW_EXPANSION_BAY_PCB_0807.pdf`, read 2026-11-07).
  This is the fan-only (UMA) module's board, not the graphics shell, but the interposer is the same:
  - Board 118.65 mm wide, 1.2 mm thick. Interposer edge features from the left mounting hole: +32 mm insert 1,
    +16.65 mm insert 2, +35.25 mm right mounting hole, then 10.3 mm to the board edge. A datum hole sits 30.2 mm
    from insert 2.
  - The two interposer screws (into "FBCAN standoffs") are 16.65 mm apart, one in the middle of each interposer.
    Our FW16_FXBeam footprints have their 2.7 mm holes at x = -8.33 / +8.32: 16.65 mm. Matches.
  - Height limits: 5.0 mm on the board generally, 2.5 mm in the interposer zone (detail A).
  - Assembly (sheet 3): the interposer pair sits on top of the PCB and M2 screws go down through it into the
    inserts. Cover-door and lock-plate dimensions are also on sheet 3.
- Insert ES00000NY00 (`reference/framework_pcb_ref/ES00000NY00_insert_M2x1.7.pdf`): brass, tin plated, SMD
  solder. Flange 4.0 mm diameter x 0.6 mm, barrel 2.5 mm diameter x 1.1 mm, M2x0.4 thread, 1.7 mm overall.
  The barrel (1.1 mm) fits inside Framework's 1.2 mm board. No land pattern is given.
- Consequences:
  - Use a 1.2 mm adapter board, as Framework does, not 1.6 mm. The interposer screw length is set by
    Framework's parts, so a thicker board loses thread engagement. With S55B on 1.2 mm under the flat cover:
    card underside 3.9 mm, inductor tops 10.3 mm (5.0 mm clear), die top 6.92 mm, ~8.4 mm above the die.
  - Footprint change still needed: the 2.7 mm holes are bare NPTH. The insert needs a copper ring (>4.0 mm) to
    solder its flange on the side opposite the interposer. Confirm which side and the barrel fit on Framework's
    PCIe test board before editing the footprints.
  - Still unknown: where the interposer sits relative to the graphics shell. The bay-to-laptop posts are
    35.8 mm apart, which is not the 16.65 mm insert spacing. Measure on the PCIe test board.
- Cover checks before printing: (1) the recessed area may exist for intake air or laptop-side clearance, so
  check that filling it doesn't block the fan intakes or hit anything when the module is installed;
  (2) print in a heat-tolerant plastic (PC, ASA or nylon, or a printing-service PA12), not PLA, and treat PETG
  as marginal next to a 100 W card; (3) copy the stock cover's clips, screw bosses and mating edges.
- Earlier options considered: (a) lowest available socket + 1.0 mm adapter + a thin cold plate cut around the inductors, with
  pockets or a replacement cover over them; (b) a stepped design with the card-carrying board on the floor and the
  interposer board on the standoffs (1.6 mm clear above the inductors, but PCIe must cross the 3.3 mm step and
  the floor ribs must clear); (c) a taller custom cover. Heat pipes to the far fan must cross the inductor row.
- Footprint result: the card is 105 x 82 mm, so 105 mm runs fan to fan (as in the photo), with 2 mm spare
  before J3's body is counted, and the card is ~2 mm deeper than the usable 80 mm. Check J3's length beyond
  the card edge on the Foxconn drawing.

### 7. Board-ID pull-up rail voltage (R1/R2)
- 330k on ID0/ID1 reads as BOARD_VERSION_12 only if the laptop's 100k pull-up goes to about 2.81 V. That
  voltage was inferred from the EC's thresholds, not measured.
- No graphics module is needed. A wrong ID is harmless: the EC simply doesn't detect the module and never
  powers it. So build the first adapter with 330k, then measure the voltage across R1 with the laptop on.
  Check what the EC detected with Framework's `framework_tool` (its expansion-bay status option), and swap
  R1/R2 if needed.
- Or ask Framework (question 3 below).
- Mostly answered (2026-11-08, t/74018 original poster): their boards always passed detection with 330k on
  ID0/ID1, checked by probing the interposer pads. They believe the pull-ups are 3.3 V. So 330k stays, and
  the measurement on the first build is now just a check. Note: 3.3 V through 100k into 330k gives 2.53 V,
  above the 2040-2197 mV window, so if the rail really is 3.3 V the pull-up is not 100k. The empirical
  result is what counts; the measurement will settle the numbers.
- Same reply: they got full 20 V on VSYS by flashing a suitable descriptor to the EEPROM, matching the plan.
  They did not level-shift PWR_EN. Since their module turned on, its PWR_EN input evidently accepted the
  host's level. U6 stays: its 1.35 V input threshold works whether the host drives 1.8 V or 3.3 V, and it
  also holds the card off until the eFuse reports power good.

## Questions for Framework (no graphics module available here)

### 8. Power interposer pins 52/53/54 in GPU mode: done (schematic changed)
- From the FW16 7040 interface schematic, page 3. Pins 52/53 (connector JFXB1 F3/G3) go through switch
  UC77 (NX3DV221). Its select input is SSD_GPU_SEL, which the EC drives from the descriptor's
  GPU_PCIE_MUX_SEL. With it LOW (GPU mode):
  - pin 52 = GC6_FB_EN3V3, a mainboard output (NVIDIA GC6 framebuffer enable). Left unconnected.
  - pin 53 = FBVDD_PWRGD, a mainboard input with a 1M pull-down. Gate UC78 ANDs it with DGPU_PWROK
    (power pin 73, our PWR_GOOD) into ALL_GPWRGD to the APU. Left floating, ALL_GPWRGD would never go high.
  - pin 54 = EXT_SSD2_CLK_REQ#, used only in SSD mode (UC76). Left unconnected.
- So these pins are not SMBus in GPU mode. Change made: R13 is now a fitted 0R from PWR_GOOD to pin 53. R12 is
  removed, pin 52 is NC, and the MXM SMB_CLK/SMB_DAT pins are NC.
- The same switch (UC75) routes DP_A AUX to the eDP mux only when SSD_GPU_SEL is LOW, which confirms the
  descriptor change GPU_PCIE_MUX_SEL = LOW.
- Add a test point on pin 53 (FBVDD_PWRGD) in layout.

### 9. Host PCIe TX AC coupling: done (R20-R35 stay 0R)
- FW16 7040 interface schematic, page 3: the host->module lanes are named PEG_CTX_C_GRX_* (CPU TX after
  the coupling Cap, to GPU RX). The module->host lanes are PEG_CRX_GTX_* (no "_C"). So the mainboard
  AC-couples its own TX, and the module must couple its TX. That matches the adapter: R20-R35 0R
  (host->card) and C10-C25 220 nF (card->host). The capacitors themselves are on sheet 6, which isn't in
  the PDF; the evidence is the net naming.
- Keep R20-R35 as 0402 pads anyway, in case caps are ever needed.

### Questions to send Framework
1. (Answered by the interface schematic: pins 52/53 = GC6_FB_EN3V3 / FBVDD_PWRGD in GPU mode.)
   Still worth asking: what does ALL_GPWRGD gate on the APU side, and does Framework's AMD module tie
   FBVDD_PWRGD to its power-good?
2. (Answered: host TX is AC-coupled on the mainboard, per the PEG_CTX_C_GRX net names.)
3. What voltage and resistor value are the ID0/ID1 pull-ups? (Not in the interface schematic: the
   GPU_B_ID_0/1 nets go to EC sheet 58, which isn't included.)
4. Does the BIOS use the EC's GPU_PRESENT flag (set only for vendor GPU_AMD_R23M) to decide whether to
   offer the internal-panel eDP mux? What does a third-party module need to use it?
5. What link rate and features does the internal panel need on DP_A (lanes, HBR2/HBR3, PSR)?
6. Does the EC cut bay power if the module asserts PROCHOT_N (signal pin 65)? MXM TH_OVERT# requires
   module power off within 500 ms.

### Questions to send X-Vision
1. With PWR_LEVEL pulled low, what power does the card drop to? (MXM requires at least 20% less.)
2. Does the card's VBIOS support eDP on DP_A, and which DP ports does it drive?
   Answered by X-Vision (2026-11-04): "currently only DP is available"; whether eDP is possible is
   uncertain. Still ask which MXM DP ports (A-F) are live, and whether a VBIOS with eDP on DP_A could be
   made.

## Displays (decision: internal panel, with an external option)

### 10. Internal panel
- The FW16 has a real eDP mux (EC `gpio_edp_mux_pwm_sw`). Host software switches it by writing
  SET_GPU_MUX / SET_APU_MUX to EC shared memory (EC function `gpu_smart_access_graphic`, i.e. AMD Smart
  Access Graphics). The EC itself doesn't check the vendor when switching. It sets GPU_PRESENT only for
  GPU_AMD_R23M, which the closed-source BIOS presumably reads.
- Route A, works without firmware changes (recommended baseline): the mux stays on the APU. The iGPU drives
  the panel, and the MXM card renders and copies frames over PCIe (Windows hybrid graphics / Linux PRIME).
  The only requirement is that AMD's driver installs on the X-Vision card.
- Route B, card drives the panel directly through the mux (lower latency, VRR on the panel). Needs all of:
  - The EC to report the module as present: either set the EEPROM vendor byte to GPU_AMD_R23M, which makes
    the laptop treat the card as Framework's RX 7700S (untested side effects), or a custom EC build.
  - The BIOS / AMD driver to accept the switch for this card (question 4). Smart Access Graphics is
    validated per platform, so this is the weakest link.
  - The card's VBIOS to define DP_A as an eDP panel output. X-Vision (2026-11-04): only DP for now, eDP
    uncertain. So route B is unlikely with the stock VBIOS. A plain-DP source may still light some eDP
    panels (same main link), but without panel power sequencing, backlight control or PSR from the GPU;
    that is an experiment, not a plan. Once route A works, dump
    the VBIOS (U5 on the back is probably its flash chip) and read its display-connector table.
    MXM 3.1 sec 3.4.6: eDP is optional for a module, and which ports are eDP is set by the MXM System
    Information Structure, which the laptop's BIOS normally supplies. The FW16 BIOS has none, so the card
    falls back to its VBIOS defaults. That makes the VBIOS check essential for route B.
- The schematic already supports both routes: DP_A, HPD and PNL_* are wired to J3, and
  GPU_PCIE_MUX_SEL is set LOW in the descriptor.

### 11. External displays
- Through the laptop's own USB-C ports: driven by the iGPU, with rendering on the card as in route A.
  Works with no extra hardware.
- Directly from the card: add a connector on the adapter fed from a second MXM DisplayPort (DP_B), on
  the shell's rear cutout. A native DisplayPort/mini-DP needs only AC caps, HPD, AUX and DP_PWR. A USB-C
  port in DP alt mode also needs a PD controller and a mux.
- Not in the schematic yet. Since X-Vision confirms plain DP works (and eDP is uncertain), this is the
  only way the card drives a display directly.
- Shell (2026-11-06): the rear opening is a USB-C port, back middle of the bay. So the no-cutting option is
  USB-C DP alt mode, which needs a PD controller, a lane/orientation mux, VBUS/VCONN supply and SBU/AUX
  routing. Any other port means cutting the shell. VBUS comes out of the 5V_ALW budget (2.5 A), which the
  card may already use in full, so check that first.
- Opening measured in item 6. It spans 2.4-5.65 mm above the standoff, which is the same height band as the
  card, and the card already reaches about to the rear limit of the usable area. So a receptacle may not fit
  behind the card: check the gap between the card edge and the rear wall. A top-mount receptacle on the
  1.2 mm adapter would also sit ~1.2 mm low (board top 1.2 mm vs opening bottom 2.4 mm). Treat USB-C as a
  later revision.
- Still needed: which MXM DP port is live (ask X-Vision).

## MXM 3.1 spec findings (v3.1 r1.0, read 2026-11-03)
- J3 pinout: all 278 pins in the generator match Table 3.2/3.3 (checked by script).
- Lane naming confirmed: PEX_TX = output from the root complex (host), PEX_RX = input to it (Table 3.6).
- AC coupling: DC-blocking caps for PCIe TX and RX, and for every DP lane and AUX, go on the system board
  (sec 3.4.4, 3.4.5). The card has none. C10-C25 and C26-C35 are required.
- Power (Table 3.5): PWR_SRC 7-20 V up to 10 A, never below 6.5 V or above 22 V peak (matches the 6.5 V
  UVLO and SMBJ20A). 5V 2.5 A and 3V3 2.0 A maximum, which the host meets exactly.
- Sequencing (sec 3.4.1-3.4.3): no order needed between rails, but PWR_EN only after all rails are in
  tolerance, PWR_GOOD within 90 ms of PWR_EN, PEX_RST# released only after PWR_GOOD.
  Done: card PWR_EN is now gated by the eFuse PG (R19 wired-AND).
- System-board pull-ups/downs now added: PWR_GOOD 10k (R37), TH_ALERT# (R38), PEX_STD_SW# pull-down
  (R36: 7.15k for a long channel; 147k medium, NC short; try others if link training is marginal).
  Already present: TH_OVERT# (R8), PEX_CLK_REQ# (R5), PRSNT (R6/R7).
- DP_A_HPD: the 100k pull-down is on the module, so R14 is not needed.
- TH_OVERT#: the system must cut module power within 500 ms. Routed to the FW16's PROCHOT_N; whether the
  laptop's EC shuts the bay down on it is unknown.
- TH_PWM: optional fan PWM output from the module. Left unconnected; the F75303 drives the fans.
- PWR_LEVEL (sec 3.4.14): module has a 100k pull-up (open = full power). Pulled low, the module must cut
  power by at least 20% within 50 ms. The spec says the system should pull it low on battery or when
  PWR_SRC could exceed 10 A, exactly the FW16 battery case. Done: U2 (74LVC1G07) drives it from
  GPIO2_EC, with R39 100k pull-down and C44 bypass. The FW EC drives GPIO2_EC with extpower_is_present()
  (any external power), not the ">=180 W" in Framework's ExpansionBay README, once the descriptor sets
  gpio2 = GPIO_FUNC_ACDC.
- Ask X-Vision how much power the card drops to with PWR_LEVEL low (the spec only requires >=20%).
- SMBus (sec 3.4.12): the card's GPU temperature sensor answers at 7-bit 0x4C, 0x4F, 0x2B or 0x19. The
  F75303 (0x4D) sits on a different bus (ALW), so there is no conflict.

## FW16 7040 mainboard interface schematic findings (read 2026-11-04)
Source: FrameworkComputer/Framework-Laptop-16, `Mainboard/Mainboard_Interfaces_Schematic_Framework_Laptop_16_7040_Series.pdf`
(kept locally, not published here). Page 3 is the expansion-bay connector pair: JFXB2 = signal, JFXB1 = power,
both UNIMI FBGCBE057-A-X, pins lettered A1-L8.
- F75303 address 0x4D (page 9): see item 1.
- Pins 52/53/54 and the AUX/SSD-clock switch: see item 8.
- Host TX AC coupling: see item 9.
- The mainboard expects these pull-ups on the module ("GPU/B have PU"). The adapter already has them:
  - ALW I2C (GPU_ALW_CLK/DAT): BSS138 level shifters on the mainboard, pull-ups on the module side
    -> R3/R4 4.7k.
  - GPU_ALERT#: BSS138 shifter, "GPU/B PU 10K +3.3V_AUX" -> R38 10k (TH_ALERT#).
  - DGPU_PWROK (power pin 73): "GPU/B PU 49.9K +3.3V_AUX", 1M pull-down on the mainboard -> R37 10k
    (MXM asks for 10k; both work against the 1M).
  - "GPU/B PU 4.7K +3.3V_AUX, R55" sits by the TH_OVERT# / LCD_EN pins -> R8 10k on PROCHOT_N.
- PEX_RST# to the module (DGPU_PEX_RST#) is AND gate UG6 of PEX_RST# and APU_PCIE0_RST#, with a 100k
  pull-down. Nothing needed on the adapter.
- eDP: the GPU_EDP_TX0-3 / AUX lanes go to the PS8461 mux on sheet 39, which isn't in this PDF. Page 4
  shows coupling caps CV1-CV8 / CV454-455 after the mux (SW_EDP_*_C), toward the panel. Keep C26-C35 on
  the adapter: MXM requires them on the system side, and a second series cap does no harm.
- Not in this PDF: the ID0/ID1 pull-ups (EC sheet 58), the PCIe caps themselves (sheet 6), the eDP mux
  (sheet 39), and what ALL_GPWRGD does on the APU side (sheet 10).

## Forum threads checked (2026-11-04): no answers to the open items
- "FW16 Electrical Specifications (MB/DB Pinout Clarification)" (community.frame.work/t/66338): about
  extended-battery use of VADP_GPU (pin 41) and battery I2C; no staff answers on ID pull-ups, the eDP mux,
  PROCHOT or pins 52/53. Note: VADP_GPU is a feed back into the laptop; the adapter leaves it unused.
- "Expansion Bay Developer Program" (t/35268, staff: nrp): Framework has offered small quantities of
  Expansion Bay -> PCIe "riser boards" on request, which could be a useful bench reference. Staff said
  there was no shareable full schematic for them.

## Original adapter thread (community.frame.work/t/74018, read 2026-11-04, posts 1-292)
JJ-Shapiro's FW16-to-MXM adapter (github.com/JJ-Shapiro/Framework-GPU-to-MXM). Status Oct 2026: no MXM card
ever enumerated as a GPU ("we don't even have a functional design"), work paused. Useful findings:
- **PWR_EN is 1.8 V.** Post 233 (Kieran_Levin, a Framework engineer; staff badge not checked): "PWR_EN is
  powered directly from a 1.8V GPIO on the APU ... do not pull high to 3.3V". Measured 1.7 V (post 230).
  Our R19 passes it straight to the card's PWR_EN: check the MXM PWR_EN input high level, and whether
  the card pulls PWR_EN up to 3.3 V (that would back-drive the APU GPIO through R19). Probably needs a
  1.8 V -> 3.3 V translator. **Done:** U6 SN74LV1T08 (VIH max 1.37 V at 3.3 V VCC, TI SCLS739F) drives the
  card's PWR_EN = host PWR_EN AND eFuse PG; R19 is now a 100k pull-down on the host side.
- PWR_EN is "tied to the internal GPU dynamic power control logic in the bios", which checks the GPU's
  PCI ID (post 233). PEX_RST# comes from an APU GPIO; the SSD resets come from the EC (post 209).
- **x8 reset problem** (Filip, OCuLink board, posts 201-203): with an x8 descriptor, PEX_RST# goes to 0 V
  after BIOS POST, so the device drops off the bus; x4x2 / x4 configs, where reset comes from the EC's
  SSD reset, worked. Likely the BIOS powering down a dGPU it doesn't recognise. **Biggest risk for this
  design.** Fallback added: R41 (0R, fitted) takes PEX_RST# from the host; R42 (0R, DNP) takes it from
  power pin 52 instead (EXT_SSD1_RST# from the EC, active only with an SSD-mode descriptor). Using it costs
  the DP_A AUX (route B), not route A. Whether an SSD-mode descriptor can still run the card at x8 is
  unknown; Filip's working setups were x4.
- Board ID from framework_tool (post 244): (12,12) = DualInterposer, (13,15) = UmaFans,
  (11,15) = SingleInterposer, (15,15) = NoModule. JJ used 330k to GND on both IDs (post 14), and the
  OCuLink board with the same arrangement reads (12,12) (post 245). Supports R1/R2 = 330k (item 7).
- EEPROM: JJ copied his RX 7700S module's .bin onto the adapter EEPROM (post 90); the EC reads it once at
  EC boot (posts 108, 213).
- PCIe: lane order must match; P/N swaps are tolerated (post 173). JJ also had wrong TX/RX direction early on
  (post 58). Six-layer flex, then 4-layer plans. No working link was reported.
- Not discussed: F75303, pins 52/53, eDP mux, PROCHOT, AC caps on the host side.
- A public archived copy of the MXM 3.1 spec is linked in post 292 (web.archive.org, module-store.de).

## Resolved this pass (for reference)
- Fan connector pinout: 1 +12V, 2 SPEED, 3 PWM, 4 GND (`reference/evidence/fw_ref_pcb_fan_pinout.png`).
  The fan's own FPC is numbered the opposite way (`coolermaster_fan_fpc_pinout.png`).
- Fan connector maker and land pattern: Zhejiang Hefeng AFC58-S04FIA-R1, 0.5 mm, lower contact
  (`hefeng_afc58_land_pattern.png`). Verify the nail-pad position before fab.
- TPS25982 package: RGE0024M; pad 25 = IN, pad 26 = GND (`ti_rge0024m_land_pattern.png`).
- F75303M pinout and 2200 pF across each D+/D- pair: see item 1 (FW16 7040 interface schematic p.9).
  0.1 uF bypass on VCC (C45) is standard practice.
