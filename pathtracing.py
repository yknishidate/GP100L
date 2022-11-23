import taichi as ti
import math
from raytracing import intersect_spheres, reflect


@ti.func
def sample_sky_image(direction):
    theta = ti.math.acos(direction.y)
    phi = ti.math.atan2(direction.z, direction.x)
    if phi < 0:
        phi += 2.0 * math.pi

    width, height = sky_image.shape[0], sky_image.shape[1]
    i = int(phi / (2.0 * math.pi) * width)
    j = height - int(theta / math.pi * height)
    return sky_image[i, j] / 255.0


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
            _, hit_position, hit_normal, hit_sphere = intersect_spheres(origin, direction, sphere_centers, sphere_radiuses)

            if hit_sphere == -1:
                sky_color = sample_sky_image(direction)
                color += weight * sky_color * 2.0
                break

            hit_emission = sphere_emissions[hit_sphere]
            hit_color = sphere_colors[hit_sphere]
            hit_material = sphere_materials[hit_sphere]
            if hit_material == LIGHT:
                color += weight * hit_emission
            elif hit_material == DIFFUSE:
                direction, pdf = sample_direction(hit_normal)
                origin = hit_position + 0.001 * direction
                brdf = hit_color / math.pi
                weight *= brdf * ti.math.dot(direction, hit_normal) / pdf
            elif hit_material == MIRROR:
                direction = reflect(direction, hit_normal)
                origin = hit_position + 0.001 * direction
                weight *= hit_color

        color = ti.math.clamp(color, 0.0, 1.0)
        colors[i, j] = (color + colors[i, j] * frame) / (frame + 1)


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    width, height = 1024, 1024
    eps = 0.00001
    LIGHT, DIFFUSE, MIRROR = 0, 1, 2
    image_data = ti.tools.imread("data/modern_buildings_2_2k.hdr", 3)
    sky_image = ti.Vector.field(3, dtype=float, shape=(image_data.shape[0], image_data.shape[1]))
    sky_image.from_numpy(image_data)

    gui = ti.GUI("Pathtracing", res=(width, height), fast_gui=True)
    colors = ti.Vector.field(3, dtype=float, shape=(width, height))
    num_spheres = 4
    sphere_centers = ti.Vector.field(3, dtype=float, shape=num_spheres)
    sphere_centers[0] = (0.0, -100.1, 0.0)
    sphere_centers[1] = (0.2, 0.0, 0.0)
    sphere_centers[2] = (-0.2, 0.0, 0.0)
    sphere_centers[3] = (0.0, 0.0, 0.0)
    sphere_radiuses = ti.field(dtype=float, shape=num_spheres)
    sphere_radiuses[0] = 100
    sphere_radiuses[1] = 0.1
    sphere_radiuses[2] = 0.1
    sphere_radiuses[3] = 0.1
    sphere_emissions = ti.Vector.field(3, dtype=float, shape=num_spheres)
    sphere_emissions[2] = (1.0, 1.0, 1.0)
    sphere_colors = ti.Vector.field(3, dtype=float, shape=num_spheres)
    sphere_colors[0] = (0.9, 0.9, 0.9)
    sphere_colors[1] = (1.0, 0.6, 0.6)
    sphere_colors[3] = (0.8, 0.8, 0.8)
    sphere_materials = ti.field(dtype=int, shape=num_spheres)
    sphere_materials[0] = DIFFUSE
    sphere_materials[1] = DIFFUSE
    sphere_materials[2] = LIGHT
    sphere_materials[3] = MIRROR

    frame = 0
    while gui.running:
        render(frame)
        gui.set_image(colors)
        gui.show()
        frame += 1
