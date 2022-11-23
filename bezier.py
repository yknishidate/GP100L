import taichi as ti
import math


@ti.kernel
def compute_bezier():
    for i in range(num_bezier_points):
        p0, p1, p2, p3 = points[0], points[1], points[2], points[3]
        t = i / (num_bezier_points - 1)
        bezier_points[i] = ((1 - t) ** 3 * p0 +
                            3 * t * (1 - t) ** 2 * p1 +
                            3 * t ** 2 * (1 - t) * p2 +
                            t ** 3 * p3)


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Bezier", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))

    num_points = 4
    radius = 0.01
    points = ti.Vector.field(2, dtype=float, shape=num_points)
    points[0] = (0.1, 0.5)
    points[1] = (0.4, 0.8)
    points[2] = (0.6, 0.2)
    points[3] = (0.9, 0.5)
    points_indices = ti.field(dtype=int, shape=(num_points - 1) * 2)
    for i in range(num_points):
        points_indices[i * 2] = i
        points_indices[i * 2 + 1] = i + 1

    selected_point = ti.Vector.field(2, dtype=float, shape=1)
    selected = None

    num_bezier_points = 50
    bezier_points = ti.Vector.field(2, dtype=float, shape=num_bezier_points)
    bezier_indices = ti.field(dtype=int, shape=(num_bezier_points - 1) * 2)
    for i in range(num_bezier_points - 1):
        bezier_indices[i * 2] = i
        bezier_indices[i * 2 + 1] = i + 1

    compute_bezier()
    while window.running:
        canvas.circles(points, radius)
        canvas.lines(points, 0.002, points_indices)
        cursor = window.get_cursor_pos()
        if window.is_pressed(ti.ui.LMB):
            # select point
            if selected is None:
                for i in range(num_points):
                    vec = cursor - points[i]
                    dist = math.sqrt(vec.x * vec.x + vec.y * vec.y)
                    if dist < radius:
                        selected = i
                        break

            # move selected point
            if selected is not None:
                selected_point[0] = points[selected]
                canvas.circles(selected_point, radius, color=(1.0, 0.0, 0.0))
                points[selected] = cursor
                compute_bezier()
        else:
            selected = None

        canvas.lines(bezier_points, 0.003, bezier_indices, color=(0.0, 0.0, 1.0))
        window.show()
