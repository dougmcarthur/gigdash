# GigDash wedge enclosure

A stage-wedge cabinet holding both portable monitors and the Pi: the front
face shows the audience display, the sloped top tilts the performer display
back like a teleprompter/foldback wedge.

Regenerate the model after tweaking parameters in
`tools/enclosure_model.py`:

```sh
pip install trimesh manifold3d shapely matplotlib
python3 tools/enclosure_model.py
```

Outputs: `gigdash-wedge.stl` (open in any 3D viewer / slicer) and the
`view-*.png` renders.

## Key dimensions (as modeled)

| Parameter | Value |
|---|---|
| Outer footprint | 468 mm wide × 340 mm deep |
| Front height | 320 mm; rear height 100 mm |
| Slope angle | **32.9°** from horizontal (panel 405 mm long) |
| Panel stock | 9 mm lightweight plywood (poplar or baltic birch) |
| Screen windows | 345 × 225 mm (≈7 mm lip over the monitor bezel) |
| Monitor allowance | 360 × 245 mm — **measure your monitors first!** |
| Port clearance | 45 mm each side of the monitors (`SIDE_CLEAR`) for 180° USB-C / mini-HDMI adapters — **measure adapter protrusion too** |
| Estimated weight | ≈3 kg bare (4.3 L of wood), ~5 kg loaded |

## Cut list (9 mm ply)

| Qty | Panel | Size (mm) | Notes |
|---|---|---|---|
| 2 | Sides | trapezoid: 340 base, 320 front, 100 rear | shape-defining; 110×35 hand-hole, center 120 from front / 172 up |
| 1 | Front | 450 × 311 | 345×225 window, centered |
| 1 | Slope | 450 × 405 | 345×225 window, centered |
| 1 | Bottom | 450 × 340 | |
| 1 | Back | 450 × 91 | 3 vent slots 240×12, Ø32 grommet hole |
| 2 | Transit lids | 375 × 255 (6 mm ply) | cover the windows in transport; see below |
| 6 | Corner cleats | 15 × 15 softwood battens | 2× ~322 (bottom/side), 2× ~272 (front/side), 2× ~420 (bottom front + back) |
| 2 | Slope ribs | 30 × 345 (9 mm ply) | glued under the slope flanking its window |

Front/back/bottom/slope sit *between* the side panels (hence 402 wide).

## Assembly notes

- **Joints**: glue + 18ga brads or 3.5mm screws into the side-panel edges.
  Glue is the structure; fasteners are just clamps while it cures — don't
  over-screw. The corner cleats go in glued along the bottom and front
  interior joints (screw through them into both panels). Butt joints are
  fine; for clean seams, bevel the slope panel's mating
  edges at 33° (top, meets front) — or leave square and sand flush.
- **Slope stiffening**: glue the two 30 mm ribs to the underside of the
  sloped panel along the window's side edges before assembly — they guard
  against the classic stage accident (a boot or elbow on the wedge). If
  you expect rough handling, cutting the slope panel from 12 mm stock
  instead is the belt-and-braces option.
- **Monitors**: drop in behind each window, cushion the bezel with foam
  weatherstrip tape, retain with screwed-on wood strips (no glue — you
  want them removable). The windows leave a ~7 mm lip all around.
- **Pi**: mount on standoffs to the bottom panel near the back, by the
  vents and grommet. Both HDMI cables and monitor USB-C power route
  internally; only power cords exit the grommet.
- **Ventilation**: passive — rear slots + the grommet give airflow; the
  Pi 4 in kiosk duty won't need a fan.
- **Finish**: round the slope/front meeting edge, matte black paint or
  Danish oil. Rubber feet underneath so it doesn't slide on stage.
- Optional: a hinged or screwed rear hatch instead of a fixed back panel
  for easier service.

## Portability

- **Hand-holes** (modeled): one rounded 110×35 slot per side panel —
  two-handed carry, or one-handed against the hip. Sand the edges well;
  optionally line with split rubber edge trim.
- **Transit lids** (modeled, `gigdash-lids.stl`): two 6 mm ply covers,
  foam-lined (5 mm adhesive foam), overlapping each window by 15 mm per
  side. Retain with 4 pairs of Ø10×3 rare-earth magnets per lid — epoxy
  them into shallow recesses in the lid corners and the matching face.
  They protect the glass in the car and stack flat.
- **Shoulder strap**: two D-rings screwed to one side panel, clip-on
  padded strap (hands stay free for guitar + pedalboard).
- Deliberately no wheels/telescoping handle: loaded weight is ~4.5 kg.
  For full-rig load-ins, strap the box to a folding hand truck instead.
