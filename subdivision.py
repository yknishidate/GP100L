import taichi as ti
import halfedge as he
import copy
from mesh_operation import Mesh


def compute_face_points(mesh):
    vertices = mesh.vertices
    faces = mesh.faces
    edges = mesh.edges
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
    return face_points


def compute_edge_points(mesh, face_points):
    edges = mesh.edges
    vertices = mesh.vertices
    edge_points = ti.Vector.field(3, dtype=float, shape=len(edges) // 2)
    added_edges = []
    for e1 in range(len(edges)):
        if edges[e1].twin in added_edges:
            continue
        added_edges.append(e1)

        e2 = edges[e1].next

        v1 = edges[e1].origin
        v2 = edges[e2].origin

        f1 = edges[e1].face
        f2 = edges[edges[e1].twin].face

        position = (vertices[v1].position + vertices[v2].position + face_points[f1] + face_points[f2]) / 4.0
        index = len(added_edges) - 1
        edge_points[index] = position
    return edge_points, added_edges


def move_vertices(mesh, face_points):
    vertices = mesh.vertices
    edges = mesh.edges
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

        new_position = (average_face_point + 2.0 * average_edge_midpoint +
                        (count - 3.0) * vertices[v].position) / count
        vertices[v].position = new_position


def subdivide(mesh):
    face_points = compute_face_points(mesh)
    edge_points, added_edges = compute_edge_points(mesh, face_points)
    move_vertices(mesh, face_points)

    # vertices: [original][edge_points]
    added_vertices = []
    for i, e in enumerate(added_edges):
        v = mesh.add_vertex_to_edge(e, edge_points[i])
        added_vertices.append(v)

    for f in range(len(mesh.faces)):
        added_vertices_in_face = []
        for v in added_vertices:
            ev = mesh.vertices[v].edge
            et = mesh.edges[ev].twin
            fv1 = mesh.edges[ev].face
            fv2 = mesh.edges[et].face
            if f == fv1 or f == fv2:
                added_vertices_in_face.append(v)

        position = face_points[f]
        mesh.add_vertex_to_face(f, added_vertices_in_face, position)

    return face_points, edge_points


def main():
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Subdivision", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))
    scene = ti.ui.Scene()
    camera = ti.ui.Camera()
    camera.position(0.8, 1.5, 4.0)
    camera.lookat(0.0, 0.0, 0.0)

    vertices, faces, edges = he.load_obj("data/cube.obj")
    mesh = Mesh(vertices, faces, edges)

    face_points, edge_points = subdivide(mesh)
    face_points, edge_points = subdivide(mesh)
    face_points, edge_points = subdivide(mesh)

    # # original mesh
    # vertex_field = he.convert_to_vertex_field(vertices)
    # line_index_field = he.convert_to_line_index_field(edges)

    # new mesh
    new_vertex_field = he.convert_to_vertex_field(vertices)
    new_line_index_field = he.convert_to_line_index_field(edges)

    # moved_vertex_field = he.convert_to_vertex_field(moved_vertices)
    # new_vertex_field = he.convert_to_vertex_field(new_vertices)
    # new_line_index_field = he.convert_to_line_index_field(new_edges)

    while window.running:
        camera.track_user_inputs(window, movement_speed=0.03, hold_key=ti.ui.RMB)
        scene.set_camera(camera)
        scene.point_light(pos=(0, 1, 2), color=(1, 1, 1))
        scene.ambient_light((0.5, 0.5, 0.5))

        # original mesh
        # scene.particles(vertex_field, radius=0.02)  # vertex
        # scene.lines(vertex_field, width=2, indices=line_index_field)  # edge

        # new mesh
        scene.particles(new_vertex_field, radius=0.02, color=(0.0, 0.0, 1.0))  # vertex
        scene.lines(new_vertex_field, width=2, indices=new_line_index_field, color=(0.0, 0.0, 1.0))  # edge

        scene.particles(face_points, radius=0.02, color=(1.0, 0.0, 0.0))  # face points
        scene.particles(edge_points, radius=0.02, color=(0.0, 1.0, 0.0))  # edge points
        # scene.particles(moved_vertex_field, radius=0.02, color=(0.0, 0.0, 1.0))  # new vertex
        # scene.lines(new_vertex_field, width=2, indices=new_line_index_field, color=(0.0, 0.0, 1.0))  # new edge

        canvas.scene(scene)
        window.show()


if __name__ == '__main__':
    main()
