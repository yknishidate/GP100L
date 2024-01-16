import taichi as ti
import numpy as np


def find_furthest_point_in_direction(points, direction):
    dots = np.dot(points, direction)
    return np.argmax(dots)


def length(vec):
    return np.linalg.norm(vec)


def normalize(vec):
    return vec / length(vec)


def square_distance_from_line(point, line_begin, line_end):
    direction = normalize(line_end - line_begin)
    point_vec = point - line_begin
    dot = np.dot(point_vec, direction)
    return np.dot(point_vec, point_vec) - dot * dot


def find_furthest_point_from_line(points, line_begin, line_end):
    distances = np.zeros(points.shape[0])
    for i in range(points.shape[0]):
        distances[i] = square_distance_from_line(
            points[i], line_begin, line_end)
    return np.argmax(distances)


def sort_ccw(a, b, c):
    ab = b - a
    ac = c - a
    if np.cross(ab, ac) > 0:
        return a, b, c
    else:
        return a, c, b


def is_inner(p, a, b, c):
    a, b, c = sort_ccw(a, b, c)
    return np.cross(b - a, p - a) > 0 and \
        np.cross(c - b, p - b) > 0 and \
        np.cross(a - c, p - c) > 0


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
        # Select circle
        if window.is_pressed(ti.ui.LMB):
            for i in range(num):
                if length(window.get_cursor_pos() - centers[i]) < 0.01:
                    selected = i
                    break

        if selected != -1:
            centers[selected] = window.get_cursor_pos()
            if not window.is_pressed(ti.ui.LMB):
                selected = -1

        # 2点とる
        direction = np.array([-1.0, 0.0])
        index0 = find_furthest_point_in_direction(centers, direction)
        index1 = find_furthest_point_in_direction(centers, -direction)

        _centers.from_numpy(centers)
        canvas.circles(_centers, 0.01, color=(0.0, 0.0, 0.0))

        _line[0] = centers[index0]
        _line[1] = centers[index1]
        canvas.lines(_line, 0.01)

        # 線から一番遠い点をとる
        index2 = find_furthest_point_from_line(centers,
                                               centers[index0],
                                               centers[index1])

        _center[0] = centers[index0]
        canvas.circles(_center, 0.01, color=(1.0, 0.0, 0.0))
        _center[0] = centers[index1]
        canvas.circles(_center, 0.01, color=(0.0, 1.0, 0.0))
        _center[0] = centers[index2]
        canvas.circles(_center, 0.01, color=(0.0, 0.0, 1.0))

        _line[0] = centers[index0]
        _line[1] = centers[index2]
        canvas.lines(_line, 0.01)

        _line[0] = centers[index1]
        _line[1] = centers[index2]
        canvas.lines(_line, 0.01)

        for i in range(num):
            if i == index0 or i == index1 or i == index2:
                continue
            if is_inner(centers[i], centers[index0], centers[index1], centers[index2]):
                _center[0] = centers[i]
                canvas.circles(_center, 0.01, color=(1.0, 1.0, 0.0))

        window.show()
