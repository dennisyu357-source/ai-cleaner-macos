#!/usr/bin/env python3
"""
macOS应用构建脚本
完整处理从PyInstaller到最终app包的所有步骤
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
def run_command(cmd, description):
    """运行命令并处理错误"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {description}完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败")
        print(f"错误: {e.stderr}")
        return False
def build_macos_app():
    """构建macOS应用"""
    print("=" * 60)
    print("🍎 macOS应用构建脚本")
    print("=" * 60)
    
    # 配置
    app_name = "AI清洗工具2.0"
    app_bundle = f"{app_name}.app"
    main_script = "mac_ai_cleaner.py"
    
    # 检查主脚本
    if not os.path.exists(main_script):
        print(f"❌ 未找到主脚本: {main_script}")
        return False
    
    print(f"📦 应用名称: {app_name}")
    print(f"📦 主脚本: {main_script}")
    
    # 步骤1: 使用PyInstaller构建
    print("\n" + "=" * 60)
    print("步骤1: 使用PyInstaller构建可执行文件")
    print("=" * 60)
    
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", app_name,
        main_script
    ]
    
    if not run_command(pyinstaller_cmd, "PyInstaller构建"):
        return False
    
    # 检查构建结果
    exe_path = Path(f"dist/{app_name}")
    if not exe_path.exists():
        print(f"❌ 未找到可执行文件: {exe_path}")
        return False
    
    exe_size_mb = exe_path.stat().st_size / 1024 / 1024
    print(f"📦 可执行文件大小: {exe_size_mb:.2f} MB")
    
    # 步骤2: 创建app包结构
    print("\n" + "=" * 60)
    print("步骤2: 创建app包结构")
    print("=" * 60)
    
    # 删除旧的app包
    if os.path.exists(app_bundle):
        print(f"🗑️ 删除旧的app包: {app_bundle}")
        shutil.rmtree(app_bundle)
    
    # 创建目录结构
    contents_dir = Path(app_bundle) / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_dir = contents_dir / "Resources"
    
    try:
        macos_dir.mkdir(parents=True, exist_ok=True)
        resources_dir.mkdir(parents=True, exist_ok=True)
        print("✅ app包目录结构创建完成")
    except Exception as e:
        print(f"❌ 创建目录结构失败: {e}")
        return False
    
    # 复制可执行文件
    try:
        shutil.copy(exe_path, macos_dir / app_name)
        print(f"✅ 可执行文件复制完成")
    except Exception as e:
        print(f"❌ 复制可执行文件失败: {e}")
        return False
    
    # 步骤3: 创建Info.plist
    print("\n" + "=" * 60)
    print("步骤3: 创建Info.plist")
    print("=" * 60)
    
    plist_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>AI清洗工具2.0</string>
    <key>CFBundleDisplayName</key>
    <string>AI清洗工具2.0</string>
    <key>CFBundleVersion</key>
    <string>2.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0.0</string>
    <key>CFBundleIdentifier</key>
    <string>com.ai.cleaner</string>
    <key>NSHumanReadableCopyright</key>
    <string>© 2024 AI清洗工具</string>
    <key>CFBundleExecutable</key>
    <string>AI清洗工具2.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSArchitecturePriority</key>
    <array>
        <string>arm64</string>
        <string>x86_64</string>
    </array>
    <key>LSMinimumSystemVersion</key>
    <string>10.15.0</string>
</dict>
</plist>"""
    
    try:
        with open(contents_dir / "Info.plist", "w", encoding="utf-8") as f:
            f.write(plist_content)
        print("✅ Info.plist创建完成")
    except Exception as e:
        print(f"❌ 创建Info.plist失败: {e}")
        return False
    
    # 步骤4: 修复权限
    print("\n" + "=" * 60)
    print("步骤4: 修复文件权限")
    print("=" * 60)
    
    # 设置执行权限
    try:
        os.chmod(macos_dir / app_name, 0o755)
        print("✅ 可执行文件权限设置完成")
    except Exception as e:
        print(f"❌ 设置权限失败: {e}")
        return False
    
    # 步骤5: 移除隔离属性
    print("\n" + "=" * 60)
    print("步骤5: 移除隔离属性")
    print("=" * 60)
    
    if not run_command(["xattr", "-cr", app_bundle], "移除隔离属性"):
        print("⚠️ 移除隔离属性失败，但可能不影响使用")
    
    # 步骤6: 签名应用
    print("\n" + "=" * 60)
    print("步骤6: 签名应用")
    print("=" * 60)
    
    if not run_command(
        ["codesign", "--force", "--deep", "--sign", "-", app_bundle],
        "应用签名"
    ):
        print("⚠️ 签名失败，但可能不影响使用")
    
    # 步骤7: 验证应用
    print("\n" + "=" * 60)
    print("步骤7: 验证应用")
    print("=" * 60)
    
    if not run_command(
        ["codesign", "-vvv", app_bundle],
        "应用验证"
    ):
        print("⚠️ 验证失败，但可能不影响使用")
    
    # 完成
    print("\n" + "=" * 60)
    print("🎉 构建完成！")
    print("=" * 60)
    print(f"📦 应用路径: {app_bundle}")
    print(f"📦 应用大小: {get_app_size(app_bundle):.2f} MB")
    print(f"\n💡 现在可以:")
    print(f"   1. 双击打开应用")
    print(f"   2. 右键点击 → 打开")
    print(f"   3. 如果仍有问题，运行修复脚本")
    
    return True
def get_app_size(app_path):
    """获取应用包大小"""
    total = 0
    for dirpath, dirnames, filenames in os.walk(app_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total += os.path.getsize(fp)
    return total / 1024 / 1024
if __name__ == "__main__":
    try:
        success = build_macos_app()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 构建过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)