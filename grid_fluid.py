import taichi as ti
import time
from perlin_noise import PerlinNoise, lerp


@ti.func
def sample_lerp(data: ti.template(), normed_pos: ti.template()):
    pos = normed_pos * ti.Vector([width, height])
    x, y = int(pos.x), int(pos.y)
    tx, ty = pos.x - x, pos.y - y
    val00 = data[x, y]
    val10 = data[x + 1, y]
    val01 = data[x, y + 1]
    val11 = data[x + 1, y + 1]
    val0 = lerp(val00, val10, tx)
    val1 = lerp(val01, val11, tx)
    return lerp(val0, val1, ty)


# @ti.kernel
# def init_force():
#     for i, j in colors:
#         # x = perlin.noise(i / 256, j / 256, 0.34) - 0.5
#         # y = perlin.noise(i / 256, j / 256, 0.68) - 0.5
#         # force[i, j] = (x, y)
#         if
#         force[i, j] = (i / width - 0.5, j / height - 0.5)


@ti.func
def compute_pressure():
    for i, j in colors:
        x0 = pressure[i - 1, j]
        x1 = pressure[i + 1, j]
        y0 = pressure[i, j - 1]
        y1 = pressure[i, j + 1]
        div = divergence[i, j]
        pressure[i, j] = (x0 + x1 + y0 + y1 - div) / 4


@ti.kernel
def add_force(cursor: ti.template(), cursor_move: ti.template()):
    for i, j in colors:
        pos = ti.Vector([i / width, j / height])
        dist = ti.max(ti.math.distance(pos, cursor), 0.1) * 10.0
        velocity[i, j] += cursor_move / (dist * dist)


@ti.kernel
def advect():
    for i, j in colors:
        offset = velocity[i, j] * 0.05
        velocity[i, j] = velocity[i - int(offset.x * width), j - int(offset.y * height)]


@ti.kernel
def compute_divergence():
    for i, j in colors:
        x0 = velocity[i - 1, j].x
        x1 = velocity[i + 1, j].x
        y0 = velocity[i, j - 1].y
        y1 = velocity[i, j + 1].y
        dx = (x1 - x0) / 2.0
        dy = (y1 - y0) / 2.0
        divergence[i, j] = dx + dy


@ti.kernel
def render(dt: float):

    compute_pressure()
    compute_pressure()
    compute_pressure()
    compute_pressure()
    compute_pressure()
    for i, j in colors:
        x0 = pressure[i - 1, j]
        x1 = pressure[i + 1, j]
        y0 = pressure[i, j - 1]
        y1 = pressure[i, j + 1]
        dx = (x1 - x0) / 2.0
        dy = (y1 - y0) / 2.0
        grad = ti.Vector([dx, dy])
        velocity[i, j] -= grad

    for i, j in colors:
        colors[i, j].xz = ti.abs(velocity[i, j].xy * 5)
        # colors[i, j].x = ti.abs(divergence[i, j] * 5)
        # colors[i, j].x = ti.abs(pressure[i, j] * 5)


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    width, height = 1024, 1024
    window = ti.ui.Window("Grid-based fluid", (width, height), vsync=True)
    canvas = window.get_canvas()
    colors = ti.Vector.field(3, dtype=float, shape=(width, height))
    velocity = ti.Vector.field(2, dtype=float, shape=(width, height))
    divergence = ti.field(dtype=float, shape=(width, height))
    pressure = ti.field(dtype=float, shape=(width, height))
    perlin = PerlinNoise()
    # init_force()

    last_time = time.time()
    last_cursor = ti.Vector(window.get_cursor_pos())
    while window.running:
        cursor = ti.Vector(window.get_cursor_pos())
        t = time.time()
        add_force(cursor, (cursor - last_cursor))
        advect()
        compute_divergence()
        render(t - last_time)

        # ti.profiler.print_scoped_profiler_info()
        canvas.set_image(colors)
        window.show()
        last_cursor = cursor
        last_time = t
