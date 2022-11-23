import taichi as ti
import random


@ti.func
def fade(t: float) -> float:
    return t * t * t * (t * (t * 6 - 15) + 10)


@ti.func
def grad(hash: int, x: float, y: float, z: float) -> float:
    value = 0.0
    hash = hash & 0xF
    if hash == 0x0: value = x + y
    elif hash == 0x1: value = -x + y
    elif hash == 0x2: value = x - y
    elif hash == 0x3: value = -x - y
    elif hash == 0x4: value = x + z
    elif hash == 0x5: value = -x + z
    elif hash == 0x6: value = x - z
    elif hash == 0x7: value = -x - z
    elif hash == 0x8: value = y + z
    elif hash == 0x9: value = -y + z
    elif hash == 0xA: value = y - z
    elif hash == 0xB: value = -y - z
    elif hash == 0xC: value = y + x
    elif hash == 0xD: value = -y + z
    elif hash == 0xE: value = y - x
    elif hash == 0xF: value = -y - z
    return value


@ti.func
def lerp(x, y, t):
    return x * (1 - t) + y * t


@ti.func
def perlin(x: float, y: float, z: float) -> float:
    xi = int(x) & 255
    yi = int(y) & 255
    zi = int(z) & 255
    xf = x - int(x)
    yf = y - int(y)
    zf = z - int(z)
    u = fade(xf)
    v = fade(yf)
    w = fade(zf)

    aaa = p[p[p[xi] + yi] + zi]
    aba = p[p[p[xi] + yi+1] + zi]
    aab = p[p[p[xi] + yi] + zi+1]
    abb = p[p[p[xi] + yi+1] + zi+1]
    baa = p[p[p[xi+1] + yi] + zi]
    bba = p[p[p[xi+1] + yi+1] + zi]
    bab = p[p[p[xi+1] + yi] + zi+1]
    bbb = p[p[p[xi+1] + yi+1] + zi+1]

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
    ti.init(arch=ti.vulkan)
    width, height = 1024, 1024
    window = ti.ui.Window("Perlin noise", res=(width, height))
    canvas = window.get_canvas()
    colors = ti.Vector.field(3, dtype=float, shape=(width, height))

    permutation = list(range(0, 256))
    random.shuffle(permutation)
    p = ti.field(dtype=int, shape=512)
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
