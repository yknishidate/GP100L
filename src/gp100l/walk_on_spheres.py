import taichi as ti
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
        if dist < min_distance:
            min_distance = dist
            argmin = i
    return vec2(min_distance, float(argmin))

@ti.func
def sample_on_circle(center: vec2, radius: float) -> vec2:
    angle = ti.random() * 2.0 * tm.pi
    x = tm.cos(angle) * radius
    y = tm.sin(angle) * radius
    return center + (x, y)

@ti.func
def recursive_walk(sample_pos: vec2) -> int:
    curr_pos = vec2(sample_pos[0], sample_pos[1])
    boundary = -1

    ti.loop_config(serialize=True)
    for _ in range(max_recursion):
        result = distance_from_boundaries(curr_pos)
        dist = result[0]
        # NOTE: 本来は dist が十分小さければ打ち切る。taichiの都合で省略している。
        boundary = int(result[1])
        curr_pos = sample_on_circle(curr_pos, dist)
    return boundary

@ti.kernel
def render():
    for i, j in colors:
        num_samples = 100
        sum_value = vec3(0.0)
        count = 0
        for _ in range(num_samples):
            screen_position = vec2([i / width, j / height])
            boundary = recursive_walk(screen_position)
            if boundary != -1:
                sum_value += boundary_colors[boundary]
                count += 1
        colors[i, j] = sum_value / float(count)

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
    
    gui = window.get_gui()
    frame = 0
    while window.running:
        # Render image
        render()
        canvas.set_image(colors)

        # Draw lines
        for i in range(num):
            _line[0] = centers[i]
            _line[1] = centers[(i + 1) % num]
            canvas.lines(_line, 0.005, color=(boundary_colors[i][0], boundary_colors[i][1], boundary_colors[i][2]))

        # Draw all circles
        canvas.circles(centers, 0.005, color=(0.0, 0.0, 0.8))

        window.show()
