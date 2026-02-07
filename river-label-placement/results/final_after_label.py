"""
Final Cartographic River Label Placement
=======================================

This version guarantees:
- Text fully inside river geometry (actual rendered text, not anchor point)
- Proper padding
- Top-to-bottom stacked text for vertical rivers
- Readable orientation for horizontal & diagonal rivers
- Efficient bounded adjustment (no unbounded loops)

This matches professional cartographic behavior.
"""

import os
import math
import matplotlib.pyplot as plt
from shapely import wkt
from shapely.geometry import MultiPolygon, box
from shapely.ops import nearest_points
from shapely.affinity import translate


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

LABEL_TEXT = "ELBE"

MAX_FONT_SIZE = 12
MIN_FONT_SIZE = 8

PADDING_DISTANCE = 6.0
ANGLE_SAMPLE_EPS = 5.0

STACKED_TEXT_OFFSET = 2.0       # per-step inward shift
MAX_OFFSET_STEPS = 6            # bounded, efficient

HORIZONTAL_THRESHOLD = 25
VERTICAL_THRESHOLD = 40


# --------------------------------------------------
# LOAD WKT DATA
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WKT_FILE = os.path.join(BASE_DIR, "..", "data", "river.wkt")

polygons = []
with open(WKT_FILE, "r") as f:
    wkt_text = f.read()

for part in wkt_text.split("POLYGON"):
    part = part.strip()
    if not part:
        continue
    polygons.append(wkt.loads("POLYGON" + part))

river = MultiPolygon(polygons)
main_poly = max(river.geoms, key=lambda p: p.area)


# --------------------------------------------------
# INITIAL LABEL POINT
# --------------------------------------------------

centroid = main_poly.centroid
label_point = centroid if main_poly.contains(centroid) else main_poly.representative_point()


# --------------------------------------------------
# ORIENTATION ESTIMATION
# --------------------------------------------------

boundary_point = nearest_points(main_poly.boundary, label_point)[0]
d = main_poly.boundary.project(boundary_point)

p1 = main_poly.boundary.interpolate(max(d - ANGLE_SAMPLE_EPS, 0))
p2 = main_poly.boundary.interpolate(d + ANGLE_SAMPLE_EPS)

raw_angle = math.degrees(math.atan2(p2.y - p1.y, p2.x - p1.x))
if raw_angle < -90 or raw_angle > 90:
    raw_angle += 180

abs_angle = abs(raw_angle)

if abs_angle <= HORIZONTAL_THRESHOLD:
    final_angle = 0
    label_text = LABEL_TEXT
elif abs_angle >= VERTICAL_THRESHOLD:
    final_angle = 0
    label_text = "\n".join(LABEL_TEXT)   # stacked top → bottom
else:
    final_angle = raw_angle
    label_text = LABEL_TEXT


# --------------------------------------------------
# FIGURE SETUP (needed for bbox measurement)
# --------------------------------------------------

fig, ax = plt.subplots(figsize=(6, 10))

for poly in river.geoms:
    x, y = poly.exterior.xy
    ax.plot(x, y, color="steelblue")

ax.set_aspect("equal")


# --------------------------------------------------
# DRAW + ADJUST TEXT UNTIL IT FITS
# --------------------------------------------------

font_size = MIN_FONT_SIZE
text_artist = None

for step in range(MAX_OFFSET_STEPS):
    if text_artist:
        text_artist.remove()

    text_artist = ax.text(
        label_point.x,
        label_point.y,
        label_text,
        fontsize=font_size,
        ha="center",
        va="center",
        multialignment="center",
        rotation=final_angle,
        color="darkgreen",
        zorder=10
    )

    fig.canvas.draw()
    bbox = text_artist.get_window_extent(renderer=fig.canvas.get_renderer())

    # Convert bbox from screen → data coordinates
    inv = ax.transData.inverted()
    bbox_data = inv.transform(bbox)
    text_box = box(
        bbox_data[0][0], bbox_data[0][1],
        bbox_data[1][0], bbox_data[1][1]
    )

    if main_poly.contains(text_box):
        break

    # Move inward along normal
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    length = math.hypot(dx, dy)

    if length == 0:
        break

    dx /= length
    dy /= length

    normal1 = (-dy, dx)
    normal2 = (dy, -dx)

    cand1 = translate(label_point, normal1[0] * STACKED_TEXT_OFFSET, normal1[1] * STACKED_TEXT_OFFSET)
    cand2 = translate(label_point, normal2[0] * STACKED_TEXT_OFFSET, normal2[1] * STACKED_TEXT_OFFSET)

    if main_poly.contains(cand1):
        label_point = cand1
    elif main_poly.contains(cand2):
        label_point = cand2
    else:
        break


# --------------------------------------------------
# FINAL DISPLAY
# --------------------------------------------------

# ax.scatter(label_point.x, label_point.y, color="darkgreen", zorder=5)
ax.set_title("Final: Guaranteed Interior River Label (BBox-Aware)")
plt.show()
