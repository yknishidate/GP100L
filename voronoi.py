import taichi as ti
from poisson_disk import sample


@ti.func
def find_nearest_point(pos, num_points: int) -> int:
    min_dist = 100.0
    min_point = 0
    for i in range(num_points):
        dist = ti.math.distance(positions[i], pos)
        if dist < min_dist:
            min_dist = dist
            min_point = i
    return min_point


@ti.kernel
def render(num_points: int):
    for i, j in colors:
        pos = ti.Vector([i / width, j / height])
        point = find_nearest_point(pos, num_points)
        value = point / num_points
        colors[i, j] = (value, value, value)


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Voronoi", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))

    width, height = 1024, 1024
    colors = ti.Vector.field(3, dtype=float, shape=(width, height))

    radius = 0.01
    num_points = 0
    num_max_points = 500
    positions = ti.Vector.field(2, dtype=float, shape=num_max_points)

    frame = 0
    while window.running:
        if frame % 5 == 0:
            if num_points != num_max_points:
                num_points += sample(positions, num_points, radius)
            render(num_points)
        canvas.set_image(colors)
        canvas.circles(positions, radius)
        window.show()
        frame += 1
