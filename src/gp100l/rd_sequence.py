# Rd sequence
# "The Unreasonable Effectiveness of Quasirandom Sequences", Martin Roberts, 2018.
# https://extremelearning.com.au/unreasonable-effectiveness-of-quasirandom-sequences

import taichi as ti
import numpy as np

def phi(d): 
  x = 2.0
  for _ in range(10): 
    x = pow(1 + x, 1 / (d + 1)) 
  return x


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Rd sequence", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))

    dimension = 2
    num = 1000
    sequence = ti.Vector.field(dimension, dtype=float, shape=num)
    colors = ti.Vector.field(3, dtype=float, shape=num)

    g = phi(dimension)
    alpha = np.zeros(dimension)
    for j in range(dimension):
        alpha[j] = pow(1 / g, j + 1) % 1

    seed = 0.5
    i = 0
    while window.running:
        if i < num:
            sequence[i] = (seed + (i + 1) * alpha) % 1
            colors[i] = (i / num, 0.0, 1.0 - i / num)
        canvas.circles(sequence, 0.01, per_vertex_color=colors)
        if i == num:
          window.save_image(f'docs/images/rd_sequence.jpg')
        window.show()
        i += 1
