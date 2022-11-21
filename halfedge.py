import taichi as ti


class Vertex:
    def __init__(self, position, edge=-1) -> None:
        self.position = position
        self.edge = edge


class HalfEdge:
    def __init__(self, origin, face=-1, twin=-1, next=-1, prev=-1) -> None:
        self.origin = origin
        self.face = face
        self.twin = twin
        self.next = next
        self.prev = prev


class Face:
    def __init__(self, edge) -> None:
        self.edge = edge


def load_obj(file_path):
    with open(file_path) as f:
        lines = f.readlines()

    vertex_positions = []
    for line in [line for line in lines if line.startswith('v ')]:
        vals = line.split()
        x, y, z = float(vals[1]), float(vals[2]), float(vals[3])
        vertex_positions.append(ti.Vector([x, y, z]))

    face_indices = []
    for f, line in enumerate([line for line in lines if line.startswith('f ')]):
        vals = line.split()
        num_vertices = len(vals) - 1
        indices = []
        for i in range(num_vertices):
            v = int(vals[i + 1].split("/")[0]) - 1
            indices.append(v)
        face_indices.append(indices)
    return vertex_positions, face_indices

def build_half_edges(vertex_positions, face_indices):
    vertices = []
    faces = []
    edges = []
    for pos in vertex_positions:
        vertices.append(Vertex(pos))

    for f, indices in enumerate(face_indices):
        num_vertices = len(indices)
        edge_offset = len(edges)
        for i, v in enumerate(indices):
            edges.append(HalfEdge(v, f))
            vertices[v].edge = edge_offset + i

        for i in range(num_vertices):
            edges[edge_offset + i].next = edge_offset + (i + 1) % num_vertices
            edges[edge_offset + i].prev = edge_offset + (i - 1) % num_vertices

        faces.append(Face(edge_offset))

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
    line_index_field = ti.field(int, shape=len(edges))
    index = 0
    added_edges = []
    for i in range(len(edges)):
        e1 = i
        e2 = edges[i].next

        if edges[e1].twin in added_edges:
            continue
        added_edges.append(e1)

        if e2 != -1:
            v1 = edges[e1].origin
            v2 = edges[e2].origin

            line_index_field[index] = v1
            line_index_field[index + 1] = v2
            index += 2
    return line_index_field

def main():
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Half-Edge", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))
    scene = ti.ui.Scene()
    camera = ti.ui.Camera()

    vertex_positions, face_indices = load_obj("data/torus_quad.obj")
    vertices, faces, edges = build_half_edges(vertex_positions, face_indices)
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

if __name__ == '__main__':
    main()
    