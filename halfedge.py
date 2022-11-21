import taichi as ti


class Vertex:
    def __init__(self, x, y, z) -> None:
        self.position = ti.Vector([x, y, z])
        self.edge = -1


class HalfEdge:
    def __init__(self, origin, face) -> None:
        self.origin = origin
        self.face = face
        self.twin = -1
        self.next = -1
        self.prev = -1


class Face:
    def __init__(self, edge) -> None:
        self.edge = edge


def load_obj(file_path):
    with open(file_path) as f:
        lines = f.readlines()

    vertices = []
    faces = []
    edges = []
    for line in [line for line in lines if line.startswith('v ')]:
        vals = line.split()
        vertices.append(Vertex(float(vals[1]), float(vals[2]), float(vals[3])))

    for f, line in enumerate([line for line in lines if line.startswith('f ')]):
        vals = line.split()
        es = []
        for i in range(4):  # NOTE: only quad polygons
            v = int(vals[i + 1].split("/")[0]) - 1
            es.append(f * 4 + i)
            edges.append(HalfEdge(v, f))
            vertices[v].edge = es[i]

        edges[es[0]].next = es[1]
        edges[es[1]].next = es[2]
        edges[es[2]].next = es[3]
        edges[es[3]].next = es[0]

        edges[es[0]].prev = es[3]
        edges[es[1]].prev = es[0]
        edges[es[2]].prev = es[1]
        edges[es[3]].prev = es[2]

        faces.append(Face(es[0]))

    for ei1 in range(len(edges)):  # search twins
        ei2 = edges[ei1].next
        vi1 = edges[ei1].origin
        vi2 = edges[ei2].origin
        for ej1 in range(ei1, len(edges)):
            ej2 = edges[ej1].next
            vj1 = edges[ej1].origin
            vj2 = edges[ej2].origin
            if vi1 == vj2 and vi2 == vj1:
                edges[ei1].twin = ej1
                edges[ej1].twin = ei1

    return vertices, faces, edges


def convert_to_vertex_field(vertices):
    vertex_field = ti.Vector.field(3, dtype=float, shape=len(vertices))
    for i in range(len(vertices)):
        vertex_field[i] = vertices[i].position
    return vertex_field


def convert_to_line_index_field(edges):
    line_index_field = ti.field(int, shape=len(edges) * 2)
    for i in range(len(edges)):
        e1 = i
        e2 = edges[i].next
        line_index_field[i * 2 + 0] = edges[e1].origin
        line_index_field[i * 2 + 1] = edges[e2].origin
    return line_index_field


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Half-Edge", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))
    scene = ti.ui.Scene()
    camera = ti.ui.Camera()

    vertices, faces, edges = load_obj("data/torus_quad.obj")
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

        scene.particles(vertex_field, radius=0.02)  # vertex
        scene.lines(vertex_field, width=2, indices=line_index_field)  # edge
        scene.lines(vertex_field, width=6, indices=line_index_field,
                    index_offset=line_offset*2, index_count=line_count*2,
                    color=(1.0, 0.0, 0.0))  # edge (red)

        canvas.scene(scene)
        window.show()
        line_offset = (line_offset + 1) % len(edges)
