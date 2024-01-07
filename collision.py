import taichi as ti
import numpy as np


def draw_capsule(canvas, seg_begin, seg_end, radius, color):
    n = 64
    centers = ti.Vector.field(2, dtype=float, shape=n)
    centers.from_numpy(np.linspace(seg_begin, seg_end, n).astype(np.float32))
    canvas.circles(centers, radius, color=color)


def intersect_sphere_line(origin, direction, center, radius):
    oc = origin - center
    a = np.dot(direction, direction)
    b = 2.0 * np.dot(oc, direction)
    c = np.dot(oc, oc) - radius * radius
    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return False, 0.0
    else:
        t = (-b - np.sqrt(discriminant)) / (2.0 * a)
        if t < 0:
            t = (-b + np.sqrt(discriminant)) / (2.0 * a)
        if t < 0:
            return False, 0.0
        else:
            return True, t


def intersect_sphere_line_segment(seg_begin, seg_end, sphere_center, sphere_radius):
    origin = seg_begin
    distance = np.linalg.norm(seg_end - seg_begin)
    direction = (seg_end - seg_begin) / distance
    intersected, t = intersect_sphere_line(
        origin, direction, sphere_center, sphere_radius)
    if intersected:
        if 0 <= t <= distance:
            return True
    return False


def intersect_sphere_capsule(seg_begin, seg_end, capsule_rad, sphere_center, sphere_rad):
    return intersect_sphere_line_segment(seg_begin, seg_end, sphere_center, capsule_rad + sphere_rad)


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Collision", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))

    centers = ti.Vector.field(2, dtype=float, shape=1)

    gui = window.get_gui()
    sphere_rad = 0.1
    capsule_rad = 0.05
    while window.running:

        centers[0] = window.get_cursor_pos()
        canvas.circles(centers, sphere_rad, color=(1.0, 0.0, 0.0))

        color = (0.0, 0.0, 0.0)
        seg_begin = np.array([0.3, 0.3])
        seg_end = np.array([0.7, 0.7])
        if intersect_sphere_capsule(seg_begin, seg_end, capsule_rad, centers[0], sphere_rad):
            color = (1.0, 0.0, 0.0)

        draw_capsule(canvas, seg_begin, seg_end, capsule_rad, color=color)
        window.show()
