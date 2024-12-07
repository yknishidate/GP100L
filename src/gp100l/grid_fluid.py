import numpy as np
import taichi as ti

@ti.func
def sample_lerp(data: ti.template(), normed_pos: ti.template()):
    pos = normed_pos * ti.Vector([width, height])
    x, y = int(pos.x), int(pos.y)
    tx, ty = pos.x - x, pos.y - y
    val00 = data[x, y]
    val10 = data[x + 1, y]
    val01 = data[x, y + 1]
    val11 = data[x + 1, y + 1]
    val0 = ti.math.mix(val00, val10, tx)
    val1 = ti.math.mix(val01, val11, tx)
    return ti.math.mix(val0, val1, ty)


@ti.kernel
def compute_pressure(parity: int):
    for i in range(1, width - 1):
        for j in range(1, height - 1):
            if (i + j) % 2 == parity:
                x0 = pressure[i - 1, j]
                x1 = pressure[i + 1, j]
                y0 = pressure[i, j - 1]
                y1 = pressure[i, j + 1]
                div = divergence[i, j]
                pressure[i, j] = (x0 + x1 + y0 + y1 - div) / 4


@ti.kernel
def add_force(cursor: ti.template()):
    for i in range(1, width - 1):
        for j in range(1, height - 1):
            pos = ti.Vector([i / width, j / height])
            if ti.math.distance(pos, cursor) < 0.1:
                velocity[i, j] = ti.Vector([0.0, -0.2])


@ti.kernel
def advect(dt: float):
    for i in range(1, width - 1):
        for j in range(1, height - 1):
            offset = velocity[i, j] * dt
            pos = ti.Vector([i / width, j / height])
            velocity[i, j] = sample_lerp(velocity, pos - offset)


@ti.kernel
def compute_divergence():
    for i in range(1, width - 1):
        for j in range(1, height - 1):
            x0 = velocity[i - 1, j].x
            x1 = velocity[i + 1, j].x
            y0 = velocity[i, j - 1].y
            y1 = velocity[i, j + 1].y
            dx = (x1 - x0) / 2.0
            dy = (y1 - y0) / 2.0
            divergence[i, j] = (dx + dy) * 1.9


@ti.kernel
def subtract_pressure_gradient():
    for i in range(1, width - 1):
        for j in range(1, height - 1):
            x0 = pressure[i - 1, j]
            x1 = pressure[i + 1, j]
            y0 = pressure[i, j - 1]
            y1 = pressure[i, j + 1]
            dx = (x1 - x0) / 2.0
            dy = (y1 - y0) / 2.0
            grad = ti.Vector([dx, dy])
            velocity[i, j] -= grad


@ti.kernel
def render():
    for i, j in colors:
        colors[i, j].xy = ti.abs(velocity[i, j] * 5)
        colors[i, j].z = ti.abs(pressure[i, j] * 5)


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    width, height = 1024, 1024
    window = ti.ui.Window("Grid-based fluid", (width, height), vsync=True)
    canvas = window.get_canvas()
    colors = ti.Vector.field(3, dtype=float, shape=(width, height))
    velocity = ti.Vector.field(2, dtype=float, shape=(width, height))
    divergence = ti.field(dtype=float, shape=(width, height))
    pressure = ti.field(dtype=float, shape=(width, height))

    frame = 0
    while window.running:
        emitter_pos = ti.Vector([0.5 + np.sin(frame * 0.04) * 0.2, 0.7])
        add_force(emitter_pos)
        advect(0.05)
        compute_divergence()
        pressure.fill(0.0)
        for i in range(20):
            compute_pressure(parity=i%2)
        subtract_pressure_gradient()
        render()

        canvas.set_image(colors)
        window.show()
        frame += 1
