from shapely import wkt
from shapely.geometry import MultiPolygon
import matplotlib.pyplot as plt

# ------------------------------------
# 1. Load river geometry from WKT file
# ------------------------------------
polygons = []

with open("river.wkt") as f:
    data = f.read()

# The file contains multiple POLYGON definitions
for part in data.split("POLYGON"):
    part = part.strip()
    if not part:
        continue
    poly = wkt.loads("POLYGON" + part)
    polygons.append(poly)

river = MultiPolygon(polygons)

print("Geometry type:", river.geom_type)
print("Number of polygons:", len(river.geoms))

# ------------------------------------
# 2. BEFORE: visualize river only
# ------------------------------------
plt.figure(figsize=(6, 10))

for poly in river.geoms:
    x, y = poly.exterior.xy
    plt.plot(x, y, color="steelblue")

plt.gca().set_aspect("equal")
plt.title("BEFORE: River Geometry (No Label)")
plt.show()

# ------------------------------------
# 3. BEFORE: naive centroid-based label
# ------------------------------------
main_poly = max(river.geoms, key=lambda p: p.area)
centroid = main_poly.centroid

plt.figure(figsize=(6, 10))

# Plot river again
for poly in river.geoms:
    x, y = poly.exterior.xy
    plt.plot(x, y, color="steelblue")

# Plot centroid and label
plt.scatter(centroid.x, centroid.y, color="red", zorder=5)
plt.text(
    centroid.x,
    centroid.y,
    "ELBE",
    fontsize=12,
    ha="center",
    va="center",
    color="red"
)

plt.gca().set_aspect("equal")
plt.title("BEFORE: Naive Centroid-Based Label Placement")
plt.show()
