import taichi as ti


@ti.kernel
def render(cell_size: int, filled: ti.template(), colors: ti.template()):
    for i, j in colors:
        color = ti.Vector([0.1, 0.1, 0.1])
        x = i // cell_size
        y = j // cell_size

        # Grid lines
        if i % cell_size == 0 or j % cell_size == 0:
            color = ti.Vector([0.5, 0.5, 0.5])
        elif filled[x, y] == 1:
            color = ti.Vector([0.1, 0.1, 0.8])

        colors[i, j] = ti.math.clamp(color, 0.0, 1.0)


def jump_flooding_algorithm(filled, seeds, step):
    for seed in seeds:
        x, y = seed
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx * step, y + dy * step
                if nx >= 0 and nx < filled.shape[0] and ny >= 0 and ny < filled.shape[1]:
                    if filled[nx, ny] == 0:
                        filled[nx, ny] = 1
                        seeds.append((nx, ny))


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    width, height = 1024, 1024
    grid_res = 32
    cell_size = width // grid_res
    gui = ti.GUI("JFA", res=(width, height), fast_gui=True)
    colors = ti.Vector.field(3, dtype=float, shape=(width, height))
    filled = ti.field(dtype=int, shape=(grid_res, grid_res))

    seeds = [(8, 8)]

    step = grid_res // 2

    frame = 0
    interval = 10
    while gui.running:
        if frame % interval == 0 and step > 0:
            jump_flooding_algorithm(filled, seeds, step)
            if step == 1:
                step = 0
            step //= 2
        frame += 1

        for seed in seeds:
            x, y = seed
            filled[x, y] = 1

        render(cell_size, filled, colors)
        gui.set_image(colors)
        gui.show()
