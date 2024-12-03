import taichi as ti
import math


class Vertex:
    def __init__(self, position, edge=-1):
        self.position = position
        self.edge = edge


class HalfEdge:
    def __init__(self, origin, face=-1, twin=-1, next=-1, prev=-1):
        self.origin = origin
        self.face = face
        self.twin = twin
        self.next = next
        self.prev = prev


class Face:
    def __init__(self, edge):
        self.edge = edge


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
    line_index_field = ti.field(int, shape=len(edges*2))
    index = 0
    for i in range(len(edges)):
        e1 = i
        e2 = edges[i].next

        if e2 != -1:
            v1 = edges[e1].origin
            v2 = edges[e2].origin
            line_index_field[index] = v1
            line_index_field[index + 1] = v2
            index += 2
    return line_index_field


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Half-Edge", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))
    scene = ti.ui.Scene()
    camera = ti.ui.Camera()

    # create mesh
    vertex_positions = [ti.Vector([0.0, 0.0, 0.0])]
    face_indices = []
    num = 5
    for i in range(num):
        theta = 360.0 / num * i
        x = math.cos(math.radians(theta))
        y = math.sin(math.radians(theta))
        vertex_positions.append(ti.Vector([x, y, 0.0]))
        print(0, i + 1, ((i + 1) % num) + 1)
        face_indices.append([0, i + 1, ((i + 1) % num) + 1])

    # build half edges
    vertices, faces, edges = build_half_edges(vertex_positions, face_indices)
    vertex_field = convert_to_vertex_field(vertices)
    line_index_field = convert_to_line_index_field(edges)
    print("num vertices:", len(vertices))
    print("num faces:", len(faces))
    print("num edges:", len(edges))

    around_face_edge = 0
    around_vertex_edge = 0
    frame = 0
    while window.running:
        camera.position(0.0, 1.0, 4.0)
        camera.lookat(0.0, 0.0, 0.0)
        scene.set_camera(camera)
        scene.point_light(pos=(0, 1, 2), color=(1, 1, 1))
        scene.ambient_light((0.5, 0.5, 0.5))

        scene.particles(vertex_field, radius=0.02)  # vertex
        scene.lines(vertex_field, width=2, indices=line_index_field)  # edge
        scene.lines(vertex_field, width=6, indices=line_index_field,
                    index_offset=around_face_edge*2, index_count=2,
                    color=(1.0, 0.0, 0.0))  # around face edge (red)
        scene.lines(vertex_field, width=6, indices=line_index_field,
                    index_offset=around_vertex_edge*2, index_count=2,
                    color=(0.0, 0.0, 1.0))  # around vertex edge (blue)

        canvas.scene(scene)
        window.show()

        if frame % 10 == 0:
            # next face edge
            around_face_edge = edges[around_face_edge].next

            # next vertex edge
            twin = edges[around_vertex_edge].twin
            around_vertex_edge = edges[twin].next
        frame += 1
