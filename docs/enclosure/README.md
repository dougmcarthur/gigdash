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
| Outer footprint | 420 mm wide × 340 mm deep |
| Front height | 320 mm; rear height 100 mm |
| Slope angle | **32.9°** from horizontal (panel 405 mm long) |
| Panel stock | 9 mm lightweight plywood (poplar or baltic birch) |
| Screen windows | 345 × 225 mm (≈7 mm lip over the monitor bezel) |
| Monitor allowance | 360 × 245 mm — **measure your monitors first!** |
| Estimated weight | ≈2.5–3 kg bare (3.9 L of wood), ~4.5 kg loaded |

## Cut list (9 mm ply)

| Qty | Panel | Size (mm) | Notes |
|---|---|---|---|
| 2 | Sides | trapezoid: 340 base, 320 front, 100 rear | the shape-defining pieces |
| 1 | Front | 402 × 311 | 345×225 window, centered |
| 1 | Slope | 402 × 405 | 345×225 window, centered |
| 1 | Bottom | 402 × 340 | |
| 1 | Back | 402 × 91 | 3 vent slots 240×12, Ø32 grommet hole |

Front/back/bottom/slope sit *between* the side panels (hence 402 wide).

## Assembly notes

- **Joints**: glue + 18ga brads or 3.5mm screws into the side-panel edges.
  Butt joints are fine; for clean seams, bevel the slope panel's mating
  edges at 33° (top, meets front) — or leave square and sand flush.
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
- Optional: hand-hole in each side panel for carrying; a hinged or
  screwed rear hatch instead of a fixed back panel for easier service.
