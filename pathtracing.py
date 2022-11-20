import taichi as ti
import math

ti.init(arch=ti.vulkan)
width, height = 1024, 1024
gui = ti.GUI("Pathtracing", res=(width, height), fast_gui=True)
colors = ti.Vector.field(3, dtype=float, shape=(width, height))

eps = 0.00001
num_spheres = 3
sphere_centers = ti.Vector.field(3, dtype=float, shape=num_spheres)
sphere_centers[0] = ti.Vector([0.1, 0.0, 0.0])
sphere_centers[1] = ti.Vector([0.0, -100.1, 0.0])
sphere_centers[2] = ti.Vector([-0.1, 0.1, -0.2])
sphere_radiuses = ti.field(dtype=float, shape=num_spheres)
sphere_radiuses[0] = 0.1
sphere_radiuses[1] = 100
sphere_radiuses[2] = 0.2
sphere_emissions = ti.Vector.field(3, dtype=float, shape=num_spheres)
sphere_emissions[0] = ti.Vector([1.0, 1.0, 1.0]) * 0.0
sphere_emissions[1] = ti.Vector([1.0, 1.0, 1.0]) * 0.0
sphere_emissions[2] = ti.Vector([1.0, 1.0, 1.0]) * 1.0
sphere_colors = ti.Vector.field(3, dtype=float, shape=num_spheres)
sphere_colors[0] = ti.Vector([1.0, 1.0, 1.0]) * 0.5
sphere_colors[1] = ti.Vector([1.0, 1.0, 1.0]) * 0.9
sphere_colors[2] = ti.Vector([1.0, 1.0, 1.0]) * 0.0


@ti.func
def intersect(ray_origin, ray_direction, sphere_center, sphere_radius):
    result = False
    hit_distance = 0.0
    hit_position = ti.Vector([0.0, 0.0, 0.0])
    hit_normal = ti.Vector([0.0, 0.0, 0.0])
    oc = sphere_center - ray_origin
    b = ti.math.dot(oc, ray_direction)
    det = b * b - ti.math.dot(oc, oc) + sphere_radius * sphere_radius
    if det > 0.0:
        sqrt_det = ti.math.sqrt(det)
        t1 = b - sqrt_det
        t2 = b + sqrt_det
        if t1 > eps or t2 > eps:
            result = True
            if t1 > eps:
                hit_distance = t1
            else:
                hit_distance = t2
            hit_position = ray_origin + hit_distance * ray_direction
            hit_normal = ti.math.normalize(hit_position - sphere_center)
    return result, hit_distance, hit_position, hit_normal


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
            hit_distance = 10000.0
            hit_position = ti.Vector([0.0, 0.0, 0.0])
            hit_normal = ti.Vector([0.0, 0.0, 0.0])
            hit_emission = ti.Vector([0.8, 0.9, 1.0])
            hit_color = ti.Vector([0.0, 0.0, 0.0])
            hit_index = -1
            for s in range(num_spheres):
                result, distance, position, normal = intersect(origin, direction, sphere_centers[s], sphere_radiuses[s])
                if result:
                    if distance < hit_distance:
                        hit_distance = distance
                        hit_position = position
                        hit_normal = normal
                        hit_index = s
                        hit_emission = sphere_emissions[hit_index]
                        hit_color = sphere_colors[hit_index]
            color += weight * hit_emission
            if hit_index == -1:
                break
            direction, pdf = sample_direction(hit_normal)
            origin = hit_position + 0.001 * direction
            brdf = hit_color / math.pi
            weight *= brdf * ti.math.dot(direction, hit_normal) / pdf
        color = ti.math.clamp(color, 0.0, 1.0)
        colors[i, j] = (color + colors[i, j] * frame) / (frame + 1)


frame = 0
while gui.running:
    render(frame)
    gui.set_image(colors)
    gui.show()
    frame += 1
