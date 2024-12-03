import taichi as ti
import numpy as np
from taichi import math as tm

vec2 = tm.vec2
vec3 = tm.vec3

@ti.func
def closest_point(x: vec2, a: vec2, b: vec2):
    u = b - a
    t = tm.clamp(tm.dot(x - a, u) / tm.dot(u, u), 0.0, 1.0)
    return (1.0 - t) * a + t * b

@ti.func
def distance_from_boundaries(pos: vec2) -> vec2:
    min_distance = 10000.0
    num = centers.shape[0]
    argmin = -1
    for i in range(num):
        a = centers[i]
        b = centers[(i+1) % num]
        y = closest_point(pos, a, b)
        dist = tm.distance(pos, y)
        min_distance = tm.min(min_distance, dist)
        argmin = i
    return vec2(min_distance, argmin)

@ti.kernel
def render():
    for i, j in colors:
        screen_position = vec2([i / width, j / height])
        result = distance_from_boundaries(screen_position)
        dist, boundary = result[0], int(result[1])
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
def recursive_walk(sample_pos: vec2):
    recursive_circle_centers.fill((0.0, 0.0))
    recursive_circle_radiuses.fill((0.0))

    curr_pos = vec2(sample_pos[0], sample_pos[1])
    ti.loop_config(serialize=True)
    for i in range(max_recursion):
        result = distance_from_boundaries(curr_pos)
        dist, boundary = result[0], int(result[1])
        
        recursive_circle_centers[i] = vec2(curr_pos[0], curr_pos[1])  # deep copy
        recursive_circle_radiuses[i] = dist

        curr_pos = sample_on_circle(recursive_circle_centers[i], dist)

if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    width, height = 1024, 1024
    window = ti.ui.Window("Walk on Spheres", (width, height), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((0.5, 0.5, 0.5))

    num = 6
    centers = ti.Vector.field(2, dtype=float, shape=num)
    centers[0] = (0.2, 0.2)
    centers[1] = (0.8, 0.3)
    centers[2] = (0.6, 0.5)
    centers[3] = (0.8, 0.8)
    centers[4] = (0.2, 0.7)
    centers[5] = (0.4, 0.4)
    _line = ti.Vector.field(2, dtype=float, shape=2)
    colors = ti.Vector.field(3, dtype=float, shape=(width, height))

    boundary_colors = ti.Vector.field(3, dtype=float, shape=num)
    for i in range(num):
        value = i % 2
        boundary_colors[i] = (value, value, value)

    max_recursion = 10
    recursive_circle_centers = ti.Vector.field(2, dtype=float, shape=max_recursion)
    recursive_circle_radiuses = ti.Vector.field(1, dtype=float, shape=max_recursion)

    sample_pos = ti.Vector.field(2, dtype=float, shape=1)
    sample_pos[0] = (0.5, 0.5)
    _draw_pos = ti.Vector.field(2, dtype=float, shape=1)

    recursive_walk(sample_pos[0])
    
    selected = -1
    gui = window.get_gui()
    frame = 0
    clicked = False
    while window.running:
        if window.is_pressed(ti.ui.LMB):
            sample_pos[0] = window.get_cursor_pos()
            clicked = True
        if frame % 5 == 0 or clicked:
            recursive_walk(sample_pos[0])
            clicked = False

        # Render image
        render()
        canvas.set_image(colors)

        # Draw lines
        for i in range(num):
            _line[0] = centers[i]
            _line[1] = centers[(i + 1) % num]
            canvas.lines(_line, 0.005, color=(boundary_colors[i][0], boundary_colors[i][1], boundary_colors[i][2]))

        # Draw all circles
        canvas.circles(centers, 0.005, color=(0.0, 0.0, 0.0))

        # ---


        for i in range(max_recursion):
            _draw_pos[0] = recursive_circle_centers[i]
            canvas.circles(_draw_pos, recursive_circle_radiuses[i][0], color=(0.9, 0.9, 0.9))

        for i in range(max_recursion):
            _draw_pos[0] = recursive_circle_centers[i]
            canvas.circles(_draw_pos, 0.005, color=(0.0, 1.0, 0.0))

        # Draw sample pos
        canvas.circles(sample_pos, 0.005, color=(0.0, 1.0, 0.0))


        window.show()
        frame += 1
