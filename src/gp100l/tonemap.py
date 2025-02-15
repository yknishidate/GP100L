import taichi as ti

@ti.func
def hsv_to_rgb(h, s, v):
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    rgb = ti.Vector([0.0, 0.0, 0.0])
    if 0 <= h < 60:
        rgb = ti.Vector([c, x, 0])
    elif 60 <= h < 120:
        rgb = ti.Vector([x, c, 0])
    elif 120 <= h < 180:
        rgb = ti.Vector([0, c, x])
    elif 180 <= h < 240:
        rgb = ti.Vector([0, x, c])
    elif 240 <= h < 300:
        rgb = ti.Vector([x, 0, c])
    else:
        rgb = ti.Vector([c, 0, x])
    return rgb + m

@ti.func
def tonemap_reinhard(color):
    return color / (1.0 + color)

@ti.func
def tonemap_aces_approx_krzysztof_narkowicz(color):
    # ACES Tone Mapping, Krzysztof Narkowicz's version,
    # https://knarkowicz.wordpress.com/2016/01/06/aces-filmic-tone-mapping-curve/
    a = 2.51
    b = 0.03
    c = 2.43
    d = 0.59
    e = 0.14
    return (color * (a * color + b)) / (color * (c * color + d) + e)

@ti.func
def rrt_and_odt_fit(v):
    a = v * (v + 0.0245786) - 0.000090537
    b = v * (0.983729 * v + 0.4329510) + 0.238081
    return a / (b + 1e-5)

@ti.func
def tonemap_aces_approx_stephen_hill(color):
    # ACES Tone Mapping, Stephen Hill's version,
    # https://github.com/TheRealMJP/BakingLab/blob/master/BakingLab/ACES.hlsl
    aces_input_mat = ti.Matrix([[0.59719, 0.35458, 0.04823],
                                [0.07600, 0.90834, 0.01566],
                                [0.02840, 0.13383, 0.83777]])

    aces_output_mat = ti.Matrix([[ 1.60475, -0.53108, -0.07367],
                                 [-0.10208,  1.10813, -0.00605],
                                 [-0.00327, -0.07276,  1.07602]])

    color = aces_input_mat @ color  # ACES入力マトリクス適用
    color = rrt_and_odt_fit(color)  # RRT + ODT 適用
    color = aces_output_mat @ color  # ACES出力マトリクス適用
    return ti.math.clamp(color, 0.0, 1.0)

@ti.func
def tonemap_khronos_pbr_neutral(color):
    # Khronos PBR Tone Mapping,
    # https://modelviewer.dev/examples/tone-mapping.html
    startCompression = 0.8 - 0.04
    desaturation = 0.15

    x = min(color[0], min(color[1], color[2]))
    offset = x - 6.25 * x * x if x < 0.08 else 0.04
    color -= offset

    peak = max(color[0], max(color[1], color[2]))
    retval = color
    if peak >= startCompression:
        d = 1.0 - startCompression
        newPeak = 1.0 - d * d / (peak + d - startCompression)
        color *= newPeak / peak

        g = 1.0 - 1.0 / (desaturation * (peak - newPeak) + 1.0)
        retval = color * (1.0 - g) + newPeak * g
    return retval

@ti.kernel
def render(mode: ti.i32, max_luminance: ti.f32):
    for x, y in pixels:
        hue = (y / height) * 360.0
        luminance = (x / width) * max_luminance
        color = hsv_to_rgb(hue, 1.0, luminance)
        if mode == 1:
            color = tonemap_reinhard(color)
        elif mode == 2:
            color = tonemap_aces_approx_krzysztof_narkowicz(color)
        elif mode == 3:
            color = tonemap_aces_approx_stephen_hill(color)
        elif mode == 4:
            color = tonemap_khronos_pbr_neutral(color)
        else:
            color = ti.math.clamp(color, 0.0, 1.0)
        pixels[x, y] = color

if __name__ == '__main__':
    ti.init(arch=ti.vulkan)

    width, height = 1024, 1024
    pixels = ti.Vector.field(3, dtype=ti.f32, shape=(width, height))

    max_luminance = 30.0
    mode = 1
    labels = ['Clamp', 'Reinhard', 'ACES Approx (Krzysztof Narkowicz)', 'ACES Approx (Stephen Hill)', 'Khronos PBR Neutral']

    gui = ti.GUI("Tonemap Demo", res=(width, height))
    while gui.running:
        for e in gui.get_events():
            if e.key == ti.GUI.ESCAPE:
                gui.running = False
            elif e.key == 'm' and e.type == ti.GUI.PRESS:
                mode = (mode + 1) % 5
            elif e.key == 'w' and e.type == ti.GUI.PRESS:
                max_luminance += 1.0
            elif e.key == 's' and e.type == ti.GUI.PRESS:
                max_luminance = max(1.0, max_luminance - 1.0)
        render(mode, max_luminance)
        gui.set_image(pixels)
        gui.text(f"Mode: {labels[mode]}", pos=(0.01, 0.99), color=0xFFFFFF)
        gui.text(f"Max Luminance: {max_luminance:.1f}", pos=(0.01, 0.95), color=0xFFFFFF)
        gui.show()
