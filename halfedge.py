import taichi as ti
ti.init(arch=ti.vulkan)


class Edge:
    def __init__(self, v1, v2, f) -> None:
        self.v1 = v1
        self.v2 = v2
        self.f = f


class Face:
    def __init__(self, v1, v2, v3, v4) -> None:
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.v4 = v4


def load_obj(fliepath):
    with open(fliepath) as f:
        lines = f.readlines()

    vertex_lines = [line for line in lines if line.startswith('v ')]
    num_vertices = len(vertex_lines)
    face_lines = [line for line in lines if line.startswith('f ')]

    vertices = ti.Vector.field(3, dtype=float, shape=num_vertices)
    for i, line in enumerate(vertex_lines):
        vals = line.split()
        vertices[i].x = float(vals[1])
        vertices[i].y = float(vals[2])
        vertices[i].z = float(vals[3])

    faces = []
    edges = []
    for f, line in enumerate(face_lines):
        vals = line.split()
        v1 = int(vals[1].split("/")[0]) - 1
        v2 = int(vals[2].split("/")[0]) - 1
        v3 = int(vals[3].split("/")[0]) - 1
        v4 = int(vals[4].split("/")[0]) - 1
        faces.append(Face(v1, v2, v3, v4))
        edges.append(Edge(v1, v2, f))
        edges.append(Edge(v2, v3, f))
        edges.append(Edge(v3, v4, f))
        edges.append(Edge(v4, v1, f))

    return vertices, faces, edges


vertices, faces, edges = load_obj("cube.obj")

num_faces = len(faces)
num_edges = len(edges)
face_points = ti.Vector.field(3, dtype=float, shape=num_faces)
edge_points = ti.Vector.field(3, dtype=float, shape=num_faces)


# @ti.kernel
def subdivide():
    for i in range(num_faces):
        face = faces[i]
        v1 = vertices[face.v1]
        v2 = vertices[face.v2]
        v3 = vertices[face.v3]
        v4 = vertices[face.v4]
        face_points[i] = (v1 + v2 + v3 + v4) / 4.0

    # for i in range(num_edges):
    #     edge = edges[i]
    #     fp1, fp2 = face_points[edge.f], face_points[edge.f2]
    #     v1, v2 = vertices[edge.v1], vertices[edge.v2]
    #     edge_points[i] = (fp1 + fp2 + v1 + v2) / 4.0

    # num_vertices = vertices.shape[0]
    # for i in range(num_vertices):
    #     v = vertices[i]
    #     f = face_points[]


num_edges = len(edges)
line_indices = ti.field(int, shape=num_edges * 2)
print("num_edges:", num_edges)
for i in range(num_edges):
    line_indices[i * 2 + 0] = edges[i].v1
    line_indices[i * 2 + 1] = edges[i].v2

window = ti.ui.Window("Halfedge", (1024, 1024), vsync=True)
canvas = window.get_canvas()
canvas.set_background_color((1, 1, 1))
scene = ti.ui.Scene()
camera = ti.ui.Camera()
camera.track_user_inputs(window, movement_speed=0.03, hold_key=ti.ui.RMB)

subdivide()

while window.running:
    camera.position(2.0, 3.0, 5.0)
    camera.lookat(0.0, 0.0, 0.0)
    scene.set_camera(camera)

    scene.point_light(pos=(0, 1, 2), color=(1, 1, 1))
    scene.ambient_light((0.5, 0.5, 0.5))

    scene.particles(vertices, radius=0.05)
    scene.lines(vertices, width=4, indices=line_indices)

    scene.particles(face_points, radius=0.05, color=(1.0, 0.0, 0.0))

    canvas.scene(scene)
    window.show()
