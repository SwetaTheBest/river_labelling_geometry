def place_river_label(wkt_text):
    """
    Takes WKT text and returns a matplotlib Figure
    with cartographically-correct river label placement.
    """

    import math
    import matplotlib.pyplot as plt
    from shapely import wkt
    from shapely.geometry import MultiPolygon, box
    from shapely.ops import nearest_points
    from shapely.affinity import translate

    # ---------------- CONFIG ----------------
    LABEL_TEXT = "ELBE"
    PADDING_DISTANCE = 6.0
    ANGLE_SAMPLE_EPS = 5.0
    STACKED_TEXT_OFFSET = 2.0
    MAX_OFFSET_STEPS = 6
    HORIZONTAL_THRESHOLD = 25
    VERTICAL_THRESHOLD = 40

    # ---------------- LOAD WKT ----------------
    polygons = []
    for part in wkt_text.split("POLYGON"):
        part = part.strip()
        if part:
            polygons.append(wkt.loads("POLYGON" + part))

    river = MultiPolygon(polygons)
    main_poly = max(river.geoms, key=lambda p: p.area)

    # ---------------- LABEL POINT ----------------
    centroid = main_poly.centroid
    label_point = centroid if main_poly.contains(centroid) else main_poly.representative_point()

    # ---------------- ORIENTATION ----------------
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
        label_text = "\n".join(LABEL_TEXT)
    else:
        final_angle = raw_angle
        label_text = LABEL_TEXT

    # ---------------- PLOT ----------------
    fig, ax = plt.subplots(figsize=(6, 10))
    for poly in river.geoms:
        x, y = poly.exterior.xy
        ax.plot(x, y, color="steelblue")

    ax.set_aspect("equal")

    # ---------------- BBOX-AWARE PLACEMENT ----------------
    text_artist = None

    for _ in range(MAX_OFFSET_STEPS):
        if text_artist:
            text_artist.remove()

        text_artist = ax.text(
            label_point.x,
            label_point.y,
            label_text,
            fontsize=10,
            ha="center",
            va="center",
            multialignment="center",
            rotation=final_angle,
            color="darkgreen",
            zorder=10
        )

        fig.canvas.draw()
        bbox = text_artist.get_window_extent(fig.canvas.get_renderer())
        inv = ax.transData.inverted()
        bbox_data = inv.transform(bbox)
        text_box = box(
            bbox_data[0][0], bbox_data[0][1],
            bbox_data[1][0], bbox_data[1][1]
        )

        if main_poly.contains(text_box):
            break

        dx = p2.x - p1.x
        dy = p2.y - p1.y
        length = math.hypot(dx, dy)
        if length == 0:
            break

        dx /= length
        dy /= length
        normals = [(-dy, dx), (dy, -dx)]

        moved = False
        for nx, ny in normals:
            candidate = translate(label_point, nx * STACKED_TEXT_OFFSET, ny * STACKED_TEXT_OFFSET)
            if main_poly.contains(candidate):
                label_point = candidate
                moved = True
                break
        if not moved:
            break

    ax.set_title("Cartographic River Label Placement")
    return fig
