# 安装说明

## 系统要求

- Windows 10/11
- Python 3.7 或更高版本
- 网络连接

## 快速开始

### 方法一：使用批处理文件（推荐）

1. 双击运行 `run.bat`
2. 程序会自动检查并安装依赖
3. 启动GUI界面

### 方法二：手动安装

1. 安装Python依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 运行程序：
   ```bash
   python main.py
   ```

## 构建独立exe文件

### 方法一：使用批处理文件

1. 双击运行 `build.bat`
2. 等待构建完成
3. exe文件位于 `dist/U15萝莉自动解压工具.exe`

### 方法二：手动构建

1. 安装PyInstaller：
   ```bash
   pip install pyinstaller
   ```

2. 构建exe：
   ```bash
   pyinstaller --onefile --windowed --name="U15萝莉自动解压工具" --add-data="7z;7z" main.py
   ```

## 配置说明

### 代理配置

如果网络访问受限，可以配置SOCKS代理：

```json
{
  "proxy": {
    "enabled": true,
    "host": "代理服务器IP",
    "port": "代理端口",
    "username": "代理用户名（可选）",
    "password": "代理密码（可选）"
  }
}
```

### 目录配置

- `source_dir`: 存放待解压文件的目录
- `target_dir`: 解压后的目标目录
- `delete_after_extract`: 是否删除原文件

## 故障排除

### 常见问题

1. **Python未安装**
   - 下载并安装Python 3.7+
   - 确保Python在PATH环境变量中

2. **依赖包安装失败**
   - 检查网络连接
   - 尝试使用国内镜像：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`

3. **7z工具未找到**
   - 确保7z文件夹在程序目录中
   - 确保7z.exe在7z文件夹中

4. **网络连接失败**
   - 检查网络连接
   - 配置代理设置
   - 检查防火墙设置

5. **登录失败**
   - 检查用户名和密码
   - 确认网站账号有效
   - 检查网络连接

### 日志查看

程序运行时会显示详细的日志信息，包括：
- 网络连接状态
- 登录过程
- 文件匹配结果
- 解压进度
- 错误信息

## 技术支持

如果遇到问题，请：
1. 查看程序日志
2. 检查配置文件
3. 运行测试脚本：`python test.py` 