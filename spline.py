import taichi as ti
import math


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Spline", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))

    num_points = 4
    radius = 0.01
    positions = ti.Vector.field(2, dtype=float, shape=num_points)
    positions[0] = (0.2, 0.5)
    positions[1] = (0.4, 0.5)
    positions[2] = (0.6, 0.5)
    positions[3] = (0.8, 0.5)

    position = ti.Vector.field(2, dtype=float, shape=1)
    selected = None
    while window.running:
        canvas.circles(positions, radius)
        cursor = window.get_cursor_pos()
        if window.is_pressed(ti.ui.LMB):
            # select point
            if selected is None:
                for i in range(num_points):
                    vec = cursor - positions[i]
                    dist = math.sqrt(vec.x * vec.x + vec.y * vec.y)
                    if dist < radius:
                        selected = i
                        break

            # move point
            if selected is not None:
                position[0] = positions[selected]
                canvas.circles(position, radius, color=(1.0, 0.0, 0.0))
                positions[selected] = cursor
        else:
            selected = None

        window.show()
