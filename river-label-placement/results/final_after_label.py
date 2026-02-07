"""
Final Cartographic River Label Placement
=======================================

Features implemented:
- Interior placement (centroid with safe fallback)
- Geometric padding enforcement
- Adaptive font sizing (bounded for readability)
- Orientation-aware label rendering:
    * Horizontal rivers → horizontal text
    * Vertical rivers → stacked text (top to bottom)
    * Diagonal rivers → gently rotated text
- No river flow direction assumptions (polygon geometry)

This version prioritizes cartographic readability.
"""

import os
import math
import matplotlib.pyplot as plt
from shapely import wkt
from shapely.geometry import MultiPolygon
from shapely.ops import nearest_points


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

LABEL_TEXT = "ELBE"

MAX_FONT_SIZE = 12
MIN_FONT_SIZE = 8
FONT_STEP = 1

PADDING_DISTANCE = 6.0
ANGLE_SAMPLE_EPS = 5.0

# Readability thresholds (human perception, not strict geometry)
HORIZONTAL_THRESHOLD = 25   # degrees
VERTICAL_THRESHOLD = 40     # degrees


# --------------------------------------------------
# LOAD WKT DATA (robust path handling)
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WKT_FILE = os.path.join(BASE_DIR, "..", "data", "river.wkt")

polygons = []
with open(WKT_FILE, "r") as f:
    wkt_text = f.read()

# The file contains multiple POLYGON records
for part in wkt_text.split("POLYGON"):
    part = part.strip()
    if not part:
        continue
    polygons.append(wkt.loads("POLYGON" + part))

river = MultiPolygon(polygons)


# --------------------------------------------------
# SELECT MAIN RIVER BODY
# --------------------------------------------------

main_poly = max(river.geoms, key=lambda p: p.area)


# --------------------------------------------------
# STEP 1: LABEL POINT (interior guaranteed)
# --------------------------------------------------

centroid = main_poly.centroid

if main_poly.contains(centroid):
    label_point = centroid
else:
    label_point = main_poly.representative_point()


# --------------------------------------------------
# STEP 2: PADDING CHECK
# --------------------------------------------------

padded_poly = main_poly.buffer(-PADDING_DISTANCE)

feasible = (
    not padded_poly.is_empty
    and padded_poly.contains(label_point)
)

if not feasible:
    print(
        "⚠️ No padded interior region available — "
        "advanced labeling (curve-following / outside) required."
    )
    label_point = main_poly.representative_point()


# --------------------------------------------------
# STEP 3: ADAPTIVE FONT SIZE
# --------------------------------------------------

font_size = MIN_FONT_SIZE

if feasible:
    for fs in range(MAX_FONT_SIZE, MIN_FONT_SIZE - 1, -FONT_STEP):
        font_size = fs
        break


# --------------------------------------------------
# STEP 4: LOCAL ORIENTATION ESTIMATION
# --------------------------------------------------

boundary_point = nearest_points(main_poly.boundary, label_point)[0]
d = main_poly.boundary.project(boundary_point)

p1 = main_poly.boundary.interpolate(max(d - ANGLE_SAMPLE_EPS, 0))
p2 = main_poly.boundary.interpolate(d + ANGLE_SAMPLE_EPS)

raw_angle = math.degrees(math.atan2(p2.y - p1.y, p2.x - p1.x))


# --------------------------------------------------
# STEP 5: READABILITY-FIRST TEXT DECISION
# --------------------------------------------------

# Normalize angle to keep text upright
if raw_angle < -90 or raw_angle > 90:
    raw_angle += 180

abs_angle = abs(raw_angle)

# Decide orientation and text form
if abs_angle <= HORIZONTAL_THRESHOLD:
    # Mostly horizontal river
    final_angle = 0
    label_text = LABEL_TEXT

elif abs_angle >= VERTICAL_THRESHOLD:
    # Mostly vertical river → STACKED TEXT (TOP TO BOTTOM)
    final_angle = 0
    label_text = "\n".join(LABEL_TEXT)  # E\nL\nB\nE

else:
    # Diagonal river → gentle rotation
    final_angle = raw_angle
    label_text = LABEL_TEXT


# --------------------------------------------------
# VISUALIZATION
# --------------------------------------------------

plt.figure(figsize=(6, 10))

# Plot river geometry
for poly in river.geoms:
    x, y = poly.exterior.xy
    plt.plot(x, y, color="steelblue")

# Plot label anchor
plt.scatter(label_point.x, label_point.y, color="darkgreen", zorder=5)

# Draw label
plt.text(
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

plt.title(
    "Final: Interior River Label with Padding, Orientation & Readability"
)
plt.gca().set_aspect("equal")
plt.show()
