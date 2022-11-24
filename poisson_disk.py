import taichi as ti


@ti.func
def exist_neighbors(pos: ti.template(), num_active_particles: int, radius: float) -> bool:
    found = False
    for i in range(num_active_particles):
        p = positions[i]
        vec = p - pos
        dist = ti.sqrt(vec.x * vec.x + vec.y * vec.y)
        if dist < radius:
            found = True
    return found


@ti.kernel
def sample(num_active_particles: int, radius: float):
    for i in range(10):
        pos = ti.Vector([ti.random(), ti.random()])
        if not exist_neighbors(pos, num_active_particles, radius * 4):
            positions[num_active_particles] = pos


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("SPH", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))

    radius = 0.01
    num_particles = 1000
    num_active_particles = 0
    positions = ti.Vector.field(2, dtype=float, shape=num_particles)

    while window.running:
        if num_active_particles != num_particles:
            sample(num_active_particles, radius)
            num_active_particles += 1

        canvas.circles(positions, radius)
        window.show()
