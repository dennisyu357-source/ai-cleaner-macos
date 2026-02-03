#!/usr/bin/env python3
"""
macOS应用工具集
包含诊断、修复、验证功能
"""
import os
import sys
import subprocess
from pathlib import Path
class MacAppTool:
    def __init__(self, app_path):
        self.app_path = Path(app_path).resolve()
        self.app_name = self.app_path.name
        self.contents_path = self.app_path / "Contents"
        self.macos_path = self.contents_path / "MacOS"
        self.executable_path = None
        self.info_plist_path = self.contents_path / "Info.plist"
        
        # 查找可执行文件
        if self.macos_path.exists():
            for file in self.macos_path.iterdir():
                if file.is_file():
                    self.executable_path = file
                    break
    
    def diagnose(self):
        """诊断应用"""
        print("=" * 60)
        print("🔍 应用诊断")
        print("=" * 60)
        
        issues = []
        
        # 检查应用包
        if not self.app_path.exists():
            issues.append("❌ 应用包不存在")
            return issues
        
        print(f"✅ 应用包存在: {self.app_path}")
        
        # 检查Contents目录
        if not self.contents_path.exists():
            issues.append("❌ Contents目录缺失")
            return issues
        
        print(f"✅ Contents目录存在")
        
        # 检查MacOS目录
        if not self.macos_path.exists():
            issues.append("❌ MacOS目录缺失")
            return issues
        
        print(f"✅ MacOS目录存在")
        
        # 检查可执行文件
        if not self.executable_path:
            issues.append("❌ 可执行文件不存在")
            return issues
        
        print(f"✅ 可执行文件存在: {self.executable_path.name}")
        
        # 检查Info.plist
        if not self.info_plist_path.exists():
            issues.append("❌ Info.plist缺失")
            return issues
        
        print(f"✅ Info.plist存在")
        
        # 检查权限
        if not os.access(self.executable_path, os.X_OK):
            issues.append("❌ 可执行文件无执行权限")
        else:
            print(f"✅ 可执行文件有执行权限")
        
        # 检查签名
        try:
            result = subprocess.run(
                ["codesign", "-d", str(self.app_path)],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                print(f"✅ 应用已签名")
            else:
                issues.append("⚠️ 应用未签名或签名无效")
        except Exception as e:
            issues.append(f"⚠️ 检查签名失败: {e}")
        
        # 检查隔离属性
        try:
            result = subprocess.run(
                ["xattr", "-l", str(self.app_path)],
                capture_output=True,
                text=True,
                check=False
            )
            if "com.apple.quarantine" in result.stdout:
                issues.append("⚠️ 发现隔离属性")
            else:
                print(f"✅ 无隔离属性")
        except Exception as e:
            issues.append(f"⚠️ 检查隔离属性失败: {e}")
        
        return issues
    
    def fix(self):
        """修复应用"""
        print("\n" + "=" * 60)
        print("🔧 应用修复")
        print("=" * 60)
        
        fixes = []
        
        # 修复权限
        try:
            os.chmod(self.executable_path, 0o755)
            fixes.append("✅ 执行权限已设置")
        except Exception as e:
            fixes.append(f"❌ 设置权限失败: {e}")
        
        # 移除隔离属性
        try:
            subprocess.run(["xattr", "-cr", str(self.app_path)], check=True)
            fixes.append("✅ 隔离属性已移除")
        except Exception as e:
            fixes.append(f"⚠️ 移除隔离属性失败: {e}")
        
        # 签名应用
        try:
            subprocess.run(
                ["codesign", "--force", "--deep", "--sign", "-", str(self.app_path)],
                check=True
            )
            fixes.append("✅ 应用已签名")
        except Exception as e:
            fixes.append(f"⚠️ 签名失败: {e}")
        
        return fixes
    
    def verify(self):
        """验证应用"""
        print("\n" + "=" * 60)
        print("✅ 应用验证")
        print("=" * 60)
        
        try:
            result = subprocess.run(
                ["codesign", "-vvv", str(self.app_path)],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                print("✅ 应用验证通过")
                return True
            else:
                print("❌ 应用验证失败")
                print(f"错误: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 验证失败: {e}")
            return False
def main():
    if len(sys.argv) < 2:
        print("用法: python mac_app_tool.py <app_path> [diagnose|fix|verify]")
        print("示例:")
        print("  python mac_app_tool.py ~/Downloads/AI清洗工具2.0.app diagnose")
        print("  python mac_app_tool.py ~/Downloads/AI清洗工具2.0.app fix")
        print("  python mac_app_tool.py ~/Downloads/AI清洗工具2.0.app verify")
        sys.exit(1)
    
    app_path = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else "all"
    
    tool = MacAppTool(app_path)
    
    if action in ["diagnose", "all"]:
        issues = tool.diagnose()
        if issues:
            print("\n⚠️ 发现以下问题:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("\n✅ 诊断完成，未发现问题")
    
    if action in ["fix", "all"]:
        fixes = tool.fix()
        print("\n修复结果:")
        for fix in fixes:
            print(f"  {fix}")
    
    if action in ["verify", "all"]:
        tool.verify()
    
    print(f"\n📁 应用路径: {app_path}")
    print(f"💡 现在可以尝试:")
    print(f"   1. 双击打开应用")
    print(f"   2. 右键点击 → 打开")
    print(f"   3. 如果仍有问题，在终端中运行查看详细错误")
if __name__ == "__main__":
    main()