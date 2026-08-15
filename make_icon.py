# -*- coding: utf-8 -*-
"""
纯 Python 生成 App 图标（不依赖任何第三方库）
生成一个紫色渐变 + 白色对勾的圆角图标，输出 512 和 192 两个尺寸
"""
import zlib, struct, math

def make_png(path, size):
    # 1. 构建像素数据（RGB）
    rows = []
    # 渐变两端颜色（对应 App 主题）
    c1 = (102, 126, 234)   # #667eea
    c2 = (118, 75, 162)    # #764ba2

    # 对勾的两个线段端点（归一化坐标）
    A = (0.30, 0.53)
    B = (0.46, 0.68)
    C = (0.73, 0.36)

    # 线段粗度（占边长比例）
    thick = 0.075
    half = thick / 2

    def dist_to_seg(px, py, ax, ay, bx, by):
        # 点到线段的最短距离
        vx, vy = bx - ax, by - ay
        wx, wy = px - ax, py - ay
        l2 = vx*vx + vy*vy
        if l2 == 0:
            return math.hypot(px-ax, py-ay)
        t = max(0, min(1, (wx*vx + wy*vy) / l2))
        return math.hypot(px - (ax + t*vx), py - (ay + t*vy))

    for y in range(size):
        row = bytearray()
        # 每行前加一个过滤器字节 0
        row.append(0)
        fy = y / (size - 1)
        for x in range(size):
            fx = x / (size - 1)

            # 对角渐变
            t = (fx + fy) / 2
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)

            # 圆角：四角透明（用 alpha 通道控制）
            corner_r = 0.22 * size
            alpha = 255
            for (cx, cy) in [(corner_r, corner_r),
                             (size - corner_r, corner_r),
                             (corner_r, size - corner_r),
                             (size - corner_r, size - corner_r)]:
                d = math.hypot(x - cx, y - cy)
                if d > corner_r:
                    alpha = 0
                    break

            # 画白色对勾
            if alpha == 255:
                d1 = dist_to_seg(fx, fy, A[0], A[1], B[0], B[1])
                d2 = dist_to_seg(fx, fy, B[0], B[1], C[0], C[1])
                if min(d1, d2) < half:
                    r, g, b = 255, 255, 255

            row.append(r)
            row.append(g)
            row.append(b)
            row.append(alpha)
        rows.append(bytes(row))

    raw = b''.join(rows)

    # 2. 用 zlib 压缩
    def chunk(tag, data):
        c = tag + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)  # 8bit RGBA
    png = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', zlib.compress(raw, 9))
           + chunk(b'IEND', b''))

    with open(path, 'wb') as f:
        f.write(png)
    print(f"  生成 {path} ({size}x{size})")

print("正在生成图标……")
make_png(r"d:\English\my-first-app\icon-512.png", 512)
make_png(r"d:\English\my-first-app\icon-192.png", 192)
print("✅ 图标生成完成")
