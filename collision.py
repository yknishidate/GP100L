import taichi as ti
import math


def draw_capsule(canvas, p, q, radius, color):
    """
    p: ti.Vector([x, y])
    q: ti.Vector([x, y])
    """
    n = 64
    centers = ti.Vector.field(2, dtype=float, shape=n)
    for i in range(n):
        centers[i] = p + (q - p) * (i / (n - 1))

    canvas.circles(centers, radius, color=color)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def length(a):
    return math.sqrt(dot(a, a))


def normalize(a):
    return a / length(a)


def distance(a, b):
    return length(a - b)


def intersect_sphere_line(origin, direction, center, radius):
    """
    origin: ti.Vector([x, y])
    direction: ti.Vector([x, y])
    center: ti.Vector([x, y])
    """
    oc = origin - center
    a = dot(direction, direction)
    b = 2.0 * dot(oc, direction)
    c = dot(oc, oc) - radius * radius
    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return False, 0.0
    else:
        t = (-b - math.sqrt(discriminant)) / (2.0 * a)
        if t < 0:
            t = (-b + math.sqrt(discriminant)) / (2.0 * a)
        if t < 0:
            return False, 0.0
        else:
            return True, t


def intersect_sphere_line_segment(p, q, center, radius):
    origin = p
    direction = normalize(q - p)
    intersected, t = intersect_sphere_line(origin, direction, center, radius)
    if intersected:
        if 0 <= t <= distance(p, q):
            return True
    return False


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Collision", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))

    centers = ti.Vector.field(2, dtype=float, shape=1)

    gui = window.get_gui()
    rad_a = 0.1
    rad_b = 0.05
    while window.running:

        centers[0] = window.get_cursor_pos()
        canvas.circles(centers, rad_a, color=(1.0, 0.0, 0.0))

        color = (0.0, 0.0, 0.0)
        p = ti.Vector([0.3, 0.3])
        q = ti.Vector([0.7, 0.7])
        if intersect_sphere_line_segment(p, q, centers[0], rad_a + rad_b):
            color = (1.0, 0.0, 0.0)

        draw_capsule(canvas, p, q,
                     rad_b,
                     color=color)

        window.show()
