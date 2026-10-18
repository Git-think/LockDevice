# -*- coding: utf-8 -*-
"""独立自测：_sync_installed_version 只应在「从安装目录里启动」时同步 version.txt。

背景：新版单文件在已装机器上启动时，若它抢先把自己的版本号写进 version.txt，
随后的 has_update()（新版 > 新版 不成立）就恒为 False，「发现更新」窗永远不弹。

运行：python tests\\test_sync_installed_version.py
（无需第三方依赖；在临时目录里模拟安装态，不触碰真实 %LOCALAPPDATA% 数据）
"""
import os
import shutil
import sys
import tempfile


def main():
    tmp = tempfile.mkdtemp(prefix="ld_sync_test_")
    # import 前先把目录环境指到临时区，让 ROOT_DIR / INSTALL_FLAG 都落在临时目录
    os.environ["LOCALAPPDATA"] = tmp
    os.environ["ProgramFiles"] = os.path.join(tmp, "PF")
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    failures = []
    try:
        import lock_device as ld

        # ---- 模拟：机器上装着旧版 1.5.2，安装目录 <PF>\LockDevice ----
        install_dir = os.path.join(os.environ["ProgramFiles"], "LockDevice")
        os.makedirs(os.path.join(install_dir, "app"), exist_ok=True)
        app_exe = os.path.join(install_dir, "app", ld._main_name())
        open(app_exe, "w").close()
        os.makedirs(ld.ROOT_DIR, exist_ok=True)
        with open(ld.INSTALL_FLAG, "w", encoding="utf-8") as f:
            f.write(install_dir)
        with open(ld._version_file(), "w", encoding="utf-8") as f:
            f.write("1.5.2")

        ld.VERSION = "1.6.0"

        def version_txt():
            with open(ld._version_file(), "r", encoding="utf-8") as f:
                return f.read().strip()

        # 用例1：新版单文件（外部副本）启动 —— 不得改写 version.txt，且必须判定「有更新」
        ld._self_path = lambda: os.path.join(tmp, "Downloads", "LockDevice-1.6.0-qt.exe")
        ld._sync_installed_version()
        if version_txt() != "1.5.2":
            failures.append("外部副本启动改写了 version.txt：期望 1.5.2，实际 " + version_txt())
        if not ld.has_update():
            failures.append("外部副本启动后 has_update() 应为 True（不然「发现更新」窗不会弹）")

        # 用例2：从安装目录里启动本体 —— 应照常同步为当前版本
        ld._self_path = lambda: app_exe
        ld._sync_installed_version()
        if version_txt() != "1.6.0":
            failures.append("已安装副本启动未同步 version.txt：期望 1.6.0，实际 " + version_txt())

        # 用例3：未安装机器 —— 不动作
        os.remove(ld.INSTALL_FLAG)
        with open(ld._version_file(), "w", encoding="utf-8") as f:
            f.write("1.5.2")
        ld._sync_installed_version()
        if version_txt() != "1.5.2":
            failures.append("未安装机器被改写 version.txt：实际 " + version_txt())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if failures:
        print("FAIL:")
        for m in failures:
            print("  -", m)
        sys.exit(1)
    print("PASS: _sync_installed_version 行为正确")


if __name__ == "__main__":
    main()
