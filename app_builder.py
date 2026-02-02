#!/usr/bin/env python3
"""
创建macOS应用包的Python脚本
避免在YAML中使用多行文本
"""
import os
import shutil
def create_macos_app_bundle():
    """创建macOS应用包"""
    app_name = "AI清洗工具2.0.app"
    exe_name = "AI清洗工具2.0"
    
    print(f"🔄 创建macOS应用包：{app_name}")
    
    # 创建目录结构
    os.makedirs(f"{app_name}/Contents/MacOS", exist_ok=True)
    os.makedirs(f"{app_name}/Contents/Resources", exist_ok=True)
    
    # 复制可执行文件
    exe_src = f"dist/{exe_name}"
    exe_dst = f"{app_name}/Contents/MacOS/{exe_name}"
    
    if os.path.exists(exe_src):
        shutil.copy(exe_src, exe_dst)
        print(f"✅ 复制可执行文件：{exe_src} -> {exe_dst}")
    else:
        raise FileNotFoundError(f"❌ 未找到可执行文件：{exe_src}")
    
    # 创建Info.plist内容
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
        <string>x86_64</string>
        <string>arm64</string>
    </array>
</dict>
</plist>"""
    
    # 写入Info.plist文件
    plist_path = f"{app_name}/Contents/Info.plist"
    with open(plist_path, "w", encoding="utf-8") as f:
        f.write(plist_content)
    
    print(f"✅ 创建Info.plist：{plist_path}")
    
    # 设置权限
    os.chmod(exe_dst, 0o755)
    print(f"✅ 设置可执行权限：{exe_dst}")
    
    print(f"🎉 应用包创建完成：{app_name}")
    return True
if __name__ == "__main__":
    try:
        create_macos_app_bundle()
    except Exception as e:
        print(f"❌ 创建应用包失败：{e}")
        exit(1)
