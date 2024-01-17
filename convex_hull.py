import taichi as ti
import numpy as np


def generate_random_points(num_points, scale, offset=(0.0, 0.0)):
    centers = np.zeros((num_points, 2))
    for i in range(num_points):
        centers[i] = np.random.random(2) * scale + offset
    return centers


def find_furthest_point_from_line(centers, line_begin, line_end, direction=None):
    # left is positive, right is negative
    signed_distances = np.cross(line_end - line_begin, centers - line_begin)
    if direction is None:
        return np.argmax(np.abs(signed_distances))
    if direction == "left":
        index = np.argmax(signed_distances)
        if signed_distances[index] <= 0:
            return None
        return index
    if direction == "right":
        index = np.argmin(signed_distances)
        if signed_distances[index] >= 0:
            return None
        return index


def sort_ccw(centers, a, b, c):
    if np.cross(centers[b] - centers[a], centers[c] - centers[a]) > 0:
        return a, b, c
    else:
        return a, c, b


def find_hull(centers, convex_hull, convex_hull_lines, a, b):
    c = find_furthest_point_from_line(centers, centers[a], centers[b], "right")
    if c is None:
        convex_hull_lines.append(a)
        convex_hull_lines.append(b)
        return
    convex_hull.append(c)
    find_hull(centers, convex_hull, convex_hull_lines, a, c)
    find_hull(centers, convex_hull, convex_hull_lines, c, b)


def build_convex_hull(centers):
    index0 = np.argmin(centers[:, 0])  # leftmost
    index1 = np.argmax(centers[:, 0])  # rightmost
    index2 = find_furthest_point_from_line(
        centers, centers[index0], centers[index1])
    index0, index1, index2 = sort_ccw(centers, index0, index1, index2)

    convex_hull = [index0, index1, index2]
    convex_hull_lines = []
    find_hull(centers, convex_hull, convex_hull_lines, index0, index1)
    find_hull(centers, convex_hull, convex_hull_lines, index1, index2)
    find_hull(centers, convex_hull, convex_hull_lines, index2, index0)
    return convex_hull, convex_hull_lines


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Convex Hull", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))

    num = 15
    centers = generate_random_points(num, 0.5, (0.25, 0.25))
    _centers = ti.Vector.field(2, dtype=float, shape=num)
    _center = ti.Vector.field(2, dtype=float, shape=1)
    _line = ti.Vector.field(2, dtype=float, shape=2)

    selected = -1
    gui = window.get_gui()
    while window.running:
        # Select and move circle
        if selected == -1 and window.is_pressed(ti.ui.LMB):
            for i in range(num):
                if np.linalg.norm(window.get_cursor_pos() - centers[i]) < 0.01:
                    selected = i
                    break
        if selected != -1:
            centers[selected] = window.get_cursor_pos()
            if not window.is_pressed(ti.ui.LMB):
                selected = -1

        # Build convex hull
        convex_hull, convex_hull_lines = build_convex_hull(centers)

        # Draw all circles
        _centers.from_numpy(centers.astype(np.float32))
        canvas.circles(_centers, 0.01, color=(0.0, 0.0, 0.0))

        # Draw convex hull lines
        for i in range(0, len(convex_hull_lines), 2):
            _line[0] = centers[convex_hull_lines[i]]
            _line[1] = centers[convex_hull_lines[i + 1]]
            canvas.lines(_line, 0.01)

        # Draw convex hull circles
        for i in convex_hull:
            _center[0] = centers[i]
            canvas.circles(_center, 0.01, color=(1.0, 0.0, 0.0))

        window.show()
