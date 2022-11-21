import taichi as ti
import halfedge as he
import copy


def subdivide(vertices, faces, edges):
    face_points = ti.Vector.field(3, dtype=float, shape=len(faces))
    for f in range(len(faces)):
        sum_vertex = ti.Vector([0.0, 0.0, 0.0])
        e = faces[f].edge
        start_e = e
        count = 0
        while True:  # iterate around a face
            v = edges[e].origin
            sum_vertex += vertices[v].position
            count += 1

            # compute next
            e = edges[e].next
            if e == start_e:
                break
        face_points[f] = sum_vertex / count

    edge_points = ti.Vector.field(3, dtype=float, shape=len(edges))
    for e1 in range(len(edges)):
        e2 = edges[e1].next
        v1 = edges[e1].origin
        v2 = edges[e2].origin
        f1 = edges[e1].face
        twin = edges[e1].twin
        f2 = edges[twin].face
        edge_points[e1] = (vertices[v1].position + vertices[v2].position +
                           face_points[f1] + face_points[f2]) / 4.0

    new_vertices = copy.deepcopy(vertices)
    for v in range(len(vertices)):
        average_face_point = ti.Vector([0.0, 0.0, 0.0])
        average_edge_midpoint = ti.Vector([0.0, 0.0, 0.0])
        e = vertices[v].edge
        start_e = e
        count = 0
        while True:
            # add face point
            f = edges[e].face
            average_face_point += face_points[f]

            # add edge midpoint
            v1 = edges[e].origin
            v2 = edges[edges[e].next].origin
            v1_pos = vertices[v1].position
            v2_pos = vertices[v2].position
            average_edge_midpoint += (v1_pos + v2_pos) / 2.0
            count += 1

            # compute next
            twin = edges[e].twin
            e = edges[twin].next
            if e == start_e:
                break
        average_face_point /= count
        average_edge_midpoint /= count

        # recompute vertex position
        new_position = (average_face_point + 2.0 * average_edge_midpoint +
                        (count - 3.0) * vertices[v].position) / count
        new_vertices[v].position = new_position

    return face_points, edge_points, new_vertices


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Half-Edge", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))
    scene = ti.ui.Scene()
    camera = ti.ui.Camera()
    camera.position(0.8, 1.5, 4.0)
    camera.lookat(0.0, 0.0, 0.0)

    vertices, faces, edges = he.load_obj("data/cube.obj")
    face_points, edge_points, new_vertices = subdivide(vertices, faces, edges)

    vertex_field = he.convert_to_vertex_field(vertices)
    new_vertex_field = he.convert_to_vertex_field(new_vertices)
    line_index_field = he.convert_to_line_index_field(edges)
    while window.running:
        camera.track_user_inputs(window, movement_speed=0.03, hold_key=ti.ui.RMB)
        scene.set_camera(camera)
        scene.point_light(pos=(0, 1, 2), color=(1, 1, 1))
        scene.ambient_light((0.5, 0.5, 0.5))

        scene.particles(vertex_field, radius=0.02)  # vertex
        scene.particles(face_points, radius=0.02, color=(1.0, 0.0, 0.0))  # face points
        scene.particles(edge_points, radius=0.02, color=(0.0, 1.0, 0.0))  # edge points
        scene.particles(new_vertex_field, radius=0.02, color=(0.0, 0.0, 1.0))  # new vertex
        scene.lines(vertex_field, width=2, indices=line_index_field)  # edge

        canvas.scene(scene)
        window.show()
