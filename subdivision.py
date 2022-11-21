import taichi as ti
import halfedge as he


def subdivide(vertices, faces, edges):
    face_points = ti.Vector.field(3, dtype=float, shape=len(faces))
    for i in range(len(faces)):
        sum_vertex = ti.Vector([0.0, 0.0, 0.0])
        e = faces[i].edge
        edge = edges[e]
        for _ in range(4):
            v = edge.origin
            sum_vertex += vertices[v].position
            edge = edges[edge.next]
        face_points[i] = sum_vertex / 4.0

    return face_points


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Half-Edge", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))
    scene = ti.ui.Scene()
    camera = ti.ui.Camera()

    vertices, faces, edges = he.load_obj("data/cube.obj")
    face_points = subdivide(vertices, faces, edges)

    vertex_field = he.convert_to_vertex_field(vertices)
    line_index_field = he.convert_to_line_index_field(edges)
    while window.running:
        camera.position(0.8, 1.5, 4.0)
        camera.lookat(0.0, 0.0, 0.0)
        scene.set_camera(camera)
        scene.point_light(pos=(0, 1, 2), color=(1, 1, 1))
        scene.ambient_light((0.5, 0.5, 0.5))

        scene.particles(vertex_field, radius=0.02)  # vertex
        scene.particles(face_points, radius=0.02, color=(1.0, 0.0, 0.0))  # face points
        scene.lines(vertex_field, width=2, indices=line_index_field)  # edge

        canvas.scene(scene)
        window.show()
