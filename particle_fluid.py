import taichi as ti
import math


@ti.kernel
def initialize():
    for i in ti.grouped(positions):
        positions[i].x = ti.random(float) * 0.1 + 0.1
        positions[i].y = ti.random(float) * 0.1 + 0.8
        velocities[i] = [0.02, -0.01]


@ti.func
def spline_kernel(r, h):
    q = ti.math.length(r) / h
    alpha = 10.0 / (7.0 * math.pi * h**2)
    value = 0.0
    if 0.0 <= q <= 1.0:
        value = alpha * (1.0 - 3.0/2.0*q**2 + 3.0/4.0*q**3)
    elif q <= 2.0:
        value = alpha * (1.0/4.0*(2.0 - q)**3)
    return value


@ti.func
def spline_kernel_gradient(r, h):
    q = ti.math.length(r) / h
    alpha = 45.0 / (14.0 * math.pi * h**4)
    value = ti.math.vec2(0.0)
    if 0.0 <= q <= 1.0:
        value = alpha * (q - 4.0/3.0) * r
    elif q <= 2.0:
        value = -(1.0/3.0) * (2.0 - q)**2 * (h / ti.math.length(r)) * r
    return value


@ti.kernel
def update(num_active_particles: int):
    mass = 1.0
    for i in range(num_active_particles):
        # Compute density
        density = 0.0
        for j in range(num_active_particles):
            density += mass * spline_kernel(positions[i] - positions[j], radius)
        densities[i] = density

        # Compute pressure
        stiffness = 0.00007
        pressures[i] = max(stiffness * densities[i], 0.0)

    for i in range(num_active_particles):
        # Compute force
        force = ti.math.vec2(0.0)
        force.y -= 0.98  # gravity
        for j in range(num_active_particles):
            pi = pressures[i]
            pj = pressures[j]
            grad = spline_kernel_gradient(positions[i] - positions[j], radius)
            force -= mass / densities[j] * (pi + pj) / 2.0 * grad

        # Compute acceleration / velocity / position
        acceleration = force / mass
        velocities[i] += acceleration * 0.0004  # delta time
        positions[i] += velocities[i]

        # Handle collision
        restitution = 0.4
        if positions[i].x <= 0.0 or 1.0 <= positions[i].x:
            velocities[i].x *= -restitution
            positions[i].x = ti.math.clamp(positions[i].x, 0.01, 0.99)
        elif positions[i].y <= 0.0:
            velocities[i].y *= -restitution
            positions[i].y = ti.math.max(positions[i].y, 0.01)

        # Compute color
        colors[i] = (0.7 - pressures[i], 0.7 - pressures[i], 1.0)


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Particle-based fluid", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))

    radius = 0.03
    num_particles = 1000
    num_active_particles = 0
    positions = ti.Vector.field(2, dtype=float, shape=num_particles)
    densities = ti.field(dtype=float, shape=num_particles)
    pressures = ti.field(dtype=float, shape=num_particles)
    velocities = ti.Vector.field(2, dtype=float, shape=num_particles)
    colors = ti.Vector.field(3, dtype=float, shape=num_particles)
    initialize()
    while window.running:
        num_active_particles = min(num_active_particles + 5, num_particles)
        update(num_active_particles)
        canvas.circles(positions, radius / 2.0, per_vertex_color=colors)
        window.show()
