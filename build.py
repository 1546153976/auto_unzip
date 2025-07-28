import os
import subprocess
import sys

def build_exe():
    """构建exe文件"""
    print("开始构建exe文件...")
    
    # 检查PyInstaller是否安装
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # 检查7z目录是否存在
    if not os.path.exists("7z"):
        print("错误: 7z目录不存在")
        return False
    
    if not os.path.exists("7z/7z.exe"):
        print("错误: 7z/7z.exe不存在")
        return False
    
    print("检查7z目录...")
    sevenzip_files = os.listdir("7z")
    print(f"7z目录中的文件: {sevenzip_files}")
    
    # 构建命令
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=U15萝莉自动解压工具",
        "--add-data=7z;7z",
        "main.py"
    ]
    
    # 执行构建
    try:
        subprocess.check_call(cmd)
        print("构建完成！")
        print("exe文件位置: dist/U15萝莉自动解压工具.exe")
        
        # 验证构建结果
        exe_path = "dist/U15萝莉自动解压工具.exe"
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"exe文件大小: {file_size:.2f} MB")
        else:
            print("警告: exe文件未找到")
            
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    build_exe() 