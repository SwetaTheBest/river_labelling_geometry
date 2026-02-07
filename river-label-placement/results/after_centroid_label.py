from shapely import wkt
from shapely.geometry import MultiPolygon
import matplotlib.pyplot as plt

LABEL_TEXT = "ELBE"
FONT_SIZE = 12

# Try multiple paddings (large → small)
PADDING_CANDIDATES = [150, 100, 60, 30, 10]

# ------------------------------------
# 1. Load river geometry
# ------------------------------------
polygons = []

with open("river.wkt") as f:
    data = f.read()

for part in data.split("POLYGON"):
    part = part.strip()
    if not part:
        continue
    polygons.append(wkt.loads("POLYGON" + part))

river = MultiPolygon(polygons)

# ------------------------------------
# 2. Choose main river polygon
# ------------------------------------
main_poly = max(river.geoms, key=lambda p: p.area)

# ------------------------------------
# 3. Find safe label position
# ------------------------------------
label_point = None
used_padding = None

for padding in PADDING_CANDIDATES:
    candidate = main_poly.buffer(-padding)
    if candidate.is_empty:
        continue

    candidate_point = candidate.centroid

    # IMPORTANT: verify it is inside original polygon
    if main_poly.contains(candidate_point):
        label_point = candidate_point
        used_padding = padding
        inner_poly = candidate
        break

# Fallback: centroid of original polygon
if label_point is None:
    label_point = main_poly.centroid
    inner_poly = None
    used_padding = 0

print("Used padding:", used_padding)

# ------------------------------------
# 4. AFTER visualization
# ------------------------------------
plt.figure(figsize=(6, 10))

# Plot all river parts
for poly in river.geoms:
    x, y = poly.exterior.xy
    plt.plot(x, y, color="steelblue")

# Plot inner safe area (debug)
if inner_poly is not None and inner_poly.geom_type == "Polygon":
    ix, iy = inner_poly.exterior.xy
    plt.plot(ix, iy, color="green", linestyle="--", alpha=0.6)

# Plot label
plt.scatter(label_point.x, label_point.y, color="darkgreen", zorder=5)
plt.text(
    label_point.x,
    label_point.y,
    LABEL_TEXT,
    fontsize=FONT_SIZE,
    ha="center",
    va="center",
    color="darkgreen"
)

plt.gca().set_aspect("equal")
plt.title("AFTER: Geometry-Aware Label Placement (Validated)")
plt.show()
