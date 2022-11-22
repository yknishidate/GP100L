import taichi as ti


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
