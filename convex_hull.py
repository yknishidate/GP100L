import taichi as ti
import numpy as np


def find_furthest_point_in_direction(points, direction):
    dots = np.dot(points, direction)
    return np.argmax(dots)


def length(vec):
    return np.linalg.norm(vec)


def normalize(vec):
    return vec / length(vec)


def find_furthest_point_from_line(points, line_begin, line_end, direction=None):
    # 左側を正とする
    signed_distances = np.cross(line_end - line_begin, points - line_begin)
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


def sort_ccw(ai, bi, ci):
    if np.cross(centers[bi] - centers[ai], centers[ci] - centers[ai]) > 0:
        return ai, bi, ci
    else:
        return ai, ci, bi


def is_inner(p, a, b, c):
    # abcはCCWとする
    return np.cross(b - a, p - a) > 0 and \
        np.cross(c - b, p - b) > 0 and \
        np.cross(a - c, p - c) > 0


def find_hull(centers, convex_hull, convex_hull_lines, a, b):
    # print(f"find_hull({a}, {b})")
    c = find_furthest_point_from_line(centers, centers[a], centers[b], "right")
    if c is None:
        # print(f"  c is None")
        convex_hull_lines.append(a)
        convex_hull_lines.append(b)
        return
    # print(f"  c = {c}")
    convex_hull.append(c)
    find_hull(centers, convex_hull, convex_hull_lines, a, c)
    find_hull(centers, convex_hull, convex_hull_lines, c, b)


convex_hull = []
convex_hull_lines = []

if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Collision", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))

    num = 15
    centers = np.zeros((num, 2))
    for i in range(num):
        centers[i] = np.random.random(2) * 0.5 + 0.25

    _centers = ti.Vector.field(2, dtype=float, shape=num)
    _center = ti.Vector.field(2, dtype=float, shape=1)
    _line = ti.Vector.field(2, dtype=float, shape=2)

    selected = -1
    gui = window.get_gui()
    while window.running:
        convex_hull = []
        convex_hull_lines = []

        # Select circle
        if selected == -1 and window.is_pressed(ti.ui.LMB):
            for i in range(num):
                if length(window.get_cursor_pos() - centers[i]) < 0.01:
                    selected = i
                    break

        if selected != -1:
            centers[selected] = window.get_cursor_pos()
            if not window.is_pressed(ti.ui.LMB):
                selected = -1

        # Draw all circles
        _centers.from_numpy(centers)
        canvas.circles(_centers, 0.01, color=(0.0, 0.0, 0.0))

        # 2点とる
        direction = np.array([-1.0, 0.0])
        index0 = find_furthest_point_in_direction(centers, direction)
        index1 = find_furthest_point_in_direction(centers, -direction)

        # 線から一番遠い点をとる
        index2 = find_furthest_point_from_line(centers,
                                               centers[index0],
                                               centers[index1])

        index0, index1, index2 = sort_ccw(index0, index1, index2)
        convex_hull = [index0, index1, index2]

        find_hull(centers, convex_hull, convex_hull_lines, index0, index1)
        find_hull(centers, convex_hull, convex_hull_lines, index1, index2)
        find_hull(centers, convex_hull, convex_hull_lines, index2, index0)

        for i in range(num):
            if i in convex_hull:
                _center[0] = centers[i]
                canvas.circles(_center, 0.01, color=(1.0, 1.0, 0.0))

        _indices = ti.field(dtype=int, shape=len(convex_hull_lines))
        _indices.from_numpy(np.array(convex_hull_lines).astype(np.int32))
        canvas.lines(_centers, 0.01, indices=_indices)

        window.show()
