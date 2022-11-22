import taichi as ti
import math
import raytracing as rt

width, height = 1024, 1024
eps = 0.00001


@ti.func
def sample_direction(normal):
    w = normal
    u = ti.math.normalize(ti.math.cross(ti.Vector([0.0, 1.0, 0.0]), w))
    if ti.abs(w.x) < eps:
        u = ti.math.normalize(ti.math.cross(ti.Vector([1.0, 0.0, 0.0]), w))
    v = ti.math.cross(w, u)
    r1 = 2.0 * math.pi * ti.random()
    r2 = ti.random()
    dir = ti.math.normalize(u * ti.cos(r1) * ti.sqrt(r2) +
                            v * ti.sin(r1) * ti.sqrt(r2) +
                            w * ti.sqrt(1.0 - r2))
    pdf = ti.math.dot(dir, normal) / math.pi
    return dir, pdf


@ti.kernel
def render(frame: int):
    for i, j in colors:
        screen_position = ti.Vector([i / width - 0.5, j / height - 0.5, 0])
        origin = ti.Vector([0.0, 0.0, 1.0])
        direction = ti.math.normalize(screen_position - origin)
        weight = ti.Vector([1.0, 1.0, 1.0])
        color = ti.Vector([0.0, 0.0, 0.0])
        for depth in range(8):
            _, hit_position, hit_normal, hit_sphere = rt.intersect_spheres(origin, direction, sphere_centers, sphere_radiuses)
            if hit_sphere == -1:
                color += weight * ti.Vector([0.8, 0.9, 1.0])
                break
            hit_emission = sphere_emissions[hit_sphere]
            hit_color = sphere_colors[hit_sphere]
            color += weight * hit_emission
            if hit_sphere == -1:
                break
            direction, pdf = sample_direction(hit_normal)
            origin = hit_position + 0.001 * direction
            brdf = hit_color / math.pi
            weight *= brdf * ti.math.dot(direction, hit_normal) / pdf
        color = ti.math.clamp(color, 0.0, 1.0)
        colors[i, j] = (color + colors[i, j] * frame) / (frame + 1)


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    gui = ti.GUI("Pathtracing", res=(width, height), fast_gui=True)
    colors = ti.Vector.field(3, dtype=float, shape=(width, height))
    num_spheres = 3
    sphere_centers = ti.Vector.field(3, dtype=float, shape=num_spheres)
    sphere_centers[0] = (0.1, 0.0, 0.0)
    sphere_centers[1] = (0.0, -100.1, 0.0)
    sphere_centers[2] = (-0.1, 0.1, -0.2)
    sphere_radiuses = ti.field(dtype=float, shape=num_spheres)
    sphere_radiuses[0] = 0.1
    sphere_radiuses[1] = 100
    sphere_radiuses[2] = 0.2
    sphere_emissions = ti.Vector.field(3, dtype=float, shape=num_spheres)
    sphere_emissions[2] = (1.0, 1.0, 1.0)
    sphere_colors = ti.Vector.field(3, dtype=float, shape=num_spheres)
    sphere_colors[0] = (0.5, 0.5, 0.5)
    sphere_colors[1] = (0.9, 0.9, 0.9)
    frame = 0
    while gui.running:
        render(frame)
        gui.set_image(colors)
        gui.show()
        frame += 1
