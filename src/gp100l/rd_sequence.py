# Rd sequence
# "The Unreasonable Effectiveness of Quasirandom Sequences", Martin Roberts, 2018.
# https://extremelearning.com.au/unreasonable-effectiveness-of-quasirandom-sequences

import taichi as ti
import numpy as np

class RdGenerator:
    def phi(self, d):
        x = 2.0
        for _ in range(10):
            x = pow(1 + x, 1 / (d + 1)) 
        return x

    def __init__(self, dimension, seed=0.0):
        g = self.phi(dimension)
        self.seed = seed
        self.alpha = np.zeros(dimension)
        for j in range(dimension):
            self.alpha[j] = pow(1 / g, j + 1) % 1

    def sample(self, i):
        return (self.seed + (i + 1) * self.alpha) % 1


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Rd sequence", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))

    dimension = 2
    num = 1000
    sequence = ti.Vector.field(dimension, dtype=float, shape=num)
    colors = ti.Vector.field(3, dtype=float, shape=num)

    generator = RdGenerator(dimension, 0.5)

    i = 0
    while window.running:
        if i < num:
            sequence[i] = generator.sample(i)
            colors[i] = (i / num, 0.0, 1.0 - i / num)
        canvas.circles(sequence, 0.01, per_vertex_color=colors)
        if i == num:
            window.save_image(f'docs/images/rd_sequence.jpg')
        window.show()
        i += 1
