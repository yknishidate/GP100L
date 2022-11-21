import taichi as ti
import halfedge as he
import copy


def compute_face_points(vertices, faces, edges):
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


def compute_edge_points(vertices, edges, face_points):
    # edge_points = ti.Vector.field(3, dtype=float, shape=len(edges))
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

        edge_points[e1] = (vertices[v1].position + vertices[v2].position +
                           face_points[f1] + face_points[f2]) / 4.0
    return edge_points


def move_vertices(vertices, edges, face_points):
    moved_vertices = copy.deepcopy(vertices)
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
        moved_vertices[v].position = new_position

    return moved_vertices


def subdivide(vertices, faces, edges):
    face_points = compute_face_points(vertices, faces, edges)
    print("face_points:", face_points.shape[0])
    edge_points = compute_edge_points(vertices, edges, face_points)
    print("edge_points:", edge_points.shape[0])
    moved_vertices = move_vertices(vertices, edges, face_points)

    # copy moved vertices
    new_vertices = copy.deepcopy(moved_vertices)

    # add face points
    f_offset = len(new_vertices)
    for f in range(face_points.shape[0]):
        position = face_points[f]
        new_vertices.append(he.Vertex(position.x, position.y, position.z))

    # add edge points
    e_offset = len(new_vertices)
    for e in range(edge_points.shape[0]):
        position = edge_points[e]
        new_vertices.append(he.Vertex(position.x, position.y, position.z))

    # vertices: [moved_vertices][face_points][edge_points]
    # connect face points and edge points
    new_edges = []
    for e in range(len(edges)):
        fp1 = edges[e].face + f_offset
        ep = e + e_offset

        # TODO: fix
        new_edges.append(he.HalfEdge(fp1, -1))
        new_edges[-1].next = e * 2 + 1
        new_edges.append(he.HalfEdge(ep, -1))
        # new_edges[-1].next = e * 2

    return face_points, edge_points, moved_vertices, new_vertices, new_edges


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Half-Edge", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))
    scene = ti.ui.Scene()
    camera = ti.ui.Camera()
    camera.position(0.8, 1.5, 4.0)
    camera.lookat(0.0, 0.0, 0.0)

    # # create quad
    # vertices = []
    # vertices.append(he.Vertex(1, 1, 0))
    # vertices.append(he.Vertex(1, -1, 0))
    # vertices.append(he.Vertex(-1, -1, 0))
    # vertices.append(he.Vertex(-1, 1, 0))
    # edges = []
    # edges.append(he.HalfEdge(0, face=0, twin=7, next=1, prev=3))
    # edges.append(he.HalfEdge(1, face=0, twin=6, next=2, prev=0))
    # edges.append(he.HalfEdge(2, face=0, twin=5, next=3, prev=1))
    # edges.append(he.HalfEdge(3, face=0, twin=4, next=0, prev=2))

    # edges.append(he.HalfEdge(0, face=-1, twin=3, next=5, prev=7))
    # edges.append(he.HalfEdge(3, face=-1, twin=2, next=6, prev=4))
    # edges.append(he.HalfEdge(2, face=-1, twin=1, next=7, prev=5))
    # edges.append(he.HalfEdge(1, face=-1, twin=0, next=4, prev=6))

    # faces = []
    # faces.append(he.Face(0))

    vertices, faces, edges = he.load_obj("data/cube.obj")
    # face_points, edge_points, moved_vertices, new_vertices, new_edges = subdivide(vertices, faces, edges)

    vertex_field = he.convert_to_vertex_field(vertices)
    # moved_vertex_field = he.convert_to_vertex_field(moved_vertices)
    line_index_field = he.convert_to_line_index_field(edges)
    print("edges, line_field:", len(edges), line_index_field.shape[0])
    # new_vertex_field = he.convert_to_vertex_field(new_vertices)
    # new_line_index_field = he.convert_to_line_index_field(new_edges)
    while window.running:
        camera.track_user_inputs(window, movement_speed=0.03, hold_key=ti.ui.RMB)
        scene.set_camera(camera)
        scene.point_light(pos=(0, 1, 2), color=(1, 1, 1))
        scene.ambient_light((0.5, 0.5, 0.5))

        scene.particles(vertex_field, radius=0.02)  # vertex
        # scene.particles(face_points, radius=0.02, color=(1.0, 0.0, 0.0))  # face points
        # scene.particles(edge_points, radius=0.02, color=(0.0, 1.0, 0.0))  # edge points
        # scene.particles(moved_vertex_field, radius=0.02, color=(0.0, 0.0, 1.0))  # new vertex
        scene.lines(vertex_field, width=2, indices=line_index_field)  # edge
        # scene.lines(new_vertex_field, width=2, indices=new_line_index_field, color=(0.0, 0.0, 1.0))  # new edge

        canvas.scene(scene)
        window.show()
