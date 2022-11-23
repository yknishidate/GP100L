import taichi as ti
import halfedge as he
from mesh_operation import Mesh
from obj_loader import load_obj


def compute_face_points(mesh):
    face_points = ti.Vector.field(3, dtype=float, shape=len(mesh.faces))
    for f in range(len(mesh.faces)):
        sum_vertex = ti.Vector([0.0, 0.0, 0.0])
        count = 0
        for e in mesh.all_edges_around_face(f):
            v = mesh.edges[e].origin
            sum_vertex += mesh.vertices[v].position
            count += 1
        face_points[f] = sum_vertex / count
    return face_points


def compute_edge_points(mesh, face_points):
    edge_points = ti.Vector.field(3, dtype=float, shape=len(mesh.edges) // 2)
    for i, e1 in enumerate(mesh.all_unique_edges()):
        v1 = mesh.origin_vertex(e1)
        v2 = mesh.next_vertex(e1)
        f1 = mesh.left_face(e1)
        f2 = mesh.right_face(e1)
        v1_pos = mesh.vertices[v1].position
        v2_pos = mesh.vertices[v2].position

        position = (v1_pos + v2_pos + face_points[f1] + face_points[f2]) / 4.0
        edge_points[i] = position
    return edge_points


def move_vertices(mesh, face_points):
    vertices = mesh.vertices
    edges = mesh.edges
    moved_positions = []
    for v in range(len(vertices)):
        sum_face_point = ti.Vector([0.0, 0.0, 0.0])
        sum_edge_midpoint = ti.Vector([0.0, 0.0, 0.0])

        count = 0
        for e in mesh.all_edges_around_vertex(v):
            # add face point
            f = edges[e].face
            sum_face_point += face_points[f]

            # add edge midpoint
            v1 = mesh.origin_vertex(e)
            v2 = mesh.next_vertex(e)
            v1_pos = vertices[v1].position
            v2_pos = vertices[v2].position
            sum_edge_midpoint += (v1_pos + v2_pos) / 2.0

            count += 1

        fp = sum_face_point / count
        ep = sum_edge_midpoint / count
        vp = vertices[v].position
        moved_positions.append((fp + 2.0 * ep + (count - 3.0) * vp) / count)

    for v in range(len(vertices)):
        vertices[v].position = moved_positions[v]


def subdivide(mesh):
    face_points = compute_face_points(mesh)
    edge_points = compute_edge_points(mesh, face_points)
    move_vertices(mesh, face_points)

    vertex_positions = []
    # add original vertices
    for v in range(len(mesh.vertices)):
        vertex_positions.append(mesh.vertices[v].position)

    # add edge points
    edge_to_edge_points = {}
    for i, e in enumerate(mesh.all_unique_edges()):
        vertex_positions.append(edge_points[i])
        twin = mesh.edges[e].twin
        edge_to_edge_points[e] = len(vertex_positions) - 1
        edge_to_edge_points[twin] = len(vertex_positions) - 1

    # add face points
    face_to_face_points = {}
    for f in range(len(mesh.faces)):
        vertex_positions.append(face_points[f])
        face_to_face_points[f] = len(vertex_positions) - 1

        # added_vertices_in_face = []
        # for v in range(num_original_vertices, len(mesh.vertices)):
        #     if mesh.is_inner_of_face(v, f):
        #         added_vertices_in_face.append(v)

    face_indices = []
    for f in range(len(mesh.faces)):
        es = [e for e in mesh.all_edges_around_face(f)]
        vs = [mesh.edges[e].origin for e in es]
        for i in range(len(vs)):
            indices = [vs[i],
                       edge_to_edge_points[es[i]],
                       face_to_face_points[f],
                       edge_to_edge_points[es[i-1]]]
            face_indices.append(indices)
    mesh.vertices, mesh.faces, mesh.edges = he.build_half_edges(vertex_positions, face_indices)
    return face_points, edge_points


def main():
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Subdivision", (1024, 1024), vsync=True)
    gui = window.get_gui()
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))
    scene = ti.ui.Scene()
    camera = ti.ui.Camera()
    camera.position(0.0, 0.0, 4.0)
    camera.lookat(0.0, 0.0, 0.0)

    vertex_positions, face_indices = load_obj("data/cube.obj")
    vertices, faces, edges = he.build_half_edges(vertex_positions, face_indices)
    mesh = Mesh(vertices, faces, edges)
    vertex_field = he.convert_to_vertex_field(vertices)
    index_field = he.convert_to_line_index_field(edges)

    face_points, edge_points = subdivide(mesh)
    new_vertex_field = he.convert_to_vertex_field(mesh.vertices)
    new_index_field = he.convert_to_line_index_field(mesh.edges)

    while window.running:
        camera.track_user_inputs(window, movement_speed=0.03, hold_key=ti.ui.RMB)
        scene.set_camera(camera)
        scene.point_light(pos=(0, 1, 2), color=(1, 1, 1))
        scene.ambient_light((0.5, 0.5, 0.5))

        if gui.button("Subdivide"):
            face_points, edge_points = subdivide(mesh)
            new_vertex_field = he.convert_to_vertex_field(mesh.vertices)
            new_index_field = he.convert_to_line_index_field(mesh.edges)

        # original mesh
        scene.particles(vertex_field, radius=0.02)
        scene.lines(vertex_field, width=2, indices=index_field)

        # new mesh
        scene.particles(new_vertex_field, radius=0.02, color=(0.0, 0.0, 1.0))
        scene.lines(new_vertex_field, width=2, indices=new_index_field, color=(0.0, 0.0, 1.0))

        # face points / edge points
        scene.particles(face_points, radius=0.02, color=(1.0, 0.0, 0.0))
        scene.particles(edge_points, radius=0.02, color=(0.0, 1.0, 0.0))

        canvas.scene(scene)
        window.show()


if __name__ == '__main__':
    main()
