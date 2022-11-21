import taichi as ti
import halfedge as he


class Mesh:
    def __init__(self, vertices, faces, edges) -> None:
        self.vertices = vertices
        self.faces = faces
        self.edges = edges

    def add_vertex(self, position):
        self.vertices.append(he.Vertex(position.x, position.y, position.z))
        return len(self.vertices) - 1

    def add_edge(self, v, f):
        self.edges.append(he.HalfEdge(v, f))
        return len(self.edges) - 1

    def add_vertex_to_edge(self, e, position):
        new_v = self.add_vertex(position)

        old_e1 = e
        old_e2 = self.edges[old_e1].twin

        old_n1 = self.edges[old_e1].next
        old_n2 = self.edges[old_e2].next

        old_f1 = self.edges[old_e1].face
        old_f2 = self.edges[old_e2].face

        new_e1 = self.add_edge(new_v, old_f1)
        new_e2 = self.add_edge(new_v, old_f2)

        self.edges[old_n1].prev = new_e1
        self.edges[old_n2].prev = new_e2

        self.edges[new_e1].next = old_n1
        self.edges[new_e2].next = old_n2

        self.edges[old_e1].next = new_e1
        self.edges[old_e2].next = new_e2

        self.edges[new_e1].prev = old_e1
        self.edges[new_e2].prev = old_e2

        self.edges[old_e1].twin = new_e2
        self.edges[old_e2].twin = new_e1

        self.edges[new_e1].twin = old_e2
        self.edges[new_e2].twin = old_e1

        self.vertices[new_v].edge = new_e1


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
    mesh = Mesh(vertices, faces, edges)

    mesh.add_vertex_to_edge(0, ti.Vector([0.0, 1.0, 0.0]))
    mesh.add_vertex_to_edge(1, ti.Vector([-0.5, 1.0, 0.0]))

    vertex_field = he.convert_to_vertex_field(mesh.vertices)
    line_index_field = he.convert_to_line_index_field(mesh.edges)
    while window.running:
        camera.track_user_inputs(window, movement_speed=0.03, hold_key=ti.ui.RMB)
        scene.set_camera(camera)
        scene.point_light(pos=(0, 1, 2), color=(1, 1, 1))
        scene.ambient_light((0.5, 0.5, 0.5))

        scene.particles(vertex_field, radius=0.02)  # vertex
        scene.lines(vertex_field, width=2, indices=line_index_field)  # edge

        canvas.scene(scene)
        window.show()
