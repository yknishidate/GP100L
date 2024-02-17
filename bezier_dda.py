import taichi as ti
import dda


def draw_circle(gui, x: int, y: int, grid_res: int):
    p = ((x + 0.5) / grid_res, (y + 0.5) / grid_res)
    gui.circle(p, radius=10)


def plot_quad_bezier_seg(gui, x0: int, y0: int, x1: int, y1: int,
                         x2: int, y2: int, grid_res: int):
    sx = x2 - x1
    sy = y2 - y1
    xx = x0 - x1
    yy = y0 - y1
    cur = xx * sy - yy * sx  # 曲率

    # 単調でなければならない
    assert (xx * sx <= 0 and yy * sy <= 0)

    # 長い方から始める
    len12 = sx * sx + sy * sy
    len10 = xx * xx + yy * yy
    if len12 > len10:
        # p0, p2を入れ替える
        x2, x0 = x0, x2
        y2, y0 = y0, y2
        cur = -cur

    # 直線でない場合を処理
    if cur != 0:
        xx += sx
        yy += sy

        # ステップの方向を決める
        sx = 1 if x0 < x2 else -1
        sy = 1 if y0 < y2 else -1

        xx *= sx
        yy *= sy

        xy = 2 * xx * yy
        xx *= xx
        yy *= yy

        # 曲率が負の場合
        if cur * sx * sy < 0:
            xx = -xx
            yy = -yy
            xy = -xy
            cur = -cur

        dx = 4.0 * sy * cur * (x1 - x0) + xx - xy
        dy = 4.0 * sx * cur * (y0 - y1) + yy - xy
        xx += xx
        yy += yy
        err = dx + dy + xy

        while True:
            dda.draw_cell(gui, x0, y0, grid_res)

            # 最後の点に到達したら終了
            if x0 == x2 and y0 == y2:
                break

            # Yステップのテスト値を保存
            y1 = 2 * err < dx

            if 2 * err > dy:
                x0 += sx
                dx -= xy
                dy += yy
                err += dy
            if y1:
                y0 += sy
                dy -= xy
                dx += xx
                err += dx
            if dy >= dx:
                break  # 勾配が否定される -> アルゴリズムが失敗


if __name__ == '__main__':
    gui = ti.GUI('Bezier DDA', res=(1024, 1024))
    grid_res = 32
    x0, y0 = 1, 1
    x1, y1 = 10, 30
    x2, y2 = 30, 30
    while gui.running:
        save_to_image = False
        if gui.is_pressed(ti.GUI.LMB):
            pos = gui.get_cursor_pos()
            x1, y1 = int(pos[0] * grid_res), int(pos[1] * grid_res)

        if gui.get_event(ti.GUI.PRESS):
            if gui.event.key == 's':
                save_to_image = True

        dda.draw_grid(gui, grid_res)
        plot_quad_bezier_seg(gui, x0, y0, x1, y1, x2, y2, grid_res)
        dda.draw_line(gui, x0, y0, x1, y1, grid_res)
        dda.draw_line(gui, x1, y1, x2, y2, grid_res)
        draw_circle(gui, x0, y0, grid_res)
        draw_circle(gui, x1, y1, grid_res)
        draw_circle(gui, x2, y2, grid_res)
        if save_to_image:
            gui.show(f'docs/images/bezier_dda.jpg')
        else:
            gui.show()
