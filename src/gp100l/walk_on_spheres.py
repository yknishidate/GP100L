import taichi as ti
import numpy as np
from taichi import math as tm

vec2 = tm.vec2

@ti.func
def closest_point(x: vec2, a: vec2, b: vec2):
    u = b - a
    t = tm.clamp(tm.dot(x - a, u) / tm.dot(u, u), 0.0, 1.0)
    return (1.0 - t) * a + t * b

@ti.func
def distance_from_boundaries(pos: vec2, centers):
    min_distance = 10000.0
    num = centers.shape[0]
    for i in range(num):
        a = centers[i]
        b = centers[(i+1) % num]
        y = closest_point(pos, a, b)
        dist = tm.distance(pos, y)
        # if tm.cross(b - a, pos - a) < 0.0:
        #     dist = -dist
        min_distance = tm.min(min_distance, dist)
    return min_distance

@ti.kernel
def render(centers: ti.template()):
    for i, j in colors:
        # screen_position = ti.Vector([i / width - 0.5, j / height - 0.5, 0])
        screen_position = vec2([i / width, j / height])
        dist = distance_from_boundaries(screen_position, centers)
        # colors[i, j] = tm.clamp(screen_position, 0.0, 1.0)
        if dist < 0:
            colors[i, j] = (0, 0, -dist * 10)
        else:
            colors[i, j] = (dist * 10, 0, 0)

@ti.func
def sample_on_circle(center: vec2, radius: float) -> vec2:
    angle = ti.random() * 2.0 * tm.pi
    x = tm.cos(angle) * radius
    y = tm.sin(angle) * radius
    return center + (x, y)

@ti.kernel
def init_boundary_colors(boundary_colors: ti.template()):
    for i in boundary_colors:
        boundary_colors[i] = (ti.random(), ti.random(), ti.random())

@ti.kernel
def recursive_walk(sample_pos: ti.template(), centers: ti.template()):
    # TODO: curr_pos = ti.Vector([0.0, 0.0])
    recursive_circle_centers.fill((0.0, 0.0))
    recursive_circle_radiuses.fill((0.0))

    curr_pos = vec2([sample_pos[0][0], sample_pos[0][1]])
    # recursive_circle_centers[0] = (sample_pos[0][0], sample_pos[0][1])
    # curr_pos = sample_pos[0]
    broken = False  # emulate `break` in ti.kernel
    for i in range(10):
        if not broken:
            dist = distance_from_boundaries(curr_pos, centers)
            if dist < 0.001:
                broken = True
            
            recursive_circle_centers[i] = curr_pos
            recursive_circle_radiuses[i] = dist

            curr_pos = sample_on_circle(recursive_circle_centers[i], dist)


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    width, height = 1024, 1024
    window = ti.ui.Window("Walk on Spheres", (width, height), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))

    num = 6
    centers = np.zeros((num, 2))
    centers[0] = (0.2, 0.2)
    centers[1] = (0.8, 0.3)
    centers[2] = (0.6, 0.5)
    centers[3] = (0.8, 0.8)
    centers[4] = (0.2, 0.7)
    centers[5] = (0.4, 0.4)
    _centers = ti.Vector.field(2, dtype=float, shape=num)
    _line = ti.Vector.field(2, dtype=float, shape=2)
    colors = ti.Vector.field(3, dtype=float, shape=(width, height))
    boundary_colors = ti.Vector.field(3, dtype=float, shape=num)
    init_boundary_colors(boundary_colors)

    max_recursive = 10
    recursive_circle_centers = ti.Vector.field(2, dtype=float, shape=max_recursive)
    recursive_circle_radiuses = ti.Vector.field(1, dtype=float, shape=max_recursive)

    sample_pos = ti.Vector.field(2, dtype=float, shape=1)
    sample_pos[0] = (0.5, 0.5)
    _draw_pos = ti.Vector.field(2, dtype=float, shape=1)

    selected = -1
    gui = window.get_gui()
    while window.running:
        # Select and move circle
        # if selected == -1 and window.is_pressed(ti.ui.LMB):
        #     for i in range(num):
        #         if np.linalg.norm(window.get_cursor_pos() - centers[i]) < 0.02:
        #             selected = i
        #             break
        # if selected != -1:
        #     centers[selected] = window.get_cursor_pos()
        #     if not window.is_pressed(ti.ui.LMB):
        #         selected = -1
        if window.is_pressed(ti.ui.LMB):
            sample_pos[0] = window.get_cursor_pos()

        # Render image
        # render(_centers)
        # canvas.set_image(colors)

        # Draw lines
        for i in range(num):
            _line[0] = centers[i]
            _line[1] = centers[(i + 1) % num]
            canvas.lines(_line, 0.005, color=(boundary_colors[i][0], boundary_colors[i][1], boundary_colors[i][2]))

        # Draw all circles
        _centers.from_numpy(centers.astype(np.float32))
        canvas.circles(_centers, 0.005, color=(0.0, 0.0, 0.0))

        # ---

        recursive_walk(sample_pos, _centers)

        for i in range(max_recursive):
            _draw_pos[0] = recursive_circle_centers[i]
            canvas.circles(_draw_pos, recursive_circle_radiuses[i][0], color=(0.9, 0.9, 0.9))

        # Draw sample pos
        canvas.circles(sample_pos, 0.005, color=(0.0, 1.0, 0.0))


        window.show()
