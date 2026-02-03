#!/usr/bin/env python3
"""
自动化测试脚本
验证构建流程是否正常
"""
import os
import sys
import subprocess
from pathlib import Path
def test_dependencies():
    """测试依赖是否安装"""
    print("=" * 60)
    print("🧪 测试依赖")
    print("=" * 60)
    
    dependencies = [
        ("Python", "python3 --version"),
        ("PyInstaller", "pyinstaller --version"),
        ("codesign", "which codesign"),
        ("xattr", "which xattr"),
    ]
    
    all_ok = True
    for name, cmd in dependencies:
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            version = result.stdout.strip().split('\n')[-1]
            print(f"✅ {name}: {version}")
        except Exception as e:
            print(f"❌ {name}: 未安装")
            all_ok = False
    
    return all_ok
def test_build_script():
    """测试构建脚本"""
    print("\n" + "=" * 60)
    print("🧪 测试构建脚本")
    print("=" * 60)
    
    if not os.path.exists("build_mac_app.py"):
        print("❌ 构建脚本不存在")
        return False
    
    print("✅ 构建脚本存在")
    
    # 检查脚本语法
    try:
        result = subprocess.run(
            ["python3", "-m", "py_compile", "build_mac_app.py"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ 构建脚本语法正确")
        return True
    except Exception as e:
        print(f"❌ 构建脚本语法错误: {e}")
        return False
def test_main_script():
    """测试主脚本"""
    print("\n" + "=" * 60)
    print("🧪 测试主脚本")
    print("=" * 60)
    
    if not os.path.exists("mac_ai_cleaner.py"):
        print("❌ 主脚本不存在")
        return False
    
    print("✅ 主脚本存在")
    
    # 检查脚本语法
    try:
        result = subprocess.run(
            ["python3", "-m", "py_compile", "mac_ai_cleaner.py"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ 主脚本语法正确")
        return True
    except Exception as e:
        print(f"❌ 主脚本语法错误: {e}")
        return False
def test_tool_script():
    """测试工具脚本"""
    print("\n" + "=" * 60)
    print("🧪 测试工具脚本")
    print("=" * 60)
    
    if not os.path.exists("mac_app_tool.py"):
        print("❌ 工具脚本不存在")
        return False
    
    print("✅ 工具脚本存在")
    
    # 检查脚本语法
    try:
        result = subprocess.run(
            ["python3", "-m", "py_compile", "mac_app_tool.py"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ 工具脚本语法正确")
        return True
    except Exception as e:
        print(f"❌ 工具脚本语法错误: {e}")
        return False
def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 自动化测试")
    print("=" * 60)
    
    tests = [
        ("依赖测试", test_dependencies),
        ("构建脚本测试", test_build_script),
        ("主脚本测试", test_main_script),
        ("工具脚本测试", test_tool_script),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}测试失败: {e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("📋 测试总结")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试通过！可以开始构建应用。")
    else:
        print("\n⚠️ 部分测试失败，请检查问题。")
    
    return all_passed
if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)