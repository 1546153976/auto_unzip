#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本 - 验证程序基本功能
"""

import os
import sys
import json

def test_imports():
    """测试导入"""
    print("测试导入...")
    try:
        import tkinter
        print("✓ tkinter 导入成功")
    except ImportError as e:
        print(f"✗ tkinter 导入失败: {e}")
        return False
    
    try:
        import requests
        print("✓ requests 导入成功")
    except ImportError as e:
        print(f"✗ requests 导入失败: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✓ BeautifulSoup 导入成功")
    except ImportError as e:
        print(f"✗ BeautifulSoup 导入失败: {e}")
        return False
    
    return True

def test_7z():
    """测试7z工具"""
    print("\n测试7z工具...")
    
    # 检查开发环境
    dev_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '7z', '7z.exe')
    if os.path.exists(dev_path):
        print("✓ 7z工具存在 (开发环境)")
        return True
    
    # 检查默认路径
    default_path = r".\7z\7z.exe"
    if os.path.exists(default_path):
        print("✓ 7z工具存在 (默认路径)")
        return True
    
    print("✗ 7z工具不存在")
    return False

def test_config():
    """测试配置文件"""
    print("\n测试配置文件...")
    config_file = "config.json"
    
    # 测试默认配置
    default_config = {
        "proxy": {
            "enabled": False,
            "host": "",
            "port": "",
            "username": "",
            "password": ""
        },
        "login": {
            "username": "",
            "password": "",
            "cookies": {}
        },
        "directories": {
            "source_dir": "",
            "target_dir": "",
            "delete_after_extract": False
        },
        "working_domain": ""
    }
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        print("✓ 配置文件创建成功")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
        print("✓ 配置文件读取成功")
        
        # 清理测试文件
        os.remove(config_file)
        print("✓ 测试配置文件已清理")
        
        return True
    except Exception as e:
        print(f"✗ 配置文件测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试程序...\n")
    
    tests = [
        test_imports,
        test_7z,
        test_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有测试通过，程序可以正常运行")
        return True
    else:
        print("✗ 部分测试失败，请检查环境配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 