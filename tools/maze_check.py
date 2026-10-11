import math, os, xml.etree.ElementTree as ET

path = os.path.expanduser(
    "~/ardu_ws/install/ardupilot_gz_gazebo/share/ardupilot_gz_gazebo/worlds/maze.sdf")
root = ET.parse(path).getroot()

def pose(el):
    p = el.find("pose") if el is not None else None
    if p is None or not p.text:
        return (0.0, 0.0, 0.0)
    v = [float(t) for t in p.text.split()]
    yaw = v[5]
    if p.get("degrees") == "true":
        yaw = math.radians(yaw)
    return (v[0], v[1], yaw)

def compose(a, b):
    c, s = math.cos(a[2]), math.sin(a[2])
    return (a[0] + c*b[0] - s*b[1], a[1] + s*b[0] + c*b[1], a[2] + b[2])

walls = []
for model in root.iter("model"):
    m = pose(model)
    for link in model.findall("link"):
        l = compose(m, pose(link))
        for col in link.findall("collision"):
            box = col.find("geometry/box/size")
            if box is None:
                continue
            sx, sy, sz = [float(t) for t in box.text.split()]
            if sx > 50:
                continue
            w = compose(l, pose(col))
            walls.append((w, sx, sy))

def hit(x, y, margin=0.35):
    for (cx, cy, yaw), sx, sy in walls:
        dx, dy = x - cx, y - cy
        c, s = math.cos(-yaw), math.sin(-yaw)
        lx, ly = c*dx - s*dy, s*dx + c*dy
        if abs(lx) <= sx/2 + margin and abs(ly) <= sy/2 + margin:
            return True
    return False

def free_dist(x0, y0, dx, dy, maxd=15.0):
    n = math.hypot(dx, dy); dx, dy = dx/n, dy/n
    d = 0.0
    while d < maxd:
        if hit(x0 + dx*d, y0 + dy*d):
            return d
        d += 0.05
    return maxd

print("walls:", len(walls))
for (cx, cy, yaw), sx, sy in walls:
    print("  centre (%.2f, %.2f) size %.1f x %.1f yaw %.0f deg"
          % (cx, cy, sx, sy, math.degrees(yaw)))
print("free distance from (0,0): +x %.2f  -x %.2f  +y %.2f  -y %.2f" % (
    free_dist(0, 0, 1, 0), free_dist(0, 0, -1, 0),
    free_dist(0, 0, 0, 1), free_dist(0, 0, 0, -1)))
for name, tx, ty in [("variant 34 (-4.0,-1.1)", -4.0, -1.1),
                     ("opposite  (+4.0,+1.1)", 4.0, 1.1),
                     ("(+4.0,-1.1)", 4.0, -1.1), ("(-4.0,+1.1)", -4.0, 1.1)]:
    d = free_dist(0, 0, tx, ty)
    print("%s: distance to target %.2f, free along line %.2f -> %s" % (
        name, math.hypot(tx, ty), d,
        "FREE" if d >= math.hypot(tx, ty) else "BLOCKED"))
print("target (-4,-1.1) on a wall (margin 0):", hit(-4, -1.1, 0.0))
print("target (-4,-1.1) within 0.35 m of a wall:", hit(-4, -1.1, 0.35))
print("target (+4,+1.1) within 0.35 m of a wall:", hit(4, 1.1, 0.35))
