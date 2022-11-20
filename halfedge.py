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


# NOTE: Obj file must have only quad polygons.
def load_obj(fliepath):

    with open(fliepath) as f:
        lines = f.readlines()

    vertices = []
    faces = []
    edges = []
    for line in [line for line in lines if line.startswith('v ')]:
        vals = line.split()
        x = float(vals[1])
        y = float(vals[2])
        z = float(vals[3])
        vertices.append(Vertex(x, y, z))

    for f, line in enumerate([line for line in lines if line.startswith('f ')]):
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

    for i in range(len(edges)):  # search twins
        e1 = i
        e2 = edges[e1].next
        vi1 = edges[e1].origin
        vi2 = edges[e2].origin
        for j in range(len(edges)):
            e1 = j
            e2 = edges[e1].next
            vj1 = edges[e1].origin
            vj2 = edges[e2].origin
            if vi1 == vj2 and vi2 == vj1:
                edges[i].twin = j
                edges[j].twin = i

    return vertices, faces, edges


def convert_to_vertex_field(vertices):
    vertex_field = ti.Vector.field(3, dtype=float, shape=len(vertices))
    for i in range(len(vertices)):
        vertex_field[i].x = vertices[i].x
        vertex_field[i].y = vertices[i].y
        vertex_field[i].z = vertices[i].z
    return vertex_field


def convert_to_line_index_field(edges):
    line_index_field = ti.field(int, shape=len(edges) * 2)
    for i in range(len(edges)):
        e1 = i
        e2 = edges[i].next
        line_index_field[i * 2 + 0] = edges[e1].origin
        line_index_field[i * 2 + 1] = edges[e2].origin
    return line_index_field


window = ti.ui.Window("Half-Edge", (1024, 1024), vsync=True)
canvas = window.get_canvas()
canvas.set_background_color((1, 1, 1))
scene = ti.ui.Scene()
camera = ti.ui.Camera()

vertices, faces, edges = load_obj("torus_quad.obj")
vertex_field = convert_to_vertex_field(vertices)
line_index_field = convert_to_line_index_field(edges)

line_offset = 0
line_count = 8
while window.running:
    camera.position(0.0, 2.0, 4.0)
    camera.lookat(0.0, 0.0, 0.0)
    scene.set_camera(camera)
    scene.point_light(pos=(0, 1, 2), color=(1, 1, 1))
    scene.ambient_light((0.5, 0.5, 0.5))

    scene.particles(vertex_field, radius=0.01)  # vertex
    scene.lines(vertex_field, width=1, indices=line_index_field)  # edge
    scene.lines(vertex_field, width=4, indices=line_index_field,
                index_offset=line_offset*2, index_count=line_count*2,
                color=(1.0, 0.0, 0.0))  # edge (red)

    canvas.scene(scene)
    window.show()

    line_offset = (line_offset + 1) % len(edges)
