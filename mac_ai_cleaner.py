import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import requests
import threading
import configparser
import os
import sys
import traceback
import time
import re
import concurrent.futures
import queue
from datetime import datetime
class MacAICleaner:
    def __init__(self, root):
        self.root = root
        self.root.title("AI清洗工具2.0 - macOS版")
        self.root.geometry("1000x800")
        
        # macOS系统优化
        self.root.tk_setPalette(background='#f5f5f5', foreground='#333333')
        self.root.option_add('*Font', 'SF Pro Display 12')
        
        # 配置设置
        self.config = configparser.ConfigParser(interpolation=None)
        self.config_file = os.path.join(os.path.expanduser("~/.config"), "ai_cleaner_config.ini")
        
        # 确保配置目录存在
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # 加载配置
        self.load_config()
        
        self.input_file = ""
        self.output_file = ""
        self.processing = False
        self.df = None
        self.fields = []
        
        # 线程池
        self.executor = None
        self.futures = []
        
        # 进度队列
        self.progress_queue = queue.Queue()
        
        self.create_widgets()
        
        # 启动进度更新线程
        self.update_progress_thread = threading.Thread(target=self.update_progress_from_queue, daemon=True)
        self.update_progress_thread.start()
        
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                self.config.read(self.config_file, encoding='utf-8')
            except Exception as e:
                messagebox.showerror("配置加载失败", f"错误：{str(e)}\n将生成新配置文件")
                self.generate_default_config()
        else:
            self.generate_default_config()
    
    def generate_default_config(self):
        """生成默认配置（动态字段示例提示词）"""
        dynamic_prompt = """
### 动态字段清洗规则（根据此提示词自动提取字段）
请作为专业数据分析师，按照以下规则处理数据：
1. 从【宝贝名】字段提取以下信息：
   - 产品名称：提取产品的完整名称
   - 规格：提取产品的容量规格
   - 功效：提取产品的主要功效
   - 核心成分：提取产品的主要有效成分
   - 适用肤质：提取适用肤质信息
2. 输出格式要求：
   - 每个字段单独一行
   - 格式为"字段名:值"，使用英文冒号
   - 字段名必须与上述列表完全一致
   - 没有信息的字段留空
3. 示例输入：兰蔻小黑瓶精华液 30ml 保湿抗皱 二裂酵母成分 所有肤质适用
4. 示例输出：
产品名称:兰蔻小黑瓶精华液
规格:30ml
功效:保湿抗皱
核心成分:二裂酵母
适用肤质:所有肤质
### 重要说明：
- 工具会自动从第1条规则中提取字段名
- 你可以修改第1条规则中的字段列表
- 字段数量没有限制，可根据需要增删
- 严格按照示例格式输出，不要添加额外内容
"""
        self.config["DEFAULT"] = {
            "api_key": "",
            "prompt": dynamic_prompt.strip(),
            "input_file": "",
            "output_file": "",
            "batch_size": "5",  # 批量处理大小
            "max_workers": "4"  # 最大线程数
        }
        self.save_config()
    
    def save_config(self):
        """保存配置"""
        with open(self.config_file, "w", encoding="utf-8") as f:
            self.config.write(f)
    
    def create_widgets(self):
        """创建界面 - macOS风格"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # API配置
        api_frame = ttk.LabelFrame(main_frame, text="API配置", padding="10")
        api_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(api_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W)
        self.api_key_entry = ttk.Entry(api_frame, width=80, show="*")
        self.api_key_entry.grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
        self.api_key_entry.insert(0, self.config["DEFAULT"].get("api_key", ""))
        
        # 提速配置
        speed_frame = ttk.LabelFrame(main_frame, text="提速配置", padding="10")
        speed_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(speed_frame, text="批量处理大小:").grid(row=0, column=0, sticky=tk.W)
        self.batch_size_var = tk.StringVar(value=self.config["DEFAULT"].get("batch_size", "5"))
        self.batch_size_entry = ttk.Entry(speed_frame, width=10, textvariable=self.batch_size_var)
        self.batch_size_entry.grid(row=0, column=1, padx=(10, 20), sticky=tk.W)
        
        ttk.Label(speed_frame, text="最大线程数:").grid(row=0, column=2, sticky=tk.W)
        self.max_workers_var = tk.StringVar(value=self.config["DEFAULT"].get("max_workers", "4"))
        self.max_workers_entry = ttk.Entry(speed_frame, width=10, textvariable=self.max_workers_var)
        self.max_workers_entry.grid(row=0, column=3, padx=(10, 0), sticky=tk.W)
        
        # 提示词配置
        prompt_frame = ttk.LabelFrame(main_frame, text="清洗规则（动态字段版）", padding="10")
        prompt_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.prompt_text = tk.Text(prompt_frame, wrap=tk.WORD, height=15, font=('SF Pro Display', 12))
        self.prompt_text.pack(fill=tk.BOTH, expand=True)
        self.prompt_text.insert(tk.END, self.config["DEFAULT"].get("prompt", ""))
        
        # 动态字段预览
        field_frame = ttk.LabelFrame(main_frame, text="动态提取的字段（自动更新）", padding="10")
        field_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(field_frame, text="当前提取的字段：").pack(anchor=tk.W)
        self.fields_text = tk.Text(field_frame, height=3, wrap=tk.WORD, font=('SF Pro Display', 12))
        self.fields_text.pack(fill=tk.X, pady=(5, 0))
        self.fields_text.config(state=tk.DISABLED)
        
        update_btn = ttk.Button(field_frame, text="更新字段预览", command=self.update_field_preview)
        update_btn.pack(side=tk.RIGHT, pady=(5, 0))
        
        # 文件配置
        file_frame = ttk.LabelFrame(main_frame, text="文件配置", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 输入文件
        input_frame = ttk.Frame(file_frame)
        input_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(input_frame, text="输入文件:").pack(side=tk.LEFT)
        self.input_file_entry = ttk.Entry(input_frame, width=60)
        self.input_file_entry.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        self.input_file_entry.insert(0, self.config["DEFAULT"].get("input_file", ""))
        input_btn = ttk.Button(input_frame, text="浏览", command=self.select_input_file)
        input_btn.pack(side=tk.RIGHT)
        
        # 输出文件
        output_frame = ttk.Frame(file_frame)
        output_frame.pack(fill=tk.X)
        ttk.Label(output_frame, text="输出文件:").pack(side=tk.LEFT)
        self.output_file_entry = ttk.Entry(output_frame, width=60)
        self.output_file_entry.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        self.output_file_entry.insert(0, self.config["DEFAULT"].get("output_file", ""))
        output_btn = ttk.Button(output_frame, text="浏览", command=self.select_output_file)
        output_btn.pack(side=tk.RIGHT)
        
        # 操作按钮
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.start_btn = ttk.Button(action_frame, text="开始清洗", command=self.start_processing, style='Accent.TButton')
        self.start_btn.pack(side=tk.LEFT)
        
        self.stop_save_btn = ttk.Button(action_frame, text="停止并保存", command=self.stop_and_save, state=tk.DISABLED)
        self.stop_save_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        self.stop_no_save_btn = ttk.Button(action_frame, text="停止不保存", command=self.stop_no_save, state=tk.DISABLED)
        self.stop_no_save_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # 状态显示
        status_frame = ttk.LabelFrame(main_frame, text="处理状态", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.status_text = tk.Text(status_frame, wrap=tk.WORD, height=10, font=('SF Pro Display', 12))
        self.status_text.pack(fill=tk.BOTH, expand=True)
        self.status_text.insert(tk.END, "准备就绪...\n")
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100, style='Hori.TProgressbar')
        self.progress_bar.pack(fill=tk.X, pady=(0, 15))
        
        # macOS风格设置
        self.style = ttk.Style()
        self.style.theme_use('clam')  # 使用clam主题更接近macOS风格
        
        # 自定义样式
        self.style.configure('Accent.TButton', 
                            background='#007aff', 
                            foreground='white',
                            padding=(10, 5))
        self.style.map('Accent.TButton',
                       background=[('active', '#0056cc')])
        
        self.style.configure('Hori.TProgressbar',
                            troughcolor='#e0e0e0',
                            background='#007aff')
        
        # 初始化字段预览
        self.update_field_preview()
    
    def update_field_preview(self):
        """更新字段预览"""
        prompt = self.prompt_text.get("1.0", tk.END)
        fields = self.extract_dynamic_fields(prompt)
        self.fields_text.config(state=tk.NORMAL)
        self.fields_text.delete("1.0", tk.END)
        if fields:
            self.fields_text.insert(tk.END, f"将生成以下字段：\n" + ", ".join(fields))
        else:
            self.fields_text.insert(tk.END, "未提取到字段，请检查提示词格式")
        self.fields_text.config(state=tk.DISABLED)
    
    def extract_dynamic_fields(self, prompt):
        """从提示词中动态提取字段名"""
        pattern = r'[-*]\s*([^\n:：]+?)\s*[:：]'
        matches = re.findall(pattern, prompt)
        
        fields = []
        for field in matches:
            cleaned_field = re.sub(r'[^\w\u4e00-\u9fa5]', '', field).strip()
            if cleaned_field and cleaned_field not in fields:
                fields.append(cleaned_field)
        
        return fields
    
    def clean_field_name(self, field):
        """清理字段名"""
        return re.sub(r'[^\w\u4e00-\u9fa5]', '', field).strip()
    
    def select_input_file(self):
        """选择输入文件 - macOS优化"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel文件", "*.xlsx;*.xls"), ("所有文件", "*.*")],
            initialdir=os.path.expanduser("~"),
            title="选择输入文件"
        )
        if file_path:
            self.input_file_entry.delete(0, tk.END)
            self.input_file_entry.insert(0, file_path)
            self.config["DEFAULT"]["input_file"] = file_path
            self.save_config()
    
    def select_output_file(self):
        """选择输出文件 - macOS优化"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")],
            initialdir=os.path.expanduser("~/Desktop"),
            title="选择输出文件"
        )
        if file_path:
            self.output_file_entry.delete(0, tk.END)
            self.output_file_entry.insert(0, file_path)
            self.config["DEFAULT"]["output_file"] = file_path
            self.save_config()
    
    def start_processing(self):
        """开始处理"""
        self.config["DEFAULT"]["api_key"] = self.api_key_entry.get()
        self.config["DEFAULT"]["prompt"] = self.prompt_text.get("1.0", tk.END)
        self.config["DEFAULT"]["batch_size"] = self.batch_size_var.get()
        self.config["DEFAULT"]["max_workers"] = self.max_workers_var.get()
        self.save_config()
        
        if not self.config["DEFAULT"]["api_key"]:
            messagebox.showwarning("警告", "请输入API Key！")
            return
        
        input_file = self.input_file_entry.get()
        output_file = self.output_file_entry.get()
        
        if not input_file or not output_file:
            messagebox.showwarning("警告", "请选择输入和输出文件！")
            return
        
        # 检查输出文件是否可写
        if os.path.exists(output_file):
            try:
                with open(output_file, 'a'):
                    pass
            except PermissionError:
                messagebox.showwarning("权限警告", f"输出文件 {output_file} 可能已在Excel中打开，请先关闭！")
                return
        
        # 提取字段
        prompt = self.prompt_text.get("1.0", tk.END)
        self.fields = self.extract_dynamic_fields(prompt)
        if not self.fields:
            messagebox.showwarning("字段提取失败", "未从提示词中提取到字段，请检查提示词格式")
            return
        
        self.start_btn.config(state=tk.DISABLED)
        self.stop_save_btn.config(state=tk.NORMAL)
        self.stop_no_save_btn.config(state=tk.NORMAL)
        self.processing = True
        
        threading.Thread(target=self.process_data, args=(input_file, output_file)).start()
    
    def stop_and_save(self):
        """停止并保存"""
        self.processing = False
        if self.executor:
            self.executor.shutdown(wait=False)
        if self.df is not None:
            output_file = self.output_file_entry.get()
            if self.save_excel_file(output_file):
                self.progress_queue.put(("status", f"\n🛑 已保存结果到：{output_file}\n"))
        self.reset_buttons()
    
    def stop_no_save(self):
        """停止不保存"""
        self.processing = False
        if self.executor:
            self.executor.shutdown(wait=False)
        self.progress_queue.put(("status", "\n🛑 已停止，未保存结果\n"))
        self.reset_buttons()
    
    def reset_buttons(self):
        """重置按钮状态"""
        self.start_btn.config(state=tk.NORMAL)
        self.stop_save_btn.config(state=tk.DISABLED)
        self.stop_no_save_btn.config(state=tk.DISABLED)
    
    def save_excel_file(self, output_file):
        """保存Excel文件 - macOS优化"""
        try:
            df_to_save = self.df.copy()
            df_to_save = df_to_save.fillna("")
            df_to_save.to_excel(output_file, index=False, engine='openpyxl')
            return True
        except Exception as e:
            error_msg = f"保存文件错误：{str(e)}"
            self.progress_queue.put(("status", f"\n❌ {error_msg}\n"))
            return False
    
    def update_progress_from_queue(self):
        """从队列更新进度"""
        while True:
            try:
                msg_type, content = self.progress_queue.get(timeout=0.1)
                if msg_type == "status":
                    self.status_text.insert(tk.END, content)
                    self.status_text.see(tk.END)
                elif msg_type == "progress":
                    self.progress_var.set(content)
                self.root.update()
            except queue.Empty:
                continue
            except Exception:
                break
    
    def process_data(self, input_file, output_file):
        """处理数据（提速版）"""
        try:
            # 读取原始数据
            self.df = pd.read_excel(input_file, engine='openpyxl')
            original_columns = self.df.columns.tolist()
            total_rows = len(self.df)
            
            self.progress_queue.put(("status", f"✅ 读取原始数据成功，共{total_rows}行\n"))
            self.progress_queue.put(("status", f"📋 动态提取字段：{self.fields}（共{len(self.fields)}个）\n"))
            
            # 添加新字段到DataFrame
            for field in self.fields:
                if field not in self.df.columns:
                    self.df[field] = ""
            
            # 立即保存初始状态
            if self.save_excel_file(output_file):
                self.progress_queue.put(("status", f"💾 已保存初始状态到：{output_file}\n"))
            
            # 获取配置参数
            api_key = self.config["DEFAULT"]["api_key"]
            prompt_template = self.config["DEFAULT"]["prompt"]
            batch_size = int(self.config["DEFAULT"]["batch_size"])
            max_workers = int(self.config["DEFAULT"]["max_workers"])
            
            self.progress_queue.put(("status", f"⚡ 提速配置：批量大小={batch_size}，线程数={max_workers}\n"))
            
            # 批量处理数据
            start_time = time.time()
            
            # 创建线程池
            self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
            
            # 分批处理数据
            for batch_start in range(0, total_rows, batch_size):
                if not self.processing:
                    break
                
                batch_end = min(batch_start + batch_size, total_rows)
                batch_indices = list(range(batch_start, batch_end))
                
                self.progress_queue.put(("status", f"\n📦 处理批次 {batch_start//batch_size + 1}（行 {batch_start+1}-{batch_end}）...\n"))
                
                # 提交批量任务到线程池
                batch_futures = []
                for idx in batch_indices:
                    future = self.executor.submit(
                        self.process_single_row,
                        idx, self.df.iloc[idx], api_key, prompt_template, original_columns
                    )
                    batch_futures.append((idx, future))
                
                # 等待批次完成
                for idx, future in batch_futures:
                    try:
                        result = future.result(timeout=30)
                        if result:
                            # 处理所有返回的字段
                            if isinstance(result, dict):
                                self.progress_queue.put(("status", f"   行 {idx+1}: 成功提取 {len(result)} 个字段\n"))
                                for field, value in result.items():
                                    self.df.at[idx, field] = value
                            else:
                                self.progress_queue.put(("status", f"   行 {idx+1}: 提取结果格式错误\n"))
                        else:
                            self.progress_queue.put(("status", f"   行 {idx+1}: 未提取到任何字段\n"))
                    except concurrent.futures.TimeoutError:
                        self.progress_queue.put(("status", f"❌ 行 {idx+1} 处理超时\n"))
                    except Exception as e:
                        self.progress_queue.put(("status", f"❌ 行 {idx+1} 处理错误：{str(e)}\n"))
                
                # 更新进度条
                progress = (batch_end / total_rows) * 100
                self.progress_queue.put(("progress", progress))
                
                # 每批处理完成后保存
                if self.save_excel_file(output_file):
                    self.progress_queue.put(("status", f"💾 批次完成，已保存进度\n"))
            
            # 关闭线程池
            if self.executor:
                self.executor.shutdown(wait=True)
            
            # 计算总耗时
            total_time = time.time() - start_time
            avg_time_per_row = total_time / total_rows if total_rows > 0 else 0
            
            # 最终保存
            if self.save_excel_file(output_file):
                new_columns = self.df.columns.tolist()
                added_fields = [col for col in new_columns if col not in original_columns]
                
                self.progress_queue.put(("status", f"\n🎉 处理完成！\n"))
                self.progress_queue.put(("status", f"⏱️ 总耗时：{total_time:.2f}秒\n"))
                self.progress_queue.put(("status", f"⚡ 平均每行：{avg_time_per_row:.2f}秒\n"))
                self.progress_queue.put(("status", f"📊 原字段：{original_columns}\n"))
                self.progress_queue.put(("status", f"➕ 新增字段：{added_fields}（共{len(added_fields)}个）\n"))
                self.progress_queue.put(("status", f"📁 输出文件：{output_file}\n"))
            
        except Exception as e:
            error_msg = f"处理错误：{str(e)}\n{traceback.format_exc()}"
            self.progress_queue.put(("status", f"\n❌ {error_msg}\n"))
        finally:
            self.processing = False
            self.reset_buttons()
    
    def process_single_row(self, idx, row, api_key, prompt_template, original_columns):
        """处理单行数据"""
        try:
            # 构建提示词
            row_data = "\n".join([f"{col}: {row[col]}" for col in original_columns])
            current_prompt = prompt_template + "\n当前数据：\n" + row_data + "\n请严格按照要求输出结果："
            
            # 调用API
            result = self.call_ai_api(api_key, current_prompt)
            
            # 解析结果
            field_values = {}
            
            lines = result.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 处理分隔符
                if ':' in line:
                    field, value = line.split(':', 1)
                elif '：' in line:
                    field, value = line.split('：', 1)
                else:
                    continue
                
                field = field.strip()
                cleaned_field = self.clean_field_name(field)
                value = value.strip()
                
                if cleaned_field in self.fields:
                    field_values[cleaned_field] = value
            
            return field_values
        
        except Exception as e:
            self.progress_queue.put(("status", f"❌ 行 {idx+1} API错误：{str(e)}\n"))
            return {}
    
    def call_ai_api(self, api_key, prompt):
        """调用DeepSeek API"""
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 500,
            "stream": False
        }
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = MacAICleaner(root)
        root.mainloop()
    except Exception as e:
        error_msg = f"启动错误：{str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("启动失败", error_msg)
        root.destroy()