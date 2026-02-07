from shapely import wkt
from shapely.geometry import MultiPolygon
from shapely.ops import nearest_points
import matplotlib.pyplot as plt

LABEL_TEXT = "ELBE"
FONT_SIZE = 12
EPSILON = 1.0  # small inward shift to avoid boundary placement

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
# 3. Compute centroid
# ------------------------------------
centroid = main_poly.centroid

# ------------------------------------
# 4. Final label placement logic
# ------------------------------------
if main_poly.contains(centroid):
    # Best case: centroid is already valid
    label_point = centroid
else:
    # Find nearest point on polygon to centroid
    boundary_point = nearest_points(main_poly, centroid)[0]

    # Move slightly inward to guarantee interior placement
    inner_poly = main_poly.buffer(-EPSILON)

    if not inner_poly.is_empty:
        label_point = inner_poly.representative_point()
    else:
        # Robust fallback (always inside)
        label_point = main_poly.representative_point()

# ------------------------------------
# 5. Visualization (AFTER)
# ------------------------------------
plt.figure(figsize=(6, 10))

# Plot river geometry
for poly in river.geoms:
    x, y = poly.exterior.xy
    plt.plot(x, y, color="steelblue")

# Plot label point
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
plt.title("AFTER: Centroid-Aware, Guaranteed-Interior Label Placement")
plt.show()
