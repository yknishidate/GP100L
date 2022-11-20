import taichi as ti


def load_obj(fliepath):
    with open(fliepath) as f:
        lines = f.readlines()

    vertex_lines = [line for line in lines if line.startswith('v ')]
    num_vertices = len(vertex_lines)
    face_lines = [line for line in lines if line.startswith('f ')]
    num_faces = len(face_lines)
    print("num_vertices: ", num_vertices)
    print("num_faces: ", num_faces)

    indices = ti.field(int, shape=num_faces * 3)
    vertices = ti.Vector.field(3, dtype=float, shape=num_vertices)

    for i, line in enumerate(vertex_lines):
        vals = line.split()
        vertices[i].x = float(vals[1])
        vertices[i].y = float(vals[2])
        vertices[i].z = float(vals[3])

    for i, line in enumerate(face_lines):
        vals = line.split()
        for j, f in enumerate(vals[1:]):
            w = f.split("/")
            indices[i*3 + j] = int(w[0]) - 1
    return vertices, indices
