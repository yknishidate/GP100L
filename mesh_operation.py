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
        return new_v

    def add_face(self, edge):
        self.faces.append(he.Face(edge))
        return len(self.faces) - 1

    def add_vertex_to_face(self, f, vs, position):
        fp = self.add_vertex(position)
        original_f = f

        # 1. 全ての edge point を face point と結ぶ
        e = self.faces[f].edge
        start_e = e
        added_edges = []
        while True:
            v = self.edges[e].origin
            if v in vs:
                prev = self.edges[e].prev

                new1 = self.add_edge(v, -1)  # v -> fp
                new2 = self.add_edge(fp, -1)  # fp -> v
                added_edges.append(new1)
                added_edges.append(new2)

                # update prev
                self.edges[prev].next = new1

                # update new1
                self.edges[new1].prev = prev
                self.edges[new1].twin = new2

                # update new2
                self.edges[new2].next = e
                self.edges[new2].twin = new1

                # update e
                self.edges[e].prev = new2

            e = self.edges[e].next
            if e == start_e or e == -1:
                break

        # 2. 隣接する edge 同士の next, prev を埋める
        # ex) [(1,2) (3,4) (5,6) (7,0)]
        for i in range(1, len(added_edges) + 1, 2):
            e1 = added_edges[i]
            e2 = added_edges[(i+1) % len(added_edges)]
            self.edges[e1].prev = e2
            self.edges[e2].next = e1
            print(i)

        # 追加した face point を追加した適当な edge につなぐ
        # face point から出る方向であればどれでもいいため
        # added_edges のインデックスが奇数ならOK
        self.vertices[fp].edge = added_edges[1]

        # 3. ループが出来た分の face を追加する
        # 4. 全ての edge の face を更新する
        for i in range(2, len(added_edges), 2):
            e = added_edges[i]
            f = self.add_face(added_edges[i])

            start_e = e
            while True:
                self.edges[e].face = f
                e = self.edges[e].next
                if e == start_e:
                    break

        # 元からある最初のポリゴンの周りのエッジにfaceを設定する
        e = added_edges[0]
        start_e = e
        while True:
            self.edges[e].face = original_f
            e = self.edges[e].next
            if e == start_e:
                break

        return fp


def main():
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Half-Edge", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))
    scene = ti.ui.Scene()
    camera = ti.ui.Camera()
    camera.position(0.8, 1.5, 4.0)
    camera.lookat(0.0, 0.0, 0.0)

    vertices = [
        he.Vertex(1, 1, 0),
        he.Vertex(1, -1, 0),
        he.Vertex(-1, -1, 0),
        he.Vertex(-1, 1, 0)]
    edges = [
        he.HalfEdge(0, face=0, twin=7, next=1, prev=3),
        he.HalfEdge(3, face=0, twin=6, next=2, prev=0),
        he.HalfEdge(2, face=0, twin=5, next=3, prev=1),
        he.HalfEdge(1, face=0, twin=4, next=0, prev=2),
        he.HalfEdge(0, face=-1, twin=3, next=5, prev=7),
        he.HalfEdge(1, face=-1, twin=2, next=6, prev=4),
        he.HalfEdge(2, face=-1, twin=1, next=7, prev=5),
        he.HalfEdge(3, face=-1, twin=0, next=4, prev=6)]
    faces = [he.Face(0)]
    mesh = Mesh(vertices, faces, edges)

    mesh.add_vertex_to_face(0, [0, 1, 2, 3], ti.Vector([0.0, 0.0, 0.0]))
    mesh.add_vertex_to_edge(0, ti.Vector([0.0, 1.5, 0.0]))

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


if __name__ == '__main__':
    main()