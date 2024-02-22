import taichi as ti
import numpy as np


@ti.func
def index_color(index: int):
    r = (index & 1) * 0.5 + 0.5
    g = ((index >> 1) & 1) * 0.5 + 0.5
    b = ((index >> 2) & 1) * 0.5 + 0.5
    return ti.Vector([r, g, b])


@ti.kernel
def render(cell_size: int, grid: ti.template(), pixels: ti.template()):
    for i, j in pixels:
        color = ti.Vector([0.1, 0.1, 0.1])
        x = i // cell_size
        y = j // cell_size

        # Grid lines
        if i % cell_size == 0 or j % cell_size == 0:
            color = ti.Vector([0.3, 0.3, 0.3])
        elif grid[x, y] > 0:
            color = index_color(grid[x, y])

        pixels[i, j] = ti.math.clamp(color, 0.0, 1.0)


@ti.kernel
def jump_flooding_algorithm(grid: ti.template(), step: int):
    for x, y in grid:
        if grid[x, y] == 0:
            continue
        for dx in ti.static(range(-1, 2)):
            for dy in ti.static(range(-1, 2)):
                nx, ny = x + dx * step, y + dy * step
                if nx >= 0 and nx < grid.shape[0] and ny >= 0 and ny < grid.shape[1]:
                    if grid[nx, ny] == 0:
                        grid[nx, ny] = grid[x, y]


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    pixel_res = 1024
    grid_res = 64
    cell_size = pixel_res // grid_res
    gui = ti.GUI("JFA", res=(pixel_res, pixel_res), fast_gui=True)
    pixels = ti.Vector.field(3, dtype=float, shape=(pixel_res, pixel_res))
    grid = ti.field(dtype=int, shape=(grid_res, grid_res))

    n_points = 5
    points = np.random.rand(n_points, 2) * grid_res
    for i in range(n_points):
        grid[int(points[i, 0]), int(points[i, 1])] = i + 1

    step = grid_res // 2

    frame = 0
    interval = 20
    while gui.running:
        if frame % interval == 0 and step > 0:
            jump_flooding_algorithm(grid, step)
            if step == 1:
                step = 0
            step //= 2
        frame += 1

        render(cell_size, grid, pixels)
        gui.set_image(pixels)
        gui.show()
