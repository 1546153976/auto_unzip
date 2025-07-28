import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
import requests
import re
import subprocess
import threading
from urllib.parse import urljoin, urlparse
import time
from bs4 import BeautifulSoup
import sys

class AutoUnzipApp:
    def __init__(self, root):
        self.root = root
        self.root.title("U15萝莉自动解压工具")
        self.root.geometry("800x600")
        
        # 配置变量
        self.config_file = "config.json"
        self.config = self.load_config()
        self.session = requests.Session()
        self.working_domain = None
        self.is_logged_in = False
        
        # 获取7z路径
        self.sevenzip_path = self.get_sevenzip_path()
        
        # 创建界面
        self.create_widgets()
        
        # 启动时检查网络连接
        self.check_network_on_startup()
    
    def get_sevenzip_path(self):
        """获取7z工具路径，支持开发环境和打包后的环境"""
        # 如果是打包后的环境
        if getattr(sys, 'frozen', False):
            # 打包后的路径
            base_path = sys._MEIPASS
            sevenzip_path = os.path.join(base_path, '7z', '7z.exe')
            if os.path.exists(sevenzip_path):
                return sevenzip_path
        
        # 开发环境路径
        dev_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '7z', '7z.exe')
        if os.path.exists(dev_path):
            return dev_path
        
        # 如果都找不到，返回默认路径
        return r".\7z\7z.exe"
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
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
    
    def save_config(self):
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def create_widgets(self):
        """创建GUI界面"""
        # 创建notebook用于分页
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 网络配置页面
        self.create_network_tab(notebook)
        
        # 登录页面
        self.create_login_tab(notebook)
        
        # 代理配置页面
        self.create_proxy_tab(notebook)
        
        # 目录配置页面
        self.create_directory_tab(notebook)
        
        # 任务执行页面
        self.create_task_tab(notebook)
    
    def create_network_tab(self, notebook):
        """创建网络配置页面"""
        network_frame = ttk.Frame(notebook)
        notebook.add(network_frame, text="网络配置")
        
        # 域名检测
        ttk.Label(network_frame, text="域名检测", font=('Arial', 12, 'bold')).pack(pady=10)
        
        self.domain_status = tk.StringVar(value="未检测")
        ttk.Label(network_frame, textvariable=self.domain_status).pack()
        
        ttk.Button(network_frame, text="检测域名", command=self.check_domains).pack(pady=5)
    
    def create_login_tab(self, notebook):
        """创建登录页面"""
        login_frame = ttk.Frame(notebook)
        notebook.add(login_frame, text="网站登录")
        
        ttk.Label(login_frame, text="网站登录", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # 用户名
        ttk.Label(login_frame, text="用户名:").pack()
        self.username_var = tk.StringVar(value=self.config["login"]["username"])
        ttk.Entry(login_frame, textvariable=self.username_var, width=30).pack(pady=5)
        
        # 密码
        ttk.Label(login_frame, text="密码:").pack()
        self.password_var = tk.StringVar(value=self.config["login"]["password"])
        ttk.Entry(login_frame, textvariable=self.password_var, show="*", width=30).pack(pady=5)
        
        # 登录状态
        self.login_status = tk.StringVar(value="未登录")
        ttk.Label(login_frame, textvariable=self.login_status).pack(pady=5)
        
        ttk.Button(login_frame, text="登录", command=self.login).pack(pady=5)
    
    def create_proxy_tab(self, notebook):
        """创建代理配置页面"""
        proxy_frame = ttk.Frame(notebook)
        notebook.add(proxy_frame, text="代理配置")
        
        ttk.Label(proxy_frame, text="SOCKS代理配置", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # 启用代理
        self.proxy_enabled = tk.BooleanVar(value=self.config["proxy"]["enabled"])
        ttk.Checkbutton(proxy_frame, text="启用代理", variable=self.proxy_enabled).pack(pady=5)
        
        # 代理服务器
        ttk.Label(proxy_frame, text="代理服务器IP:").pack()
        self.proxy_host = tk.StringVar(value=self.config["proxy"]["host"])
        ttk.Entry(proxy_frame, textvariable=self.proxy_host, width=30).pack(pady=5)
        
        # 代理端口
        ttk.Label(proxy_frame, text="代理端口:").pack()
        self.proxy_port = tk.StringVar(value=self.config["proxy"]["port"])
        ttk.Entry(proxy_frame, textvariable=self.proxy_port, width=30).pack(pady=5)
        
        # 代理用户名
        ttk.Label(proxy_frame, text="代理用户名(可选):").pack()
        self.proxy_username = tk.StringVar(value=self.config["proxy"]["username"])
        ttk.Entry(proxy_frame, textvariable=self.proxy_username, width=30).pack(pady=5)
        
        # 代理密码
        ttk.Label(proxy_frame, text="代理密码(可选):").pack()
        self.proxy_password = tk.StringVar(value=self.config["proxy"]["password"])
        ttk.Entry(proxy_frame, textvariable=self.proxy_password, show="*", width=30).pack(pady=5)
        
        ttk.Button(proxy_frame, text="保存代理配置", command=self.save_proxy_config).pack(pady=5)
        ttk.Button(proxy_frame, text="验证代理", command=self.test_proxy).pack(pady=5)
        
        # 代理状态显示
        self.proxy_status = tk.StringVar(value="未验证")
        ttk.Label(proxy_frame, textvariable=self.proxy_status).pack(pady=5)
    
    def create_directory_tab(self, notebook):
        """创建目录配置页面"""
        dir_frame = ttk.Frame(notebook)
        notebook.add(dir_frame, text="目录配置")
        
        ttk.Label(dir_frame, text="目录配置", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # 源目录
        ttk.Label(dir_frame, text="待解压文件目录:").pack()
        source_frame = ttk.Frame(dir_frame)
        source_frame.pack(fill='x', padx=10)
        self.source_dir = tk.StringVar(value=self.config["directories"]["source_dir"])
        ttk.Entry(source_frame, textvariable=self.source_dir, width=50).pack(side='left', fill='x', expand=True)
        ttk.Button(source_frame, text="浏览", command=lambda: self.browse_directory(self.source_dir)).pack(side='right')
        
        # 目标目录
        ttk.Label(dir_frame, text="解压目标目录:").pack()
        target_frame = ttk.Frame(dir_frame)
        target_frame.pack(fill='x', padx=10)
        self.target_dir = tk.StringVar(value=self.config["directories"]["target_dir"])
        ttk.Entry(target_frame, textvariable=self.target_dir, width=50).pack(side='left', fill='x', expand=True)
        ttk.Button(target_frame, text="浏览", command=lambda: self.browse_directory(self.target_dir)).pack(side='right')
        
        # 删除选项
        self.delete_after = tk.BooleanVar(value=self.config["directories"]["delete_after_extract"])
        ttk.Checkbutton(dir_frame, text="解压后删除原文件", variable=self.delete_after).pack(pady=10)
        
        ttk.Button(dir_frame, text="保存目录配置", command=self.save_directory_config).pack(pady=10)
    
    def create_task_tab(self, notebook):
        """创建任务执行页面"""
        task_frame = ttk.Frame(notebook)
        notebook.add(task_frame, text="任务执行")
        
        ttk.Label(task_frame, text="解压任务", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # 进度条
        self.progress = ttk.Progressbar(task_frame, mode='determinate')
        self.progress.pack(fill='x', padx=10, pady=5)
        
        # 状态标签
        self.task_status = tk.StringVar(value="准备就绪")
        ttk.Label(task_frame, textvariable=self.task_status).pack(pady=5)
        
        # 日志区域
        ttk.Label(task_frame, text="执行日志:").pack()
        self.log_text = scrolledtext.ScrolledText(task_frame, height=15, width=80)
        self.log_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 开始按钮
        ttk.Button(task_frame, text="开始解压任务", command=self.start_extraction_task).pack(pady=10)
    
    def browse_directory(self, var):
        """浏览目录"""
        directory = filedialog.askdirectory()
        if directory:
            var.set(directory)
    
    def check_network_on_startup(self):
        """启动时检查网络连接"""
        threading.Thread(target=self.check_domains, daemon=True).start()
    
    def check_domains(self):
        """检测域名可访问性"""
        self.domain_status.set("正在检测...")
        self.root.update()
        
        domains = ['www.u15-loli.com', 'www.u15loli1.xyz']
        
        for domain in domains:
            try:
                url = f"https://{domain}"
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    self.working_domain = domain
                    self.config["working_domain"] = domain
                    self.save_config()
                    self.domain_status.set(f"域名可用: {domain}")
                    return
            except:
                continue
        
        self.domain_status.set("所有域名都无法访问")
        messagebox.showerror("错误", "网站无法访问，请检查网络或配置代理")
    
    def save_proxy_config(self):
        """保存代理配置"""
        self.config["proxy"]["enabled"] = self.proxy_enabled.get()
        self.config["proxy"]["host"] = self.proxy_host.get()
        self.config["proxy"]["port"] = self.proxy_port.get()
        self.config["proxy"]["username"] = self.proxy_username.get()
        self.config["proxy"]["password"] = self.proxy_password.get()
        self.save_config()
        messagebox.showinfo("成功", "代理配置已保存")
    
    def test_proxy(self):
        """测试代理连接"""
        if not self.proxy_enabled.get():
            messagebox.showinfo("提示", "请先启用代理")
            return
        
        host = self.proxy_host.get()
        port = self.proxy_port.get()
        username = self.proxy_username.get()
        password = self.proxy_password.get()
        
        if not host or not port:
            messagebox.showerror("错误", "请输入代理服务器地址和端口")
            return
        
        self.proxy_status.set("正在验证代理...")
        self.root.update()
        
        try:
            # 创建测试会话
            test_session = requests.Session()
            
            # 设置代理
            proxy_url = f"socks5://{host}:{port}"
            if username and password:
                proxy_url = f"socks5://{username}:{password}@{host}:{port}"
            
            test_session.proxies = {"http": proxy_url, "https": proxy_url}
            
            # 测试连接 - 使用IP查询服务
            ip_check_urls = [
                "https://httpbin.org/ip",
                "https://api.ipify.org?format=json",
                "https://ipinfo.io/json"
            ]
            
            ip_info = None
            for url in ip_check_urls:
                try:
                    response = test_session.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if 'ip' in data:
                            ip_info = data['ip']
                        elif 'origin' in data:
                            ip_info = data['origin']
                        break
                except:
                    continue
            
            if ip_info:
                self.proxy_status.set(f"代理验证成功 - 出口IP: {ip_info}")
                messagebox.showinfo("成功", f"代理验证成功！\n出口IP地址: {ip_info}")
            else:
                self.proxy_status.set("代理验证失败")
                messagebox.showerror("错误", "代理验证失败，请检查代理配置")
                
        except Exception as e:
            self.proxy_status.set("代理验证失败")
            messagebox.showerror("错误", f"代理验证失败: {str(e)}")
    
    def save_directory_config(self):
        """保存目录配置"""
        self.config["directories"]["source_dir"] = self.source_dir.get()
        self.config["directories"]["target_dir"] = self.target_dir.get()
        self.config["directories"]["delete_after_extract"] = self.delete_after.get()
        self.save_config()
        messagebox.showinfo("成功", "目录配置已保存")
    
    def login(self):
        """登录网站"""
        if not self.working_domain:
            messagebox.showerror("错误", "请先检测域名")
            return
        
        username = self.username_var.get()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror("错误", "请输入用户名和密码")
            return
        
        self.login_status.set("正在登录...")
        self.root.update()
        
        try:
            # 设置代理
            if self.config["proxy"]["enabled"]:
                proxy_url = f"socks5://{self.config['proxy']['host']}:{self.config['proxy']['port']}"
                if self.config["proxy"]["username"] and self.config["proxy"]["password"]:
                    proxy_url = f"socks5://{self.config['proxy']['username']}:{self.config['proxy']['password']}@{self.config['proxy']['host']}:{self.config['proxy']['port']}"
                self.session.proxies = {"http": proxy_url, "https": proxy_url}
            
            # 获取登录页面
            login_url = f"https://{self.working_domain}/member.php?mod=logging&action=login"
            response = self.session.get(login_url)
            
            # 提取formhash
            soup = BeautifulSoup(response.text, 'html.parser')
            formhash_input = soup.find('input', {'name': 'formhash'})
            if not formhash_input:
                raise Exception("无法获取formhash")
            
            formhash = formhash_input['value']
            
            # 根据HTML源码分析，登录表单需要以下字段
            login_data = {
                'formhash': formhash,
                'username': username,
                'password': password,
                'loginsubmit': 'true',
                'loginfield': 'username',  # 登录字段类型
                'cookietime': '2592000',   # 自动登录时间
                'questionid': '0',         # 安全提问ID
                'answer': '',              # 安全提问答案
                'referer': f'https://{self.working_domain}/'  # 引用页面
            }
            
            # 提交登录
            response = self.session.post(login_url, data=login_data, allow_redirects=True)
            
            # 检查登录是否成功
            # 方法1：检查重定向后的页面内容
            if '欢迎您回来' in response.text or '登录成功' in response.text:
                self.is_logged_in = True
                self.login_status.set("登录成功")
                
                # 保存登录信息
                self.config["login"]["username"] = username
                self.config["login"]["password"] = password
                self.config["login"]["cookies"] = dict(self.session.cookies)
                self.save_config()
                
                messagebox.showinfo("成功", "登录成功")
                return
            
            # 方法2：检查是否重定向到首页
            if response.url and 'forum.php' in response.url:
                self.is_logged_in = True
                self.login_status.set("登录成功")
                
                # 保存登录信息
                self.config["login"]["username"] = username
                self.config["login"]["password"] = password
                self.config["login"]["cookies"] = dict(self.session.cookies)
                self.save_config()
                
                messagebox.showinfo("成功", "登录成功")
                return
            
            # 方法3：检查cookies中是否有登录标识
            if any('auth' in cookie.name.lower() or 'login' in cookie.name.lower() for cookie in self.session.cookies):
                self.is_logged_in = True
                self.login_status.set("登录成功")
                
                # 保存登录信息
                self.config["login"]["username"] = username
                self.config["login"]["password"] = password
                self.config["login"]["cookies"] = dict(self.session.cookies)
                self.save_config()
                
                messagebox.showinfo("成功", "登录成功")
                return
            
            # 方法4：尝试访问用户中心验证登录状态
            try:
                user_center_url = f"https://{self.working_domain}/home.php?mod=space"
                user_response = self.session.get(user_center_url)
                if '欢迎您回来' in user_response.text or username in user_response.text:
                    self.is_logged_in = True
                    self.login_status.set("登录成功")
                    
                    # 保存登录信息
                    self.config["login"]["username"] = username
                    self.config["login"]["password"] = password
                    self.config["login"]["cookies"] = dict(self.session.cookies)
                    self.save_config()
                    
                    messagebox.showinfo("成功", "登录成功")
                    return
            except:
                pass
            
            # 如果都失败了，显示错误信息
            self.login_status.set("登录失败")
            
            # 尝试获取错误信息
            soup = BeautifulSoup(response.text, 'html.parser')
            error_msg = soup.find('div', {'class': 'alert_error'}) or soup.find('div', {'class': 'error'})
            if error_msg:
                error_text = error_msg.get_text(strip=True)
                messagebox.showerror("错误", f"登录失败: {error_text}")
            else:
                messagebox.showerror("错误", "登录失败，请检查用户名和密码")
                
        except Exception as e:
            self.login_status.set("登录失败")
            messagebox.showerror("错误", f"登录失败: {str(e)}")
    

    
    def get_purchase_records(self):
        """获取购买记录"""
        if not self.is_logged_in:
            raise Exception("请先登录")
        
        url = f"https://{self.working_domain}/plugin.php?id=get_purchase_records:get_purchase_records"
        response = self.session.get(url)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        records = []
        
        # 解析购买记录表格
        table = soup.find('table', {'class': 'table'})
        if table:
            rows = table.find_all('tr')[1:]  # 跳过表头
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    filename = cells[1].get_text(strip=True)
                    link = cells[2].find('a')['href'] if cells[2].find('a') else None
                    records.append({
                        'filename': filename,
                        'link': link
                    })
        
        return records
    
    def get_extraction_password(self, thread_url):
        """获取解压密码"""
        if not thread_url:
            return None
        
        full_url = urljoin(f"https://{self.working_domain}/", thread_url)
        response = self.session.get(full_url)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找包含密码的文本
        content = soup.get_text()
        
        # 常见的密码模式
        password_patterns = [
            r'密码[：:]\s*([a-zA-Z0-9]{8,})',
            r'解压密码[：:]\s*([a-zA-Z0-9]{8,})',
            r'密码[：:]\s*([a-zA-Z0-9]{8,})',
            r'password[：:]\s*([a-zA-Z0-9]{8,})',
            r'Password[：:]\s*([a-zA-Z0-9]{8,})'
        ]
        
        for pattern in password_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return None
    
    def match_filename(self, local_filename, purchase_records):
        """匹配文件名"""
        # 移除扩展名
        local_name = os.path.splitext(local_filename)[0]
        
        for record in purchase_records:
            purchase_name = record['filename']
            
            # 直接匹配
            if local_name == purchase_name:
                return record
            
            # 移除特殊字符后匹配
            clean_local = re.sub(r'[^\w]', '', local_name.lower())
            clean_purchase = re.sub(r'[^\w]', '', purchase_name.lower())
            
            if clean_local == clean_purchase:
                return record
            
            # 部分匹配
            if local_name in purchase_name or purchase_name in local_name:
                return record
        
        return None
    
    def extract_file(self, file_path, password, target_dir):
        """使用7z解压文件"""
        if not os.path.exists(self.sevenzip_path):
            raise Exception(f"7z工具未找到: {self.sevenzip_path}")
        
        cmd = [
            self.sevenzip_path,
            "x",
            file_path,
            f"-o{target_dir}",
            "-y"  # 自动覆盖
        ]
        
        if password:
            cmd.extend([f"-p{password}"])
        
        # 使用subprocess.STARTUPINFO来隐藏命令行窗口
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode != 0:
            raise Exception(f"解压失败: {result.stderr}")
        
        return True
    
    def start_extraction_task(self):
        """开始解压任务"""
        if not self.is_logged_in:
            messagebox.showerror("错误", "请先登录")
            return
        
        if not self.source_dir.get() or not self.target_dir.get():
            messagebox.showerror("错误", "请配置源目录和目标目录")
            return
        
        if not os.path.exists(self.source_dir.get()):
            messagebox.showerror("错误", "源目录不存在")
            return
        
        if not os.path.exists(self.target_dir.get()):
            os.makedirs(self.target_dir.get())
        
        # 在新线程中执行任务
        threading.Thread(target=self.extraction_task, daemon=True).start()
    
    def extraction_task(self):
        """解压任务主逻辑"""
        try:
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, "开始执行解压任务...\n")
            self.root.update()
            
            # 获取购买记录
            self.log_text.insert(tk.END, "正在获取购买记录...\n")
            purchase_records = self.get_purchase_records()
            self.log_text.insert(tk.END, f"获取到 {len(purchase_records)} 条购买记录\n")
            self.root.update()
            
            # 获取源目录中的文件
            source_dir = self.source_dir.get()
            files = [f for f in os.listdir(source_dir) if f.lower().endswith(('.rar', '.7z', '.zip'))]
            
            if not files:
                self.log_text.insert(tk.END, "源目录中没有找到压缩文件\n")
                return
            
            self.log_text.insert(tk.END, f"找到 {len(files)} 个压缩文件\n")
            self.root.update()
            
            # 设置进度条
            self.progress['maximum'] = len(files)
            self.progress['value'] = 0
            
            success_count = 0
            failed_count = 0
            
            for i, filename in enumerate(files):
                try:
                    self.task_status.set(f"正在处理: {filename}")
                    self.log_text.insert(tk.END, f"\n处理文件: {filename}\n")
                    self.root.update()
                    
                    # 匹配文件名
                    matched_record = self.match_filename(filename, purchase_records)
                    
                    if not matched_record:
                        self.log_text.insert(tk.END, f"  未找到匹配的购买记录\n")
                        failed_count += 1
                        continue
                    
                    self.log_text.insert(tk.END, f"  找到匹配记录: {matched_record['filename']}\n")
                    
                    # 获取解压密码
                    password = self.get_extraction_password(matched_record['link'])
                    
                    if not password:
                        self.log_text.insert(tk.END, f"  未找到解压密码\n")
                        failed_count += 1
                        continue
                    
                    self.log_text.insert(tk.END, f"  获取到密码正在处理\n")
                    
                    # 解压文件
                    file_path = os.path.join(source_dir, filename)
                    target_dir = os.path.join(self.target_dir.get(), os.path.splitext(filename)[0])
                    
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)
                    
                    self.extract_file(file_path, password, target_dir)
                    self.log_text.insert(tk.END, f"  解压成功\n")
                    
                    # 删除原文件
                    if self.delete_after.get():
                        os.remove(file_path)
                        self.log_text.insert(tk.END, f"  已删除原文件\n")
                    
                    success_count += 1
                    
                except Exception as e:
                    self.log_text.insert(tk.END, f"  处理失败: {str(e)}\n")
                    failed_count += 1
                
                # 更新进度
                self.progress['value'] = i + 1
                self.root.update()
            
            # 任务完成
            self.task_status.set("任务完成")
            self.log_text.insert(tk.END, f"\n任务完成！成功: {success_count}, 失败: {failed_count}\n")
            
        except Exception as e:
            self.task_status.set("任务失败")
            self.log_text.insert(tk.END, f"任务失败: {str(e)}\n")
            messagebox.showerror("错误", f"任务失败: {str(e)}")

def main():
    root = tk.Tk()
    app = AutoUnzipApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 