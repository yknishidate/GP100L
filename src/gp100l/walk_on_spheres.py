import taichi as ti
import numpy as np

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

if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Convex Hull", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))

    num = 6
    centers = np.zeros((num, 2))
    centers[0] = (0.2, 0.2)
    centers[1] = (0.8, 0.3)
    centers[2] = (0.6, 0.5)
    centers[3] = (0.8, 0.8)
    centers[4] = (0.2, 0.7)
    centers[5] = (0.4, 0.4)
    _centers = ti.Vector.field(2, dtype=float, shape=num)
    _center = ti.Vector.field(2, dtype=float, shape=1)
    _line = ti.Vector.field(2, dtype=float, shape=2)

    selected = -1
    gui = window.get_gui()
    while window.running:
        # Select and move circle
        if selected == -1 and window.is_pressed(ti.ui.LMB):
            for i in range(num):
                if np.linalg.norm(window.get_cursor_pos() - centers[i]) < 0.02:
                    selected = i
                    break
        if selected != -1:
            centers[selected] = window.get_cursor_pos()
            if not window.is_pressed(ti.ui.LMB):
                selected = -1

        # Draw lines
        for i in range(0, num):
            _line[0] = centers[i]
            _line[1] = centers[(i + 1) % num]
            canvas.lines(_line, 0.005)

        # Draw all circles
        _centers.from_numpy(centers.astype(np.float32))
        canvas.circles(_centers, 0.005, color=(0.0, 0.0, 0.0))

        window.show()
