import taichi as ti


@ti.kernel
def update_positions():
    angle = 0.0
    ti.loop_config(serialize=True)
    for joint in (range(1, num_joints)):
        angle += angles[joint - 1]
        vec = ti.Vector([length * ti.cos(angle),
                         length * ti.sin(angle)])
        joints[joint] = joints[joint - 1] + vec


@ti.kernel
def update_angle(joint: int):
    last = num_joints - 1
    to_target = ti.math.normalize(target[0] - joints[joint])
    to_last = ti.math.normalize(joints[last] - joints[joint])
    angle_target = ti.math.atan2(to_target.x, to_target.y)
    angle_last = ti.math.atan2(to_last.x, to_last.y)
    angles[joint] -= angle_target - angle_last


if __name__ == '__main__':
    ti.init(arch=ti.vulkan)
    window = ti.ui.Window("Inverse kinematics", (1024, 1024), vsync=True)
    canvas = window.get_canvas()
    canvas.set_background_color((1, 1, 1))

    length = 0.25
    num_joints = 4
    radius = 0.05
    joints = ti.Vector.field(2, dtype=float, shape=num_joints)
    angles = ti.field(dtype=float, shape=num_joints - 1)
    joints[0] = (0.3, 0.3)

    joints_indices = ti.field(dtype=int, shape=(num_joints - 1) * 2)
    for i in range(num_joints):
        joints_indices[i * 2] = i
        joints_indices[i * 2 + 1] = i + 1

    target = ti.Vector.field(2, dtype=float, shape=1)

    gui = window.get_gui()
    update_positions()
    while window.running:
        canvas.circles(joints, radius)
        canvas.lines(joints, 0.02, joints_indices)

        target[0] = window.get_cursor_pos()
        canvas.circles(target, radius, color=(1.0, 0.0, 0.0))

        for i in range(3):
            for joint in [2, 1, 0]:
                update_angle(joint)
                update_positions()

        if window.get_event(ti.ui.PRESS):
            if window.event.key == 's':
                window.save_image("docs/images/inverse_kinematics.jpg")
        window.show()
