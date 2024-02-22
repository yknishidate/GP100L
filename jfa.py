import taichi as ti


@ti.kernel
def render(cell_size: int, grid: ti.template(), colors: ti.template()):
    for i, j in colors:
        color = ti.Vector([0.1, 0.1, 0.1])
        x = i // cell_size
        y = j // cell_size

        # Grid lines
        if i % cell_size == 0 or j % cell_size == 0:
            color = ti.Vector([0.5, 0.5, 0.5])
        elif grid[x, y] == 1:
            color = ti.Vector([0.1, 0.1, 0.8])

        colors[i, j] = ti.math.clamp(color, 0.0, 1.0)


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
                        grid[nx, ny] = 1


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    width, height = 1024, 1024
    grid_res = 64
    cell_size = width // grid_res
    gui = ti.GUI("JFA", res=(width, height), fast_gui=True)
    colors = ti.Vector.field(3, dtype=float, shape=(width, height))
    grid = ti.field(dtype=int, shape=(grid_res, grid_res))
    grid[8, 8] = 1

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

        render(cell_size, grid, colors)
        gui.set_image(colors)
        gui.show()
