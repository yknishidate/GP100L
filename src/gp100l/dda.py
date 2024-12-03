import taichi as ti


def draw_grid(gui, grid_res: int):
    for i in range(grid_res):
        t = i / float(grid_res)
        gui.line((t, 0), (t, 1), color=0xFFFFFF)
        gui.line((0, t), (1, t), color=0xFFFFFF)


def draw_line(gui, x0: int, y0: int, x1: int, y1: int, grid_res: int):
    gui.line(((x0 + 0.5) / grid_res, (y0 + 0.5) / grid_res),
             ((x1 + 0.5) / grid_res, (y1 + 0.5) / grid_res), radius=2, color=0x068587)


def draw_cell(gui, x: int, y: int, grid_res: int):
    p0 = (x / grid_res, y / grid_res)
    p1 = ((x + 1) / grid_res, (y + 1) / grid_res)
    gui.rect(p0, p1, radius=5, color=0x068587)


def draw_line_using_dda(gui, x0: int, y0: int, x1: int, y1: int, grid_res: int):
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy))
    x_inc = dx / steps
    y_inc = dy / steps
    x, y = x0, y0
    for _ in range(int(steps) + 1):
        draw_cell(gui, round(x), round(y), grid_res)
        x += x_inc
        y += y_inc


if __name__ == '__main__':
    gui = ti.GUI('DDA', res=(1024, 1024))
    grid_res = 16
    x0, y0 = 3, 3
    x1, y1 = 12, 12
    while gui.running:
        save_to_image = False
        if gui.get_event(ti.GUI.PRESS):
            e = gui.event
            if e.key == ti.GUI.LMB:
                x0, y0 = int(e.pos[0] * grid_res), int(e.pos[1] * grid_res)
            if e.key == ti.GUI.RMB:
                x1, y1 = int(e.pos[0] * grid_res), int(e.pos[1] * grid_res)
            if e.key == 's':
                save_to_image = True

        draw_grid(gui, grid_res)
        draw_line_using_dda(gui, x0, y0, x1, y1, grid_res)
        draw_line(gui, x0, y0, x1, y1, grid_res)
        if save_to_image:
            gui.show(f'docs/images/dda.jpg')
        else:
            gui.show()
