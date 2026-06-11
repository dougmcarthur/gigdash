#!/usr/bin/env python3
"""Parametric 3D model of the GigDash wedge enclosure.

Generates docs/enclosure/gigdash-wedge.stl plus rendered PNG views.
All dimensions in mm; tweak the parameters below and re-run.

Requires: pip install trimesh manifold3d matplotlib
"""
import numpy as np
import trimesh
from pathlib import Path

# ---------------------------------------------------------------- parameters
T = 9.0          # panel thickness (9mm lightweight ply)
D = 340.0        # outer depth (front to back)
HF = 320.0       # front face height (audience side)
HR = 100.0       # rear height (performer side)

# Monitor: CNBANAN/ZQ P160A17 16" 3:2 -- MEASURE YOURS and adjust.
MON_W, MON_H = 360.0, 245.0      # monitor outer size incl. bezel
WIN_W, WIN_H = 345.0, 225.0      # window cutout (smaller => retaining lip)

# Clearance between each monitor side edge and the inner wall, for the
# side-facing ports with 180-degree USB-C / mini-HDMI adapters plugged in.
# Measure: adapter protrusion off the bezel edge, plus ~10mm of slack.
SIDE_CLEAR = 45.0
W = MON_W + 2 * (SIDE_CLEAR + T)  # outer width (458 with defaults)

VENT_W, VENT_H, VENT_N = 240.0, 12.0, 3   # rear vent slots
GROMMET_R = 16.0                          # rear cable grommet radius

# Hand-holes through both side panels (rounded slot, sized for gloved hand)
SLOT_LEN, SLOT_H = 110.0, 35.0            # overall length x height
SLOT_Y, SLOT_Z = 120.0, 172.5             # slot center (depth, height)

# Transit lids: 6mm ply covers overlapping each screen window by 15mm/side
LID_T = 6.0
LID_W, LID_H = WIN_W + 30, WIN_H + 30

OUT = Path(__file__).resolve().parent.parent / "docs" / "enclosure"

# Slope geometry
RUN, RISE = D, HF - HR
SLOPE_LEN = float(np.hypot(RUN, RISE))
SLOPE_DEG = float(np.degrees(np.arctan2(RISE, RUN)))


def box(size, translate=(0, 0, 0), transform=None):
    m = trimesh.creation.box(extents=size)
    m.apply_translation(np.array(size) / 2.0)  # corner at origin
    if transform is not None:
        m.apply_transform(transform)
    m.apply_translation(translate)
    return m


def slope_basis():
    """Frame for the sloped panel: X=width, Y=downhill, Z=outward normal."""
    u = np.array([0, RUN, -RISE]) / SLOPE_LEN          # downhill
    n = np.array([0, RISE, RUN]) / SLOPE_LEN           # outward (up/back)
    x = np.array([1, 0, 0])
    tf = np.eye(4)
    tf[:3, :3] = np.column_stack([x, u, n])
    return tf, u, n


def build():
    panels = []
    # Two trapezoid side panels (full profile: they carry the shape)
    profile = np.array([[0, 0], [D, 0], [D, HR], [0, HF]])  # (y, z)
    from shapely.geometry import Polygon
    side = trimesh.creation.extrude_polygon(Polygon(profile), T)  # extruded in +z
    tf = np.eye(4)  # map extrusion (x=y, y=z, z=x): rotate axes
    tf[:3, :3] = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]])
    left = side.copy()
    left.apply_transform(tf)
    right = left.copy()
    right.apply_translation([W - T, 0, 0])
    panels += [left, right]

    inner_w = W - 2 * T
    panels.append(box((inner_w, D, T), (T, 0, 0)))                    # bottom
    panels.append(box((inner_w, T, HF - T), (T, 0, T)))               # front
    panels.append(box((inner_w, T, HR - T), (T, D - T, T)))           # back

    stf, u, n = slope_basis()
    slope = box((inner_w, SLOPE_LEN, T), transform=stf)
    slope.apply_translation(np.array([T, 0, HF]) - n * T)             # top edge
    panels.append(slope)

    # 15x15 softwood corner cleats along the main interior joints
    C = 15.0
    for x in (T, W - T - C):
        panels.append(box((C, D - 2 * T, C), (x, T, T)))              # bottom/side
        panels.append(box((C, C, HF - 2 * T - 30), (x, T, T + C)))    # front/side
    panels.append(box((inner_w - 2 * C, C, C), (T + C, T, T)))        # bottom/front
    panels.append(box((inner_w - 2 * C, C, C), (T + C, D - T - C, T)))  # bottom/back

    # 30mm ply stiffener ribs under the slope, flanking the window
    for x in (25.0, W - 55.0):
        rib = box((30.0, SLOPE_LEN - 60.0, T), transform=stf)
        rib.apply_translation(np.array([x, 0, HF]) + u * 30.0 - n * 2 * T)
        panels.append(rib)

    shell = trimesh.boolean.union(panels, engine="manifold")

    cuts = []
    # Front window, centered on front face
    cuts.append(box((WIN_W, 3 * T, WIN_H),
                    ((W - WIN_W) / 2, -T, T + (HF - T - WIN_H) / 2)))
    # Slope window, centered on the sloped face
    swin = box((WIN_W, WIN_H, 4 * T), transform=stf)
    s0 = (SLOPE_LEN - WIN_H) / 2
    swin.apply_translation(np.array([(W - WIN_W) / 2, 0, HF]) + u * s0 - n * 2 * T)
    cuts.append(swin)
    # Rear vent slots
    for i in range(VENT_N):
        z = 22 + i * (VENT_H + 14)
        cuts.append(box((VENT_W, 3 * T, VENT_H), ((W - VENT_W) / 2, D - 2 * T, z)))
    # Rear cable grommet
    g = trimesh.creation.cylinder(radius=GROMMET_R, height=3 * T)
    g.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
    g.apply_translation([W - 70, D - T / 2, 55])
    cuts.append(g)
    # Hand-holes: one rounded slot through each side (single full-width cut;
    # the interior at this position is empty air, so only the sides lose wood)
    r = SLOT_H / 2
    slot = [box((W + 20, SLOT_LEN - SLOT_H, SLOT_H),
                (-10, SLOT_Y - (SLOT_LEN - SLOT_H) / 2, SLOT_Z - r))]
    for end in (-1, 1):
        c = trimesh.creation.cylinder(radius=r, height=W + 20)
        c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
        c.apply_translation([W / 2, SLOT_Y + end * (SLOT_LEN - SLOT_H) / 2, SLOT_Z])
        slot.append(c)
    cuts += slot

    return trimesh.boolean.difference(
        [shell, trimesh.boolean.union(cuts, engine="manifold")], engine="manifold")


def screens():
    """Render-only stand-ins for the two monitors sitting behind the windows."""
    stf, u, n = slope_basis()
    front = box((MON_W, 4.0, MON_H),
                ((W - MON_W) / 2, T + 0.5, T + (HF - T - MON_H) / 2))
    s0 = (SLOPE_LEN - MON_H) / 2
    sloped = box((MON_W, MON_H, 4.0), transform=stf)
    sloped.apply_translation(
        np.array([(W - MON_W) / 2, 0, HF]) + u * s0 - n * (T + 4.5))
    return [front, sloped]


def lids(offset=0.0):
    """Transit lids covering both windows, optionally floated off the faces."""
    stf, u, n = slope_basis()
    front = box((LID_W, LID_T, LID_H),
                ((W - LID_W) / 2, -LID_T - offset, T + (HF - T - WIN_H) / 2 - 15))
    s0 = (SLOPE_LEN - WIN_H) / 2 - 15
    sloped = box((LID_W, LID_H, LID_T), transform=stf)
    sloped.apply_translation(
        np.array([(W - LID_W) / 2, 0, HF]) + u * s0 + n * offset)
    return [front, sloped]


def render(mesh, views, extra=()):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    parts = [(mesh, np.array([0.82, 0.70, 0.48]))]          # plywood-ish
    parts += [(s, np.array([0.10, 0.11, 0.14])) for s in screens()]
    parts += [(m, np.array([0.72, 0.58, 0.38])) for m in extra]
    tris_list, colors_list = [], []
    light = np.array([0.4, -0.55, 0.73])
    for part, base in parts:
        normals = part.triangles_cross
        normals = normals / (np.linalg.norm(normals, axis=1, keepdims=True) + 1e-9)
        shade = np.clip(normals @ light, -1, 1) * 0.5 + 0.5
        tris_list.append(part.triangles)
        colors_list.append(np.clip(base * (0.45 + 0.55 * shade[:, None]), 0, 1))
    tris = np.vstack(tris_list)
    colors = np.vstack(colors_list)

    for name, (elev, azim) in views.items():
        fig = plt.figure(figsize=(11, 8.5), dpi=130)
        ax = fig.add_subplot(111, projection="3d")
        pc = Poly3DCollection(tris, facecolors=colors, edgecolors="none")
        ax.add_collection3d(pc)
        c, r = mesh.bounds.mean(axis=0), mesh.extents.max() * 0.62
        ax.set_xlim(c[0] - r, c[0] + r)
        ax.set_ylim(c[1] - r, c[1] + r)
        ax.set_zlim(0, 2 * r * 0.75)
        ax.view_init(elev=elev, azim=azim)
        ax.set_axis_off()
        ax.set_box_aspect((1, 1, 0.75))
        fig.tight_layout(pad=0)
        fig.savefig(OUT / f"view-{name}.png", facecolor="white")
        plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    mesh = build()
    mesh.export(OUT / "gigdash-wedge.stl")
    print(f"slope: {SLOPE_DEG:.1f} deg from horizontal, panel {SLOPE_LEN:.0f}mm long")
    print(f"watertight: {mesh.is_watertight}, volume: {mesh.volume / 1e6:.2f} L of wood")
    lid_meshes = lids()
    trimesh.util.concatenate(lid_meshes).export(OUT / "gigdash-lids.stl")
    render(mesh, {
        "front-audience": (18, -65),
        "rear-performer": (32, 115),
        "side-profile": (2, 0),
    })
    render(mesh, {"transit-lids": (18, -65)}, extra=lids(offset=70))
    print("wrote:", *[p.name for p in sorted(OUT.iterdir())])
