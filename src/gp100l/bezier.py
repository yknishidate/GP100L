import taichi as ti
import ui_util


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
    points = ti.Vector.field(2, dtype=float, shape=num_points)
    points[0] = (0.1, 0.5)
    points[1] = (0.4, 0.8)
    points[2] = (0.6, 0.2)
    points[3] = (0.9, 0.5)

    selected_point = ti.Vector.field(2, dtype=float, shape=1)
    selected = -1

    num_bezier_points = 50
    bezier_points = ti.Vector.field(2, dtype=float, shape=num_bezier_points)

    compute_bezier()
    while window.running:
        compute_bezier()

        canvas.circles(points, 0.007)
        canvas.lines(points, 0.003)

        selected = ui_util.select_and_drag_circle(window, selected, points, num_points)
        selected_point[0] = points[selected]
        canvas.circles(selected_point, 0.007, color=(1.0, 0.0, 0.0))

        canvas.lines(bezier_points, 0.003, color=(0.0, 0.0, 1.0))
        window.show()
