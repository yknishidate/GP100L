import taichi as ti
import numpy as np


def draw_capsule(canvas, begin, end, radius, color):
    capsule_centers[0] = begin
    capsule_centers[1] = end
    canvas.circles(capsule_centers, radius, color=color)
    canvas.lines(capsule_centers, radius * 2, color=color)


def intersect_sphere_line(origin, direction, center, radius):
    oc = origin - center
    a = np.dot(direction, direction)
    b = 2.0 * np.dot(oc, direction)
    c = np.dot(oc, oc) - radius * radius
    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return False, 0.0
    t = (-b - np.sqrt(discriminant)) / (2.0 * a)
    if t < 0:
        t = (-b + np.sqrt(discriminant)) / (2.0 * a)
    if t < 0:
        return False, 0.0
    else:
        return True, t


def intersect_sphere_segment(sphere_center, circle_radius, seg_begin, seg_end):
    distance = np.linalg.norm(seg_end - seg_begin)
    direction = (seg_end - seg_begin) / distance
    intersected, t = intersect_sphere_line(
        seg_begin, direction, sphere_center, circle_radius)
    return intersected and 0 <= t <= distance


def intersect_sphere_capsule(sphere_center, circle_rad, cap_begin, cap_end, cap_rad):
    return intersect_sphere_segment(sphere_center, cap_rad + circle_rad, cap_begin, cap_end)


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Collision", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))

    circle_rad = 0.1
    circle_center = ti.Vector.field(2, dtype=float, shape=1)
    capsule_centers = ti.Vector.field(2, dtype=float, shape=2)
    capsule_rad = 0.05

    while window.running:
        circle_center[0] = window.get_cursor_pos()
        canvas.circles(circle_center, circle_rad, color=(1.0, 0.0, 0.0))

        color = (0.0, 0.0, 0.0)
        cap_begin = np.array([0.3, 0.3])
        cap_end = np.array([0.7, 0.7])
        if intersect_sphere_capsule(circle_center[0], circle_rad, cap_begin, cap_end, capsule_rad):
            color = (1.0, 0.0, 0.0)

        draw_capsule(canvas, cap_begin, cap_end, capsule_rad, color)
        window.show()
