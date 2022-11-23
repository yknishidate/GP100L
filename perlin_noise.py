import taichi as ti

ti.init(arch=ti.vulkan)
width, height = 1024, 1024
p = ti.field(dtype=int, shape=512)


@ti.func
def fade(t: float) -> float:
    return t * t * t * (t * (t * 6 - 15) + 10)


@ti.func
def grad(hash: int, x: float, y: float, z: float) -> float:
    value = 0.0
    hash = hash & 0xF
    if hash == 0x0:
        value = x + y
    elif hash == 0x1:
        value = -x + y
    elif hash == 0x2:
        value = x - y
    elif hash == 0x3:
        value = -x - y
    elif hash == 0x4:
        value = x + z
    elif hash == 0x5:
        value = -x + z
    elif hash == 0x6:
        value = x - z
    elif hash == 0x7:
        value = -x - z
    elif hash == 0x8:
        value = y + z
    elif hash == 0x9:
        value = -y + z
    elif hash == 0xA:
        value = y - z
    elif hash == 0xB:
        value = -y - z
    elif hash == 0xC:
        value = y + x
    elif hash == 0xD:
        value = -y + z
    elif hash == 0xE:
        value = y - x
    elif hash == 0xF:
        value = -y - z
    return value


@ti.func
def lerp(x, y, t):
    return x * (1 - t) + y * t


@ti.func
def perlin(x: float, y: float, z: float) -> float:
    xi = int(x) & 255
    yi = int(y) & 255
    zi = int(z) & 255

    # local coord
    xf = x - int(x)
    yf = y - int(y)
    zf = z - int(z)

    u = fade(xf)
    v = fade(yf)
    w = fade(zf)

    # hash
    xj = xi + 1
    yj = yi + 1
    zj = zi + 1
    aaa = p[p[p[xi] + yi] + zi]
    aba = p[p[p[xi] + yj] + zi]
    aab = p[p[p[xi] + yi] + zj]
    abb = p[p[p[xi] + yj] + zj]
    baa = p[p[p[xj] + yi] + zi]
    bba = p[p[p[xj] + yj] + zi]
    bab = p[p[p[xj] + yi] + zj]
    bbb = p[p[p[xj] + yj] + zj]

    x1 = lerp(grad(aaa, xf, yf, zf), grad(baa, xf-1, yf, zf), u)
    x2 = lerp(grad(aba, xf, yf-1, zf), grad(bba, xf-1, yf-1, zf), u)
    y1 = lerp(x1, x2, v)

    x1 = lerp(grad(aab, xf, yf, zf-1), grad(bab, xf-1, yf, zf-1), u)
    x2 = lerp(grad(abb, xf, yf-1, zf-1), grad(bbb, xf-1, yf-1, zf-1), u)
    y2 = lerp(x1, x2, v)

    return (lerp(y1, y2, w) + 1) / 2


@ti.kernel
def render(size: int):
    for i, j in colors:
        value = perlin(i / size, j / size, 0.34)
        colors[i, j] = (value, value, value)


if __name__ == '__main__':
    window = ti.ui.Window("Perlin noise", res=(width, height))
    canvas = window.get_canvas()
    colors = ti.Vector.field(3, dtype=float, shape=(width, height))

    permutation = [
        51, 160, 137, 91, 90, 15, 131, 13, 201, 95, 96, 53, 194, 233, 7, 225, 140,
        36, 103, 30, 69, 142, 8, 99, 37, 240, 21, 10, 23, 190, 6, 148, 247, 120,
        234, 75, 0, 26, 197, 62, 94, 252, 219, 203, 117, 35, 11, 32, 57, 177, 33,
        88, 237, 149, 56, 87, 174, 20, 125, 136, 171, 168, 68, 175, 74, 165, 71,
        134, 139, 48, 27, 166, 77, 146, 158, 231, 83, 111, 229, 122, 60, 211, 133,
        230, 220, 105, 92, 41, 55, 46, 245, 40, 244, 102, 143, 54, 65, 25, 63, 161,
        1, 216, 80, 73, 209, 76, 132, 187, 208, 89, 18, 169, 200, 196, 135, 130,
        116, 188, 159, 86, 164, 100, 109, 198, 173, 186, 3, 64, 52, 217, 226, 250,
        124, 123, 5, 202, 38, 147, 118, 126, 255, 82, 85, 212, 207, 206, 59, 227,
        47, 16, 58, 17, 182, 189, 28, 42, 223, 183, 170, 213, 119, 248, 152, 2, 44,
        154, 163, 70, 221, 153, 101, 155, 167, 43, 172, 9, 129, 22, 39, 253, 19, 98,
        108, 110, 79, 113, 224, 232, 178, 185, 112, 104, 218, 246, 97, 228, 251, 34,
        242, 193, 238, 210, 144, 12, 191, 179, 162, 241, 81, 51, 145, 235, 249, 14,
        239, 107, 49, 192, 214, 31, 181, 199, 106, 157, 184, 84, 204, 176, 115, 121,
        50, 45, 127, 4, 150, 254, 138, 236, 205, 93, 222, 114, 67, 29, 24, 72, 243,
        141, 128, 195, 78, 66, 215, 61, 156, 180]

    for x in range(512):
        p[x] = permutation[x % 256]

    render(64)
    gui = window.get_gui()
    old_size = 64
    while window.running:
        new_size = gui.slider_int("Size", old_size, 1, 128)
        if new_size != old_size:
            render(new_size)
            old_size = new_size
        canvas.set_image(colors)
        window.show()
