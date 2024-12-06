import taichi as ti
import numpy as np

def select_and_drag_circle(window: ti.ui.Window, selection: int, centers, num: int) -> int:
    if selection == -1 and window.is_pressed(ti.ui.LMB):
        for i in range(num):
            if np.linalg.norm(window.get_cursor_pos() - centers[i]) < 0.01:
                selection = i
                break
    if selection != -1:
        centers[selection] = window.get_cursor_pos()
        if not window.is_pressed(ti.ui.LMB):
            selection = -1
    return selection
