# -*- coding: utf-8 -*-
"""生成 onefile 启动图 splash.png（Nuitka --onefile-windows-splash-screen-image 用）。

用 lock_device.ico 的图标 + 应用名 + 「正在启动…」拼一张深色卡片，
首启解压/加载期间由 Nuitka 引导层先显示，避免用户以为「没点成功」。

依赖 Pillow（仅打包机需要，运行时不依赖）：pip install pillow
用法：python scripts\\make_splash.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICO = os.path.join(ROOT, "lock_device.ico")
OUT = os.path.join(ROOT, "splash.png")

W, H = 480, 320          # 启动图建议不超过 ~600x400，过大反而拖慢显示
BG = (24, 24, 27, 255)   # #18181b 深色卡片背景
FG = (240, 240, 245, 255)
SUB = (150, 152, 158, 255)

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("缺少 Pillow：请先 pip install pillow")
    sys.exit(1)


def load_icon():
    """取 ico 里最大的一层（通常 256x256），转 RGBA。"""
    im = Image.open(ICO)
    sizes = getattr(im, "info", {}).get("sizes") or []
    best = None
    for s in sorted(sizes, key=lambda t: t[0] * t[1], reverse=True):
        try:
            im.size = s
            best = im.convert("RGBA").copy()
            break
        except Exception:
            continue
    return best or im.convert("RGBA")


def load_font(size):
    """Windows 微软雅黑；找不到就退回默认字体。"""
    for name in ("msyh.ttc", "msyhbd.ttc", "simhei.ttf"):
        p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", name)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def main():
    card = Image.new("RGBA", (W, H), BG)
    d = ImageDraw.Draw(card)

    # 图标：居中偏上
    icon = load_icon()
    icon = icon.resize((192, 192), Image.LANCZOS)
    card.paste(icon, ((W - 192) // 2, 36), icon)

    # 应用名
    f1 = load_font(30)
    t1 = "专注锁定"
    b1 = d.textbbox((0, 0), t1, font=f1)
    d.text(((W - (b1[2] - b1[0])) // 2, 236), t1, font=f1, fill=FG)

    # 副标题
    f2 = load_font(16)
    t2 = "正在启动…"
    b2 = d.textbbox((0, 0), t2, font=f2)
    d.text(((W - (b2[2] - b2[0])) // 2, 282), t2, font=f2, fill=SUB)

    card.save(OUT, "PNG")
    print("已生成", OUT, f"{W}x{H}")


if __name__ == "__main__":
    main()
