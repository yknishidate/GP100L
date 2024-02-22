import taichi as ti
import numpy as np


@ti.func
def index_color(index: int):
    r = (index & 0b11) / 3
    g = ((index >> 2) & 0b11) / 3
    b = ((index >> 4) & 0b11) / 3
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


@ti.func
def distance(x1, y1, x2, y2):
    return (x1 - x2) ** 2 + (y1 - y2) ** 2


@ti.kernel
def jump_flooding_algorithm(grid: ti.template(), seeds_points: ti.template(), step: int):
    for x, y in grid:
        if grid[x, y] == 0:
            continue
        new_seed = grid[x, y]
        for dx, dy in ti.ndrange((-1, 2), (-1, 2)):
            nx, ny = x + dx * step, y + dy * step
            if nx < 0 or nx >= grid.shape[0] or ny < 0 or ny >= grid.shape[1]:
                continue
            if grid[nx, ny] == 0:
                grid[nx, ny] = new_seed
            elif grid[nx, ny] != new_seed:
                old_seed = grid[nx, ny]
                new_point = seeds_points[new_seed - 1]
                old_point = seeds_points[old_seed - 1]
                new_dist = distance(nx, ny, new_point[0], new_point[1])
                old_dist = distance(nx, ny, old_point[0], old_point[1])
                if new_dist < old_dist:
                    grid[nx, ny] = new_seed


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    pixel_res = 1024
    grid_res = 128
    cell_size = pixel_res // grid_res
    gui = ti.GUI("JFA", res=(pixel_res, pixel_res), fast_gui=True)
    pixels = ti.Vector.field(3, dtype=float, shape=(pixel_res, pixel_res))
    grid = ti.field(dtype=int, shape=(grid_res, grid_res))

    np.random.seed(2)
    num_seeds = 32
    random_points = np.random.rand(num_seeds, 2) * grid_res
    random_points = random_points.astype(int)
    seeds_points = ti.Vector.field(2, dtype=int, shape=num_seeds)
    seeds_points.from_numpy(random_points)
    for i in range(num_seeds):
        grid[random_points[i, 0], random_points[i, 1]] = i + 1

    step = grid_res // 2
    frame = 0
    interval = 30
    while gui.running:
        if frame % interval == 0:
            jump_flooding_algorithm(grid, seeds_points, step)
            step = max(step // 2, 1)
            ti.tools.imwrite(pixels.to_numpy(), 'docs/images/jfa.jpg')
        frame += 1

        render(cell_size, grid, pixels)
        gui.set_image(pixels)
        gui.show()
