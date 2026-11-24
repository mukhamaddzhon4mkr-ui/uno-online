import math


def draw_gradient(canvas, width, height, top, bottom):
    for y in range(height):
        k = y / height
        r = int(top[0] + (bottom[0] - top[0]) * k)
        g = int(top[1] + (bottom[1] - top[1]) * k)
        b = int(top[2] + (bottom[2] - top[2]) * k)
        canvas.create_line(0, y, width, y, fill=f"#{r:02x}{g:02x}{b:02x}")


def round_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    points = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def rotated_oval(canvas, cx, cy, rx, ry, angle, **kwargs):
    points = []
    rad = math.radians(angle)
    for i in range(48):
        t = 2 * math.pi * i / 48
        x = rx * math.cos(t)
        y = ry * math.sin(t)
        px = cx + x * math.cos(rad) - y * math.sin(rad)
        py = cy + x * math.sin(rad) + y * math.cos(rad)
        points.append(px)
        points.append(py)
    return canvas.create_polygon(points, smooth=True, **kwargs)