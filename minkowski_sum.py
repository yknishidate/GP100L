import taichi as ti
import numpy as np
import convex_hull as ch


class ConvexHull:
    def __init__(self, num_points, pos):
        self.centers = np.zeros((num_points, 2))
        for i in range(num_points):
            self.centers[i] = np.random.random(2) * 0.5

        self.convex_hull = []
        self.convex_hull_lines = []
        self.convex_hull, self.convex_hull_lines = ch.build_convex_hull(
            self.centers)
        self.pos = pos

        # self._centers = ti.Vector.field(2, dtype=float, shape=num_points)
        self._center = ti.Vector.field(2, dtype=float, shape=1)
        self._line = ti.Vector.field(2, dtype=float, shape=2)

    def draw(self, canvas):
        # Draw all circles
        # self._centers.from_numpy(self.centers.astype(np.float32))
        # canvas.circles(self._centers, 0.01, color=(0.0, 0.0, 0.0))
        # self._centers.from_numpy((self.centers + self.pos).astype(np.float32))
        centers = self.centers + self.pos

        # Draw convex hull lines
        for i in range(0, len(self.convex_hull_lines), 2):
            self._line[0] = centers[self.convex_hull_lines[i]]
            self._line[1] = centers[self.convex_hull_lines[i + 1]]
            canvas.lines(self._line, 0.005)

        # Draw convex hull circles
        for i in self.convex_hull:
            self._center[0] = centers[i]
            canvas.circles(self._center, 0.01)

    def is_inner(self, p):
        # check using cross
        p -= self.pos
        for i in range(0, len(self.convex_hull_lines), 2):
            a = self.centers[self.convex_hull_lines[i]]
            b = self.centers[self.convex_hull_lines[i + 1]]
            if np.cross(b - a, p - a) < 0:
                return False
        return True


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Convex Hull", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))

    convex_hull1 = ConvexHull(10, np.array([0.0, 0.25]))
    convex_hull2 = ConvexHull(10, np.array([0.5, 0.25]))

    selected = False
    prev_pos = None
    gui = window.get_gui()
    while window.running:
        # Select and move circle
        if not selected and window.is_pressed(ti.ui.LMB):
            if convex_hull2.is_inner(window.get_cursor_pos()):
                selected = True
                prev_pos = np.array(window.get_cursor_pos())

        if selected:
            convex_hull2.pos += np.array(window.get_cursor_pos()) - prev_pos
            prev_pos = np.array(window.get_cursor_pos())
            if not window.is_pressed(ti.ui.LMB):
                selected = False
                prev_pos = None

        convex_hull1.draw(canvas)
        convex_hull2.draw(canvas)

        window.show()
