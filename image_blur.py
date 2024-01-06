import numpy as np
import taichi as ti
import time

@ti.kernel
def blur(src: ti.template(), dst: ti.template()):
    """
    src: ti.field(dtype=float, shape=(w, h, 3)))
    dst: ti.field(dtype=float, shape=(w, h, 3)))
    """
    for i, j, k in src:
        r = 4
        n = 2 * r + 1
        for u, v in ti.ndrange(n, n):
            dst[i, j, k] += src[i + u - r, j + v - r, k]
            # src[i, j, k] += src[i + u - r, j + v - r, k]
        dst[i, j, k] /= n * n
        # src[i, j, k] /= n * n

    

if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    src_img = ti.tools.imread('sample.jpg')
    # print(src_img[0, 0])
    # dst = np.zeros(src.shape, dtype=src.dtype)
    # print(src_img.shape)
    src = ti.field(dtype=float, shape=src_img.shape)
    src.from_numpy(src_img / 255.0)
    dst = ti.field(dtype=float, shape=src_img.shape)
    blur(src, dst)

    # img = src.to_numpy()
    img = dst.to_numpy()
    ti.tools.imshow(img, "JPEG Read Result")
