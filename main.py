import wx
import os
import json


class ShaderBrowser(wx.Frame):
    # 版本号定义，方便更新
    VERSION = "1.0.0"
    CONFIG_FILE = "shader_browser_config.json"
    
    def __init__(self, parent, title):
        # 在标题中添加版本号
        full_title = f"{title} v{self.VERSION}"
        super(ShaderBrowser, self).__init__(parent, title=full_title, size=(800, 500))

        self.InitUI()
        self.Centre()
        self.Show()
        
        # 加载保存的路径
        self.load_saved_path()
    
    def InitUI(self):
        panel = wx.Panel(self)
        
        # 创建垂直布局管理器
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # 第一行：路径标签和输入框
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        self.browse_btn = wx.Button(panel, label="浏览路径:", size=(68, -1))
        self.browse_btn.Bind(wx.EVT_BUTTON, self.on_browse)
        hbox1.Add(self.browse_btn, flag=wx.EXPAND)
        self.path_text = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.path_text.Bind(wx.EVT_TEXT_ENTER, self.on_path_enter)
        hbox1.Add(self.path_text, proportion=1, flag=wx.EXPAND)
        
        vbox.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # 第二行：操作按钮
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        self.workFrag_btn = wx.Button(panel, label="分离frag")
        self.workFrag_btn.Bind(wx.EVT_BUTTON, self.on_separate_frag)
        hbox2.Add(self.workFrag_btn, flag=wx.ALIGN_CENTER | wx.LEFT, border=10)
        
        self.refresh_btn = wx.Button(panel, label="刷新")
        self.refresh_btn.Bind(wx.EVT_BUTTON, self.on_refresh)
        hbox2.Add(self.refresh_btn, flag=wx.ALIGN_CENTER | wx.LEFT, border=10)
        
        vbox.Add(hbox2, flag=wx.ALIGN_LEFT | wx.TOP, border=10)
        
        # 第三行：双列表标签行
        hbox_labels = wx.BoxSizer(wx.HORIZONTAL)
        
        file_label = wx.StaticText(panel, label=".shader 文件列表:")
        hbox_labels.Add(file_label, proportion=1, flag=wx.EXPAND)
        
        frag_label = wx.StaticText(panel, label="分离的 frag 列表:")
        hbox_labels.Add(frag_label, proportion=1, flag=wx.EXPAND)
        
        vbox.Add(hbox_labels, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        
        # 第四行：双列表框
        hbox_lists = wx.BoxSizer(wx.HORIZONTAL)
        
        # 左侧：文件列表框
        self.file_list = wx.ListBox(panel, style=wx.LB_SINGLE | wx.LB_HSCROLL)
        self.file_list.Bind(wx.EVT_LISTBOX_DCLICK, self.on_file_double_click)
        hbox_lists.Add(self.file_list, proportion=1, flag=wx.EXPAND)
        
        # 右侧：frag 列表框
        self.frag_list = wx.ListBox(panel, style=wx.LB_SINGLE | wx.LB_HSCROLL)
        self.frag_list.Bind(wx.EVT_LISTBOX_DCLICK, self.on_frag_double_click)
        hbox_lists.Add(self.frag_list, proportion=1, flag=wx.EXPAND | wx.LEFT, border=10)
        
        vbox.Add(hbox_lists, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        
        # 第五行：状态栏
        self.status_bar = wx.StatusBar(panel)
        vbox.Add(self.status_bar, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        
        panel.SetSizer(vbox)
    
    def on_file_double_click(self, event):
        """处理文件列表双击事件"""
        selection = self.file_list.GetSelection()
        if selection != wx.NOT_FOUND:
            file_name = self.file_list.GetString(selection)
            current_path = self.path_text.GetValue()
            if current_path:
                full_path = os.path.join(current_path, file_name)
                wx.MessageBox(f"完整路径:\n{full_path}", "文件信息", wx.OK | wx.ICON_INFORMATION)
    
    def on_path_enter(self, event):
        """处理路径文本框回车事件"""
        path = self.path_text.GetValue()
        if path:
            self.load_shader_files(path)
    
    def on_browse(self, event):
        """处理浏览按钮点击事件"""
        dlg = wx.DirDialog(self, "选择包含 .shader 文件的目录", 
                          style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_OK:
            selected_path = dlg.GetPath()
            self.path_text.SetValue(selected_path)
            self.load_shader_files(selected_path)
        
        dlg.Destroy()
    
    def save_path_to_config(self, path):
        """保存路径到配置文件"""
        try:
            config = {"last_path": path}
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.status_bar.SetStatusText(f"路径已保存到配置文件: {self.CONFIG_FILE}")
        except Exception as e:
            self.status_bar.SetStatusText(f"保存配置文件失败: {str(e)}")
    
    def load_saved_path(self):
        """从配置文件加载保存的路径，如果没有则使用当前目录"""
        try:
            current_dir = os.getcwd()  # 获取当前工作目录
            
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    last_path = config.get("last_path", "")
                    if last_path and os.path.isdir(last_path):
                        # 使用保存的路径
                        self.path_text.SetValue(last_path)
                        self.load_shader_files(last_path)
                        self.status_bar.SetStatusText(f"已加载上次保存的路径: {last_path}")
                        return
                    else:
                        self.status_bar.SetStatusText("配置文件中没有有效的路径，使用当前目录")
            else:
                self.status_bar.SetStatusText("配置文件不存在，使用当前目录")
            
            # 使用当前目录
            self.path_text.SetValue(current_dir)
            self.load_shader_files(current_dir)
            self.status_bar.SetStatusText(f"已加载当前目录: {current_dir}")
            
        except Exception as e:
            self.status_bar.SetStatusText(f"加载路径失败: {str(e)}")
            # 失败时也尝试加载当前目录
            try:
                current_dir = os.getcwd()
                self.path_text.SetValue(current_dir)
                self.load_shader_files(current_dir)
            except:
                pass
    
    def on_frag_double_click(self, event):
        """处理frag列表双击事件：使用malisc.exe编译选中的frag文件"""
        selection = self.frag_list.GetSelection()
        if selection == wx.NOT_FOUND:
            wx.MessageBox("请先在右侧列表中选择一个.frag文件", "提示", wx.OK | wx.ICON_WARNING)
            return
        
        frag_file_name = self.frag_list.GetString(selection)
        current_path = self.path_text.GetValue()
        if not current_path:
            wx.MessageBox("请先选择或输入路径", "提示", wx.OK | wx.ICON_WARNING)
            return
        
        # 构建frag文件的完整路径
        frags_dir = os.path.join(current_path, "Frags")
        frag_file_path = os.path.join(frags_dir, frag_file_name)
        
        if not os.path.exists(frag_file_path):
            wx.MessageBox(f"文件不存在: {frag_file_path}", "错误", wx.OK | wx.ICON_ERROR)
            return
        
        # 查找malisc.exe
        malisc_path = self.find_malisc_exe()
        if not malisc_path:
            wx.MessageBox(
                "未找到 malisc.exe\n"
                "请确保 Mali_Offline_Compiler_Windows 目录存在且包含 malisc.exe",
                "错误", wx.OK | wx.ICON_ERROR
            )
            return
        
        try:
            # 使用powershell执行malisc.exe
            cmd = f'powershell -Command "& \'{malisc_path}\' \'{frag_file_path}\'"'
            self.status_bar.SetStatusText(f"正在编译: {frag_file_name}")
            
            # 执行命令
            import subprocess
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
            
            # 显示结果
            output = result.stdout
            if result.returncode != 0:
                output += f"\n\n错误代码: {result.returncode}"
                if result.stderr:
                    output += f"\n错误信息: {result.stderr}"
            
            # 显示编译结果对话框
            dlg = wx.Dialog(self, title=f"编译结果 - {frag_file_name}", size=(800, 400))
            text_ctrl = wx.TextCtrl(dlg, value=output, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(text_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
            dlg.SetSizer(sizer)
            dlg.ShowModal()
            dlg.Destroy()
            
            self.status_bar.SetStatusText(f"编译完成: {frag_file_name}")
            
        except Exception as e:
            self.status_bar.SetStatusText(f"编译失败: {str(e)}")
            wx.MessageBox(f"编译失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)
    
    def find_malisc_exe(self):
        """查找malisc.exe的路径"""
        # 可能的malisc.exe路径
        possible_paths = [
            # 在当前目录下的Mali_Offline_Compiler_Windows目录
            os.path.join(os.getcwd(), "Mali_Offline_Compiler_Windows", "malisc.exe"),
            # 在应用程序目录下的Mali_Offline_Compiler_Windows目录
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "Mali_Offline_Compiler_Windows", "malisc.exe"),
            # 在系统PATH中
            "malisc.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return os.path.abspath(path)
        
        return None
    
    def on_refresh(self, event):
        """处理刷新按钮点击事件：重新加载当前目录的文件"""
        current_path = self.path_text.GetValue()
        if not current_path:
            wx.MessageBox("请先选择或输入路径", "提示", wx.OK | wx.ICON_WARNING)
            return
        
        if not os.path.isdir(current_path):
            wx.MessageBox(f"路径不是有效的目录: {current_path}", "错误", wx.OK | wx.ICON_ERROR)
            return
        
        try:
            self.status_bar.SetStatusText("正在刷新文件列表...")
            self.load_shader_files(current_path)
            self.status_bar.SetStatusText(f"刷新完成: {current_path}")
        except Exception as e:
            self.status_bar.SetStatusText(f"刷新失败: {str(e)}")
            wx.MessageBox(f"刷新失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)
    
    def on_separate_frag(self, event):
        """处理分离frag按钮点击事件"""
        # 获取选中的shader文件
        selection = self.file_list.GetSelection()
        if selection == wx.NOT_FOUND:
            wx.MessageBox("请先在左侧列表中选择一个.shader文件", "提示", wx.OK | wx.ICON_WARNING)
            return
        
        file_name = self.file_list.GetString(selection)
        current_path = self.path_text.GetValue()
        if not current_path:
            wx.MessageBox("请先选择或输入路径", "提示", wx.OK | wx.ICON_WARNING)
            return
        
        shader_path = os.path.join(current_path, file_name)
        
        try:
            # 分离frag
            frag_files = self.separate_frag_from_shader(shader_path, current_path)
            
            if frag_files:
                # 更新右侧frag列表
                self.load_frag_files(current_path)
                self.status_bar.SetStatusText(f"成功分离出 {len(frag_files)} 个frag文件")
                wx.MessageBox(f"成功分离出 {len(frag_files)} 个frag文件到 Frags 目录", "完成", wx.OK | wx.ICON_INFORMATION)
            else:
                self.status_bar.SetStatusText("未找到可分离的frag内容")
                wx.MessageBox("未在文件中找到 #ifdef FRAGMENT 标记，无法分离frag", "提示", wx.OK | wx.ICON_WARNING)
                
        except Exception as e:
            self.status_bar.SetStatusText(f"分离frag失败: {str(e)}")
            wx.MessageBox(f"分离frag失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)
    
    def separate_frag_from_shader(self, shader_path, base_directory):
        """从shader文件中分离frag内容"""
        if not os.path.exists(shader_path):
            raise FileNotFoundError(f"文件不存在: {shader_path}")
        
        # 读取文件内容
        with open(shader_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 查找所有 #ifdef FRAGMENT 的位置
        fragment_indices = []
        for i, line in enumerate(lines):
            if '#ifdef FRAGMENT' in line:
                fragment_indices.append(i)
        
        if len(fragment_indices) < 2:
            return []  # 至少需要两个 #ifdef FRAGMENT 才能分割
        
        # 创建Frags目录
        frags_dir = os.path.join(base_directory, "Frags")
        os.makedirs(frags_dir, exist_ok=True)
        
        # 获取shader文件名（不含扩展名）
        shader_name = os.path.splitext(os.path.basename(shader_path))[0]
        
        frag_files = []
        
        # 分割每个fragment块
        for i in range(len(fragment_indices) - 1):
            start_idx = fragment_indices[i]
            end_idx = fragment_indices[i + 1]
            
            # 提取fragment内容（从start_idx到end_idx-1）
            fragment_content = lines[start_idx:end_idx]
            
            # 处理文本：移除第一行的 #ifdef FRAGMENT 和最后的 #endif
            processed_content = self.process_fragment_content(fragment_content)
            
            # 生成文件名
            frag_filename = f"{shader_name}_{i+1:03d}.frag"
            frag_filepath = os.path.join(frags_dir, frag_filename)
            
            # 写入文件
            with open(frag_filepath, 'w', encoding='utf-8') as f:
                f.writelines(processed_content)
            
            frag_files.append(frag_filename)
        
        # 处理最后一个fragment块（到文件结尾）
        if fragment_indices:
            start_idx = fragment_indices[-1]
            fragment_content = lines[start_idx:]
            
            # 处理文本：移除第一行的 #ifdef FRAGMENT 和最后的 #endif
            processed_content = self.process_fragment_content(fragment_content)
            
            frag_filename = f"{shader_name}_{len(fragment_indices):03d}.frag"
            frag_filepath = os.path.join(frags_dir, frag_filename)
            
            with open(frag_filepath, 'w', encoding='utf-8') as f:
                f.writelines(processed_content)
            
            frag_files.append(frag_filename)
        
        return frag_files
    
    def process_fragment_content(self, content_lines):
        """处理fragment内容：移除标记、修改版本号并按分隔线分割"""
        if not content_lines:
            return []
        
        # 创建副本以避免修改原始列表
        processed = content_lines.copy()
        
        # 1. 移除第一行的 #ifdef FRAGMENT（如果存在）
        if processed and '#ifdef FRAGMENT' in processed[0]:
            processed = processed[1:]
        
        # 2. 查找分隔线 "//////////////////////////////////////////////////////"
        separator_line = "//////////////////////////////////////////////////////"
        separator_index = -1
        
        for i, line in enumerate(processed):
            if separator_line in line:
                separator_index = i
                break
        
        # 3. 如果找到分隔线，只保留分隔线之前的内容
        if separator_index != -1:
            processed = processed[:separator_index]
        
        # 4. 移除最后一行的 #endif（如果存在）及其后面的空行
        # 从后往前查找 #endif
        endif_index = -1
        for i in range(len(processed) - 1, -1, -1):
            if '#endif' in processed[i]:
                endif_index = i
                break
        
        if endif_index != -1:
            # 移除 #endif 行
            processed = processed[:endif_index]
            
            # 移除 #endif 后面的空行（从后往前移除连续的空行）
            while processed and processed[-1].strip() == '':
                processed = processed[:-1]
        
        # 5. 修改 #version 300 es 为 #version 320 es
        for i in range(len(processed)):
            if '#version 300 es' in processed[i]:
                processed[i] = processed[i].replace('#version 300 es', '#version 320 es')
        
        return processed
    
    def load_frag_files(self, directory):
        """加载指定目录下Frags文件夹中的所有.frag文件"""
        self.frag_list.Clear()
        
        frags_dir = os.path.join(directory, "Frags")
        if not os.path.isdir(frags_dir):
            self.status_bar.SetStatusText(f"Frags目录不存在: {frags_dir}")
            return
        
        try:
            # 获取所有 .frag 文件
            frag_files = []
            for root, dirs, files in os.walk(frags_dir):
                for file in files:
                    if file.lower().endswith('.frag'):
                        full_path = os.path.join(root, file)
                        # 显示相对路径（相对于Frags目录）
                        rel_path = os.path.relpath(full_path, frags_dir)
                        frag_files.append(rel_path)
            
            if frag_files:
                frag_files.sort()  # 按字母顺序排序
                self.frag_list.Set(frag_files)
                self.status_bar.SetStatusText(f"找到 {len(frag_files)} 个.frag文件")
            else:
                self.status_bar.SetStatusText("未找到.frag文件")
                
        except Exception as e:
            self.status_bar.SetStatusText(f"加载frag文件失败: {str(e)}")
    
    def load_shader_files(self, directory):
        """加载指定目录中的所有 .shader 文件"""
        self.file_list.Clear()
        
        # 保存路径到配置文件
        self.save_path_to_config(directory)
        
        if not os.path.isdir(directory):
            self.status_bar.SetStatusText(f"错误: {directory} 不是有效的目录")
            return
        
        try:
            # 获取所有 .shader 文件
            shader_files = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith('.shader'):
                        full_path = os.path.join(root, file)
                        # 显示相对路径
                        rel_path = os.path.relpath(full_path, directory)
                        shader_files.append(rel_path)
            
            if shader_files:
                shader_files.sort()  # 按字母顺序排序
                self.file_list.Set(shader_files)
                self.status_bar.SetStatusText(f"找到 {len(shader_files)} 个 .shader 文件")
                
                # 同时加载frag文件
                self.load_frag_files(directory)
            else:
                self.status_bar.SetStatusText("未找到 .shader 文件")
                
        except Exception as e:
            self.status_bar.SetStatusText(f"错误: {str(e)}")


def main():
    app = wx.App(False)
    frame = ShaderBrowser(None, "Shader frag 分离器")  #创建应用程序的主窗口实例
    app.MainLoop()


if __name__ == '__main__':
    main()
