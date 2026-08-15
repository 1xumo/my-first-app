# -*- coding: utf-8 -*-
"""
生成 App 图标：紫色渐变背景 + 白色对勾（完整不透明正方形）
输出 512x512 和 192x192 两个 PNG
"""
import zlib, struct, math

def make_png(path, size):
    c1 = (102, 126, 234)   # #667eea
    c2 = (118, 75, 162)    # #764ba2

    # 对勾的两个线段（归一化坐标，在中心安全区域内）
    A = (0.28, 0.52)
    B = (0.45, 0.68)
    C = (0.74, 0.34)
    thick = 0.10          # 对勾粗度（占边长比例）
    half = thick / 2

    def dist_to_seg(px, py, ax, ay, bx, by):
        vx, vy = bx - ax, by - ay
        wx, wy = px - ax, py - ay
        l2 = vx*vx + vy*vy
        if l2 == 0:
            return math.hypot(px-ax, py-ay)
        t = max(0.0, min(1.0, (wx*vx + wy*vy) / l2))
        return math.hypot(px - (ax + t*vx), py - (ay + t*vy))

    rows = []
    for y in range(size):
        row = bytearray(b'\x00')   # filter type 0
        fy = y / (size - 1)
        for x in range(size):
            fx = x / (size - 1)
            # 对角渐变
            t = (fx + fy) / 2
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            # 画白色对勾
            d1 = dist_to_seg(fx, fy, A[0], A[1], B[0], B[1])
            d2 = dist_to_seg(fx, fy, B[0], B[1], C[0], C[1])
            if min(d1, d2) < half:
                r, g, b = 255, 255, 255
            row += bytes((r, g, b, 255))   # 完全不透明
        rows.append(bytes(row))

    raw = b''.join(rows)

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

print("正在生成图标（修复版）……")
make_png(r"d:\English\my-first-app\icon-512.png", 512)
make_png(r"d:\English\my-first-app\icon-192.png", 192)
print("✅ 完成")
