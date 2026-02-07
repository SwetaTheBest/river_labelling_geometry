from shapely import wkt
from shapely.geometry import MultiPolygon
import matplotlib.pyplot as plt

# -------------------------
# 1. Load river geometry
# -------------------------
polygons = []

with open("river.wkt") as f:
    data = f.read()

for part in data.split("POLYGON"):
    part = part.strip()
    if not part:
        continue
    polygons.append(wkt.loads("POLYGON" + part))

river = MultiPolygon(polygons)

print(river.geom_type, len(river.geoms))

# -------------------------
# 2. BEFORE: visualize river
# -------------------------
plt.figure(figsize=(8, 10))
for poly in river.geoms:
    x, y = poly.exterior.xy
    plt.plot(x, y, color="steelblue")

plt.gca().set_aspect("equal")
plt.title("River Geometry – BEFORE")
plt.show()

# -------------------------
# 3. BEFORE: centroid label
# -------------------------
main_poly = max(river.geoms, key=lambda p: p.area)
centroid = main_poly.centroid

plt.figure(figsize=(8, 10))
for poly in river.geoms:
    x, y = poly.exterior.xy
    plt.plot(x, y, color="steelblue")

plt.text(
    centroid.x,
    centroid.y,
    "ELBE",
    fontsize=12,
    ha="center",
    va="center",
    color="red"
)

plt.scatter(centroid.x, centroid.y, color="red")
plt.gca().set_aspect("equal")
plt.title("BEFORE: Centroid-Based Label Placement")
plt.show()
