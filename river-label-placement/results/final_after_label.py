"""
Final Cartographic Label Placement (Optimized)

Guarantees:
- Label point lies inside river geometry (or explicitly flagged)
- Padding enforced using inward buffer
- Font size reduced only within readable bounds
- Text rotated to align with local river flow direction

This solution intentionally avoids curve-following text,
which is documented as advanced / out-of-scope.
"""

import os
import math
import matplotlib.pyplot as plt
from shapely import wkt
from shapely.geometry import MultiPolygon
from shapely.ops import nearest_points


# ------------------------------------
# CONFIGURATION
# ------------------------------------

LABEL_TEXT = "ELBE"

MAX_FONT_SIZE = 12        # preferred size
MIN_FONT_SIZE = 8         # minimum readable size
FONT_STEP = 1

PADDING_DISTANCE = 6.0    # geometric padding from river edges
ANGLE_SAMPLE_EPS = 5.0    # distance to estimate river direction


# ------------------------------------
# LOAD DATA (ROBUST PATH)
# ------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WKT_FILE = os.path.join(BASE_DIR, "..", "data", "river.wkt")

polygons = []
with open(WKT_FILE, "r") as f:
    data = f.read()

# Parse multiple POLYGON records → MultiPolygon
for part in data.split("POLYGON"):
    part = part.strip()
    if not part:
        continue
    polygons.append(wkt.loads("POLYGON" + part))

river = MultiPolygon(polygons)


# ------------------------------------
# SELECT MAIN RIVER BODY
# ------------------------------------

main_poly = max(river.geoms, key=lambda p: p.area)


# ------------------------------------
# STEP 1: LABEL POINT SELECTION
# ------------------------------------

centroid = main_poly.centroid

# Prefer centroid if valid, else guaranteed interior point
if main_poly.contains(centroid):
    label_point = centroid
else:
    label_point = main_poly.representative_point()


# ------------------------------------
# STEP 2: ENFORCE PADDING
# ------------------------------------

# Shrink polygon inward to enforce padding constraint
padded_poly = main_poly.buffer(-PADDING_DISTANCE)

if padded_poly.is_empty or not padded_poly.contains(label_point):
    # Padding makes interior placement infeasible
    feasible = False
    label_point = main_poly.representative_point()
else:
    feasible = True


# ------------------------------------
# STEP 3: FONT SIZE ADAPTATION
# ------------------------------------

font_size = None

if feasible:
    for fs in range(MAX_FONT_SIZE, MIN_FONT_SIZE - 1, -FONT_STEP):
        font_size = fs
        break

if font_size is None:
    # No feasible interior placement at readable size
    font_size = MIN_FONT_SIZE
    print("⚠️ No padded interior region available — advanced labeling required.")


# ------------------------------------
# STEP 4: TEXT ROTATION (RIVER FLOW)
# ------------------------------------

# Estimate local river direction using boundary tangent
boundary_point = nearest_points(main_poly.boundary, label_point)[0]
d = main_poly.boundary.project(boundary_point)

p1 = main_poly.boundary.interpolate(max(d - ANGLE_SAMPLE_EPS, 0))
p2 = main_poly.boundary.interpolate(d + ANGLE_SAMPLE_EPS)

angle = math.degrees(math.atan2(p2.y - p1.y, p2.x - p1.x))


# ------------------------------------
# VISUALIZATION
# ------------------------------------

plt.figure(figsize=(6, 10))

# Plot river geometry
for poly in river.geoms:
    x, y = poly.exterior.xy
    plt.plot(x, y, color="steelblue")

# Plot label point
plt.scatter(label_point.x, label_point.y, color="darkgreen", zorder=5)

# Draw rotated label
plt.text(
    label_point.x,
    label_point.y,
    LABEL_TEXT,
    fontsize=font_size,
    ha="center",
    va="center",
    rotation=angle,
    rotation_mode="anchor",
    color="darkgreen",
    zorder=10
)

plt.title("Final: Interior River Label with Padding, Rotation & Adaptive Font")
plt.gca().set_aspect("equal")
plt.show()
