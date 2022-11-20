import taichi as ti
ti.init(arch=ti.vulkan)


class Vertex:
    def __init__(self, x, y, z, edge=-1) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.edge = edge


class HalfEdge:
    def __init__(self, origin, twin=-1, face=-1, next=-1, prev=-1) -> None:
        self.origin = origin
        self.face = face
        self.twin = twin
        self.next = next
        self.prev = prev


class Face:
    def __init__(self, edge) -> None:
        self.edge = edge


def load_obj(fliepath):
    """
    NOTE: Obj file must have only quad polygons.
    """

    with open(fliepath) as f:
        lines = f.readlines()

    vertex_lines = [line for line in lines if line.startswith('v ')]
    face_lines = [line for line in lines if line.startswith('f ')]

    vertices = []
    faces = []
    edges = []
    for line in vertex_lines:
        vals = line.split()
        x = float(vals[1])
        y = float(vals[2])
        z = float(vals[3])
        vertices.append(Vertex(x, y, z))

    for f, line in enumerate(face_lines):
        vals = line.split()
        v1 = int(vals[1].split("/")[0]) - 1
        v2 = int(vals[2].split("/")[0]) - 1
        v3 = int(vals[3].split("/")[0]) - 1
        v4 = int(vals[4].split("/")[0]) - 1

        e1 = f * 4 + 0
        e2 = f * 4 + 1
        e3 = f * 4 + 2
        e4 = f * 4 + 3
        edges.append(HalfEdge(v1, face=f))
        edges.append(HalfEdge(v2, face=f))
        edges.append(HalfEdge(v3, face=f))
        edges.append(HalfEdge(v4, face=f))

        vertices[v1].edge = e1
        vertices[v2].edge = e2
        vertices[v3].edge = e3
        vertices[v4].edge = e4

        edges[e1].next = e2
        edges[e2].next = e3
        edges[e3].next = e4
        edges[e4].next = e1

        edges[e1].prev = e4
        edges[e2].prev = e1
        edges[e3].prev = e2
        edges[e4].prev = e3

        faces.append(Face(e1))

    return vertices, faces, edges


vertices, faces, edges = load_obj("cube.obj")

num_faces = len(faces)
num_edges = len(edges)
face_points = ti.Vector.field(3, dtype=float, shape=num_faces)
edge_points = ti.Vector.field(3, dtype=float, shape=num_faces)


# @ti.kernel
# def subdivide():
#     for i in range(num_faces):
#         face = faces[i]
#         v1 = vertices[face.v1]
#         v2 = vertices[face.v2]
#         v3 = vertices[face.v3]
#         v4 = vertices[face.v4]
#         face_points[i] = (v1 + v2 + v3 + v4) / 4.0

# for i in range(num_edges):
#     edge = edges[i]
#     fp1, fp2 = face_points[edge.f], face_points[edge.f2]
#     v1, v2 = vertices[edge.v1], vertices[edge.v2]
#     edge_points[i] = (fp1 + fp2 + v1 + v2) / 4.0

# num_vertices = vertices.shape[0]
# for i in range(num_vertices):
#     v = vertices[i]
#     f = face_points[]


# num_edges = len(edges)
# line_indices = ti.field(int, shape=num_edges * 2)
# print("num_edges:", num_edges)
# for i in range(num_edges):
#     line_indices[i * 2 + 0] = edges[i].v1
#     line_indices[i * 2 + 1] = edges[i].v2

window = ti.ui.Window("Halfedge", (1024, 1024), vsync=True)
canvas = window.get_canvas()
canvas.set_background_color((1, 1, 1))
scene = ti.ui.Scene()
camera = ti.ui.Camera()
camera.track_user_inputs(window, movement_speed=0.03, hold_key=ti.ui.RMB)

# subdivide()

# Convert list to ti.Vector.field
vertex_field = ti.Vector.field(3, dtype=float, shape=len(vertices))
for i in range(len(vertices)):
    vertex_field[i].x = vertices[i].x
    vertex_field[i].y = vertices[i].y
    vertex_field[i].z = vertices[i].z

line_index_field = ti.field(int, shape=len(edges) * 2)
for i in range(len(edges)):
    e1 = i
    e2 = edges[e1].next
    line_index_field[i * 2 + 0] = edges[e1].origin
    line_index_field[i * 2 + 1] = edges[e2].origin

while window.running:
    camera.position(2.0, 3.0, 5.0)
    camera.lookat(0.0, 0.0, 0.0)
    scene.set_camera(camera)

    scene.point_light(pos=(0, 1, 2), color=(1, 1, 1))
    scene.ambient_light((0.5, 0.5, 0.5))

    # TODO: draw ndarray?
    scene.particles(vertex_field, radius=0.05)
    scene.lines(vertex_field, width=4, indices=line_index_field)

    # scene.particles(face_points, radius=0.05, color=(1.0, 0.0, 0.0))

    canvas.scene(scene)
    window.show()
