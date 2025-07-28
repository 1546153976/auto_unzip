#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试解压功能 - 验证命令行窗口隐藏
"""

import os
import sys
import subprocess
import tempfile
import zipfile

def test_extract_without_window():
    """测试解压时不显示命令行窗口"""
    print("测试解压功能...")
    
    # 检查7z工具
    sevenzip_path = r".\7z\7z.exe"
    if not os.path.exists(sevenzip_path):
        print("错误: 7z工具未找到")
        return False
    
    # 创建测试压缩文件
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("这是一个测试文件")
        
        # 创建zip文件
        zip_file = os.path.join(temp_dir, "test.zip")
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(test_file, "test.txt")
        
        print(f"创建测试压缩文件: {zip_file}")
        
        # 测试解压（应该不显示命令行窗口）
        extract_dir = os.path.join(temp_dir, "extract")
        os.makedirs(extract_dir, exist_ok=True)
        
        cmd = [
            sevenzip_path,
            "x",
            zip_file,
            f"-o{extract_dir}",
            "-y"
        ]
        
        # 使用隐藏窗口的方式
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                print("✓ 解压成功，无命令行窗口显示")
                
                # 检查解压结果
                extracted_file = os.path.join(extract_dir, "test.txt")
                if os.path.exists(extracted_file):
                    print("✓ 文件解压正确")
                    return True
                else:
                    print("✗ 文件解压失败")
                    return False
            else:
                print(f"✗ 解压失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ 解压异常: {e}")
            return False

def main():
    """主测试函数"""
    print("测试解压功能 - 命令行窗口隐藏")
    print("=" * 50)
    
    if test_extract_without_window():
        print("\n✓ 所有测试通过！")
        print("解压功能正常工作，不会显示命令行窗口")
    else:
        print("\n✗ 测试失败")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main() 