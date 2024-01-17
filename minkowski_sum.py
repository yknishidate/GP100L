import taichi as ti
import numpy as np
import convex_hull as ch


class ConvexHull:
    def __init__(self):
        self.centers = None
        self.convex_hull = []
        self.convex_hull_lines = []
        self.pos = np.array([0.0, 0.0])

        # self._centers = ti.Vector.field(2, dtype=float, shape=num_points)
        self._center = ti.Vector.field(2, dtype=float, shape=1)
        self._line = ti.Vector.field(2, dtype=float, shape=2)

    def build(self, centers):
        self.centers = centers
        self.convex_hull, self.convex_hull_lines = ch.build_convex_hull(
            self.centers)

    def draw(self, canvas, color):
        centers = self.centers + self.pos

        # Draw convex hull lines
        for i in range(0, len(self.convex_hull_lines), 2):
            self._line[0] = centers[self.convex_hull_lines[i]]
            self._line[1] = centers[self.convex_hull_lines[i + 1]]
            canvas.lines(self._line, 0.01, color=color)

        # Draw convex hull circles
        for i in self.convex_hull:
            self._center[0] = centers[i]
            canvas.circles(self._center, 0.01, color=color)

    def is_inner(self, p):
        # check using cross
        p -= self.pos
        for i in range(0, len(self.convex_hull_lines), 2):
            a = self.centers[self.convex_hull_lines[i]]
            b = self.centers[self.convex_hull_lines[i + 1]]
            if np.cross(b - a, p - a) < 0:
                return False
        return True

    def minkowski_diff(self, other):
        centers = np.zeros((len(self.centers) * len(other.centers), 2))
        self_centers = self.centers + self.pos
        other_centers = other.centers + other.pos
        for i in range(len(self_centers)):
            for j in range(len(other_centers)):
                centers[i * len(other_centers) +
                        j] = self_centers[i] - other_centers[j]
        sum = ConvexHull()
        sum.build(centers)
        return sum


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Minkowski Sum", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))

    convex_hull1 = ConvexHull()
    convex_hull1.build(ch.generate_random_points(10, 0.5))
    convex_hull1.pos = np.array([0.0, 0.25])
    convex_hull2 = ConvexHull()
    convex_hull2.build(ch.generate_random_points(10, 0.5))
    convex_hull2.pos = np.array([0.5, 0.25])

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

        # Compute Minkowski sum
        sum_hull = convex_hull1.minkowski_diff(convex_hull2)
        color = (0.0, 0.0, 0.0)
        if sum_hull.is_inner(np.array([0.0, 0.0])):
            color = (1.0, 0.0, 0.0)

        convex_hull1.draw(canvas, color)
        convex_hull2.draw(canvas, color)
        window.show()
