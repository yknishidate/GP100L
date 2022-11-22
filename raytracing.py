import taichi as ti
import math

ti.init(arch=ti.vulkan)
width, height = 1024, 1024
eps = 0.00001
gui = ti.GUI("Raytracing", res=(width, height), fast_gui=True)
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

LIGHT, DIFFUSE, MIRROR, GLASS = 0, 1, 2, 3
sphere_materials = ti.field(dtype=int, shape=num_spheres)
sphere_materials[0] = DIFFUSE
sphere_materials[1] = DIFFUSE
sphere_materials[2] = LIGHT
sphere_materials[3] = MIRROR


@ti.func
def intersect_sphere(origin, direction, sphere_center, sphere_radius):
    hit_distance = 10000.0
    hit_position = ti.Vector([0.0, 0.0, 0.0])
    hit_normal = ti.Vector([0.0, 0.0, 0.0])
    oc = sphere_center - origin
    b = ti.math.dot(oc, direction)
    det = b * b - ti.math.dot(oc, oc) + sphere_radius * sphere_radius
    if det > 0.0:
        sqrt_det = ti.math.sqrt(det)
        t1, t2 = b - sqrt_det, b + sqrt_det
        if t1 > eps or t2 > eps:
            if t1 > eps:
                hit_distance = t1
            else:
                hit_distance = t2
            hit_position = origin + hit_distance * direction
            hit_normal = ti.math.normalize(hit_position - sphere_center)
    return hit_distance, hit_position, hit_normal


@ti.func
def intersect_spheres(origin, direction):
    hit_distance = 10000.0
    hit_position = ti.Vector([0.0, 0.0, 0.0])
    hit_normal = ti.Vector([0.0, 0.0, 0.0])
    hit_sphere = -1
    for s in range(num_spheres):
        distance, position, normal = intersect_sphere(origin, direction, sphere_centers[s], sphere_radiuses[s])
        if distance < hit_distance:
            hit_distance = distance
            hit_position = position
            hit_normal = normal
            hit_sphere = s
    return hit_distance, hit_position, hit_normal, hit_sphere


@ti.func
def reflect(dir, normal):
    return dir - 2 * ti.math.dot(dir, normal) * normal


@ti.kernel
def render():
    light_position = ti.Vector([10, 10, 10])
    for i, j in colors:
        screen_position = ti.Vector([i / width - 0.5, j / height - 0.5, 0])
        origin = ti.Vector([0.0, 0.0, 1.0])
        direction = ti.math.normalize(screen_position - origin)
        color = ti.Vector([0.0, 0.0, 0.0])
        weight = ti.Vector([1.0, 1.0, 1.0])
        for depth in range(4):
            _, hit_position, hit_normal, hit_sphere = intersect_spheres(origin, direction)
            if hit_sphere == -1:
                color = weight * ti.Vector([0.8, 0.9, 1.0])
                break
            material = sphere_materials[hit_sphere]
            sphere_emission = sphere_emissions[hit_sphere]
            sphere_color = sphere_colors[hit_sphere]
            if material == LIGHT:
                color = weight * sphere_emission
                break
            if material == DIFFUSE:
                light_direction = ti.math.normalize(light_position - hit_position)
                origin = hit_position + hit_normal * 0.001
                hit_sphere = intersect_spheres(origin, light_direction)[3]
                if hit_sphere == -1:
                    color = weight * sphere_color * ti.math.dot(hit_normal, light_direction)
                break
            if material == MIRROR:
                direction = reflect(direction, hit_normal)
                origin = hit_position + direction * 0.001
                weight *= sphere_color

        colors[i, j] = ti.math.clamp(color, 0.0, 1.0)


while gui.running:
    render()
    gui.set_image(colors)
    gui.show()
