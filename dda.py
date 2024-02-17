import taichi as ti

grid_res = 16


def draw_grid(gui):
    for i in range(grid_res):
        t = i / float(grid_res)
        gui.line((t, 0), (t, 1), color=0xFFFFFF)
        gui.line((0, t), (1, t), color=0xFFFFFF)


def draw_cell(gui, x: int, y: int):
    p0 = (x / grid_res, y / grid_res)
    p1 = ((x + 1) / grid_res, (y + 1) / grid_res)
    gui.rect(p0, p1, radius=5, color=0x068587)


def draw_line_using_dda(gui, begin, end):
    x0, y0 = int(begin[0] * grid_res), int(begin[1] * grid_res)
    x1, y1 = int(end[0] * grid_res), int(end[1] * grid_res)
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy))
    x_inc = dx / steps
    y_inc = dy / steps
    x, y = x0, y0
    for _ in range(int(steps) + 1):
        draw_cell(gui, round(x), round(y))
        x += x_inc
        y += y_inc


if __name__ == '__main__':
    gui = ti.GUI('DDA', res=(1024, 1024))
    begin = [0.1, 0.3]
    end = [0.9, 0.9]
    while gui.running:
        save_to_image = False
        if gui.get_event(ti.GUI.PRESS):
            e = gui.event
            if e.key == ti.GUI.LMB:
                begin = [e.pos[0], e.pos[1]]
            if e.key == ti.GUI.RMB:
                end = [e.pos[0], e.pos[1]]
            if e.key == 's':
                save_to_image = True

        draw_grid(gui)
        draw_line_using_dda(gui, begin, end)
        gui.line(begin, end, radius=3, color=0x068587)
        if save_to_image:
            gui.show(f'docs/images/dda.jpg')
        else:
            gui.show()
