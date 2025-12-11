import wx
import os
import json


class CompileResultDialog(wx.Dialog):
    """编译结果对话框（非模态）"""
    def __init__(self, parent, frag_file_name, output):
        super().__init__(parent, title=f"编译结果 - {frag_file_name}", size=(800, 550))
        
        # 设置对话框样式，允许同时打开多个
        self.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        
        # 创建控件
        text_ctrl = wx.TextCtrl(self, value=output, 
                               style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP | wx.TE_RICH2)
        # 设置浅灰色背景
        text_ctrl.SetBackgroundColour(wx.Colour(200, 200, 200))
        # 使用与PowerShell相同的字体，确保显示一致性
        try:
            # PowerShell常用字体优先级：Lucida Console -> Consolas -> 系统等宽字体
            font_names = ["Cascadia Mono", "Consolas", "Courier New"]
            # font_names = ["Lucida Console", "Consolas", "Courier New"]
            selected_font = None
            
            for font_name in font_names:
                try:
                    font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                  wx.FONTWEIGHT_NORMAL, faceName=font_name)
                    if font.IsOk():
                        selected_font = font
                        break
                except:
                    continue
            
            if selected_font:
                text_ctrl.SetFont(selected_font)
            else:
                # 所有指定字体都不可用时使用系统等宽字体
                text_ctrl.SetFont(wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        except:
            # 异常情况下使用系统等宽字体
            text_ctrl.SetFont(wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        
        # 添加关闭按钮
        self.close_btn = wx.Button(self, label="关闭")
        self.close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        self.close_btn.SetBackgroundColour(wx.Colour(245, 95, 90))
        
        # 添加复制按钮
        copy_btn = wx.Button(self, label="复制结果")
        copy_btn.Bind(wx.EVT_BUTTON, lambda e: self.copy_to_clipboard(output))
        copy_btn.SetBackgroundColour(wx.Colour(155, 225, 110))
        
        # 计算Longest Path Cycles三个值的和
        cycles_sum = self.calculate_longest_path_cycles_sum(output)
        
        # 创建结果显示文本
        result_text = ""
        if cycles_sum is not None:
            result_text = f"Longest Path Cycles 总和: {cycles_sum}"
        else:
            result_text = "Longest Path Cycles: --"
        
        result_label = wx.StaticText(self, label=result_text)
        
        # 根据总和结果分级设置字体颜色
        if cycles_sum is not None:
            if cycles_sum <= 40:
                # 40以下：绿色 - 良好性能
                result_label.SetForegroundColour(wx.Colour(0, 180, 0))  # 绿色
            elif cycles_sum <= 79:
                # 41~79：橙色 - 中等性能
                result_label.SetForegroundColour(wx.Colour(255, 140, 0))  # 橙色
            else:
                # 80以上：红色 - 需要优化
                result_label.SetForegroundColour(wx.Colour(220, 0, 0))  # 红色
        else:
            # 无数据：蓝色
            result_label.SetForegroundColour(wx.Colour(0, 100, 200))  # 蓝色
        
        result_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        # 布局
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        
        # 底部按钮和结果区域
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 左侧：结果文本
        bottom_sizer.Add(result_label, proportion=1, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=10)
        
        # 右侧：按钮
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(copy_btn, flag=wx.ALIGN_CENTER | wx.RIGHT, border=10)
        btn_sizer.Add(self.close_btn, flag=wx.ALIGN_CENTER)
        bottom_sizer.Add(btn_sizer, flag=wx.ALIGN_CENTER | wx.RIGHT, border=10)
        
        sizer.Add(bottom_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        self.SetSizer(sizer)
        
        # 居中显示
        self.Centre()
        
        # 绑定关闭事件
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        # 设置默认按钮为关闭按钮
        self.close_btn.SetDefault()
        
        # 在对话框显示后将焦点设置到关闭按钮
        self.Bind(wx.EVT_SHOW, self.on_show)
    
    def calculate_longest_path_cycles_sum(self, output):
        """计算Longest Path Cycles三个值的和"""
        try:
            # 查找"Longest Path Cycles:"在文本中的位置
            lines = output.split('\n')
            for line in lines:
                if "Longest Path Cycles:" in line:
                    # 提取冒号后面的部分
                    parts = line.split("Longest Path Cycles:")
                    if len(parts) > 1:
                        values_str = parts[1].strip()
                        
                        # 提取所有数字（可能用逗号、空格分隔）
                        import re
                        numbers = re.findall(r'\d+', values_str)
                        
                        if len(numbers) >= 3:
                            # 取前三个数字
                            try:
                                num1 = int(numbers[0])
                                num2 = int(numbers[1])
                                num3 = int(numbers[2])
                                return num1 + num2 + num3
                            except ValueError:
                                return None
            return None
        except Exception as e:
            print(f"计算Longest Path Cycles总和时出错: {e}")
            return None
    
    def on_show(self, event):
        """处理对话框显示事件：将焦点设置到关闭按钮"""
        if event.IsShown():
            # 延迟设置焦点，确保对话框完全显示
            wx.CallAfter(self.close_btn.SetFocus)
        event.Skip()
    
    def on_close(self, event):
        """处理关闭事件"""
        self.Destroy()
    
    @staticmethod
    def copy_to_clipboard(text):
        """复制文本到剪贴板"""
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(text))
            wx.TheClipboard.Close()
            # wx.MessageBox("结果已复制到剪贴板", "提示", wx.OK | wx.ICON_INFORMATION)


class ShaderBrowser(wx.Frame):
    # 版本号定义，方便更新
    VERSION = "1.2"
    CONFIG_FILE = "shader_browser_config.json"
    
    def __init__(self, parent, title):
        # 在标题中添加版本号
        full_title = f"{title} v{self.VERSION}"
        super(ShaderBrowser, self).__init__(parent, title=full_title, size=(800, 700))

        # 设置窗口图标
        self.SetIcon(self.load_icon())
        
        self.InitUI()
        self.Centre()
        self.Show()
        
        # 加载保存的路径
        self.load_saved_path()
    
    def load_icon(self):
        """加载窗口图标"""
        try:
            # 尝试加载mm1.ico文件
            icon_path = "mm1.ico"
            if os.path.exists(icon_path):
                icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
                if icon.IsOk():
                    return icon
            
            # 如果文件不存在或加载失败，创建默认图标
            return self.create_default_icon()
        except Exception as e:
            print(f"加载图标失败: {e}")
            return self.create_default_icon()
    
    def create_default_icon(self):
        """创建默认图标"""
        try:
            # 创建一个简单的默认图标（16x16和32x32）
            icon = wx.Icon()
            
            # 创建16x16位图
            bmp16 = wx.Bitmap(16, 16)
            dc = wx.MemoryDC(bmp16)
            dc.SetBackground(wx.Brush(wx.Colour(0, 120, 215)))  # 蓝色背景
            dc.Clear()
            dc.SetTextForeground(wx.Colour(255, 255, 255))  # 白色文字
            dc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            dc.DrawText("S", 4, 2)  # 绘制"S"表示Shader
            dc.SelectObject(wx.NullBitmap)
            
            # 创建32x32位图  
            bmp32 = wx.Bitmap(32, 32)
            dc = wx.MemoryDC(bmp32)
            dc.SetBackground(wx.Brush(wx.Colour(0, 120, 215)))  # 蓝色背景
            dc.Clear()
            dc.SetTextForeground(wx.Colour(255, 255, 255))  # 白色文字
            dc.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            dc.DrawText("S", 10, 6)  # 绘制"S"表示Shader
            dc.SelectObject(wx.NullBitmap)
            
            # 将16x16位图复制到图标
            icon.CopyFromBitmap(bmp16)
            return icon
        except:
            # 如果创建默认图标也失败，返回空图标
            return wx.Icon()
    
    def InitUI(self):
        panel = wx.Panel(self)
        
        # 创建垂直布局管理器
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # 第一行：路径标签和输入框
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        self.browse_btn = wx.Button(panel, label="浏览路径:", size=(68, -1))
        self.browse_btn.Bind(wx.EVT_BUTTON, self.on_browse)
        # 设置橙黄色背景
        self.browse_btn.SetBackgroundColour(wx.Colour(255, 225, 110))  # 橙黄色
        hbox1.Add(self.browse_btn, flag=wx.EXPAND)
        self.path_text = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.path_text.Bind(wx.EVT_TEXT_ENTER, self.on_path_enter)
        # 设置浅黄色背景
        self.path_text.SetBackgroundColour(wx.Colour(255, 255, 224))  # 浅黄色
        hbox1.Add(self.path_text, proportion=1, flag=wx.EXPAND)
        
        vbox.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # 第二行：操作按钮
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        self.workFrag_btn = wx.Button(panel, label="分离frag")
        self.workFrag_btn.Bind(wx.EVT_BUTTON, self.on_separate_frag)
        # 设置浅蓝色背景
        self.workFrag_btn.SetBackgroundColour(wx.Colour(173, 216, 230))  # 浅蓝色
        hbox2.Add(self.workFrag_btn, flag=wx.ALIGN_CENTER | wx.LEFT, border=10)
        
        self.refresh_btn = wx.Button(panel, label="刷新")
        self.refresh_btn.Bind(wx.EVT_BUTTON, self.on_refresh)
        # 设置绿色背景
        self.refresh_btn.SetBackgroundColour(wx.Colour(144, 238, 144))  # 浅绿色
        hbox2.Add(self.refresh_btn, flag=wx.ALIGN_CENTER | wx.LEFT, border=10)
        
        vbox.Add(hbox2, flag=wx.ALIGN_LEFT | wx.TOP, border=10)
        
        # 第三行：双列表标签行
        hbox_labels = wx.BoxSizer(wx.HORIZONTAL)
        
        file_label = wx.StaticText(panel, label="shader 文件列表:")
        hbox_labels.Add(file_label, proportion=1, flag=wx.EXPAND)
        
        # frag标签和总和显示区域
        frag_label_sizer = wx.BoxSizer(wx.HORIZONTAL)
        frag_label = wx.StaticText(panel, label="frag 列表:")
        frag_label_sizer.Add(frag_label, flag=wx.ALIGN_CENTER_VERTICAL)
        
        # 添加总和显示文本（初始为空）
        self.frag_sum_label = wx.StaticText(panel, label="")
        self.frag_sum_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        frag_label_sizer.Add(self.frag_sum_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=10)
        
        hbox_labels.Add(frag_label_sizer, proportion=1, flag=wx.EXPAND)
        
        vbox.Add(hbox_labels, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        
        # 第四行：双列表框
        hbox_lists = wx.BoxSizer(wx.HORIZONTAL)

        # 左侧：文件列表框
        self.file_list = wx.ListBox(panel, style=wx.LB_SINGLE | wx.LB_HSCROLL)
        self.file_list.Bind(wx.EVT_LISTBOX_DCLICK, self.on_file_double_click)
        self.file_list.SetMinSize((0, -1))  # 👈 关键：允许水平方向被压缩
        hbox_lists.Add(self.file_list, proportion=1, flag=wx.EXPAND)

        # 右侧：frag 列表框
        self.frag_list = wx.ListBox(panel, style=wx.LB_SINGLE | wx.LB_HSCROLL)
        self.frag_list.Bind(wx.EVT_LISTBOX_DCLICK, self.on_frag_double_click)
        self.frag_list.Bind(wx.EVT_LISTBOX, self.on_frag_click)
        self.frag_list.Bind(wx.EVT_CHAR_HOOK, self.on_frag_char_hook)
        self.frag_list.SetMinSize((0, -1))  # 👈 同样设置
        hbox_lists.Add(self.frag_list, proportion=1, flag=wx.EXPAND)
        
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
            self.status_bar.SetStatusText(f"路径已保存: {self.CONFIG_FILE}")
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
                        self.status_bar.SetStatusText(f"已加载路径: {last_path}")
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
    
    def on_frag_click(self, event):
        """处理frag列表单击事件：计算并显示Longest Path Cycles总和"""
        selection = self.frag_list.GetSelection()
        if selection == wx.NOT_FOUND:
            # 清空显示
            self.frag_sum_label.SetLabel("")
            return
        
        frag_file_name = self.frag_list.GetString(selection)
        current_path = self.path_text.GetValue()
        if not current_path:
            self.frag_sum_label.SetLabel("请先选择路径")
            self.frag_sum_label.SetForegroundColour(wx.Colour(0, 100, 200))  # 蓝色
            return
        
        # 构建frag文件的完整路径
        frags_dir = os.path.join(current_path, "Frags")
        frag_file_path = os.path.join(frags_dir, frag_file_name)
        
        if not os.path.exists(frag_file_path):
            self.frag_sum_label.SetLabel("文件不存在")
            self.frag_sum_label.SetForegroundColour(wx.Colour(0, 100, 200))  # 蓝色
            return
        
        # 查找malisc.exe
        malisc_path = self.find_malisc_exe()
        if not malisc_path:
            self.frag_sum_label.SetLabel("未找到malisc.exe")
            self.frag_sum_label.SetForegroundColour(wx.Colour(0, 100, 200))  # 蓝色
            return
        
        # 在新线程中执行编译并计算总和
        import threading
        thread = threading.Thread(
            target=self.calculate_frag_cycles_sum_in_thread,
            args=(frag_file_name, frag_file_path, malisc_path)
        )
        thread.daemon = True
        thread.start()
        
        # 显示加载中状态
        self.frag_sum_label.SetLabel(f"{frag_file_name}")
        self.frag_sum_label.SetForegroundColour(wx.Colour(0, 100, 200))  # 蓝色
    
    def calculate_frag_cycles_sum_in_thread(self, frag_file_name, frag_file_path, malisc_path):
        """在新线程中编译frag文件并计算Longest Path Cycles总和"""
        try:
            # 使用powershell执行malisc.exe
            cmd = f'powershell -Command "& \'{malisc_path}\' \'{frag_file_path}\'"'
            
            # 执行命令
            import subprocess
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
            
            # 获取输出
            output = result.stdout
            if result.returncode != 0:
                output += f"\n\n错误代码: {result.returncode}"
                if result.stderr:
                    output += f"\n错误信息: {result.stderr}"
            
            # 计算Longest Path Cycles总和
            cycles_sum = self.calculate_longest_path_cycles_sum(output)
            
            # 在主线程中更新显示
            wx.CallAfter(self.update_frag_sum_display, frag_file_name, cycles_sum)
            
        except Exception as e:
            error_msg = f"计算失败: {str(e)}"
            wx.CallAfter(self.update_frag_sum_display, frag_file_name, None, error_msg)
    
    def update_frag_sum_display(self, frag_file_name, cycles_sum, error_msg=None):
        """更新frag总和显示"""
        if error_msg:
            # 显示错误信息
            self.frag_sum_label.SetLabel(f"错误: {error_msg[:30]}...")
            self.frag_sum_label.SetForegroundColour(wx.Colour(0, 100, 200))  # 蓝色
            return
        
        # 创建显示文本
        if cycles_sum is not None:
            display_text = f"复杂度:{cycles_sum}"
            
            # 根据总和设置颜色（与CompileResultDialog一致）
            if cycles_sum <= 40:
                # 40以下：绿色 - 良好性能
                self.frag_sum_label.SetForegroundColour(wx.Colour(0, 180, 0))  # 绿色
            elif cycles_sum <= 79:
                # 41~79：橙色 - 中等性能
                self.frag_sum_label.SetForegroundColour(wx.Colour(255, 140, 0))  # 橙色
            else:
                # 80以上：红色 - 需要优化
                self.frag_sum_label.SetForegroundColour(wx.Colour(220, 0, 0))  # 红色
        else:
            display_text = "--"
            self.frag_sum_label.SetForegroundColour(wx.Colour(0, 100, 200))  # 蓝色
        
        self.frag_sum_label.SetLabel(display_text)
    
    def calculate_longest_path_cycles_sum(self, output):
        """计算Longest Path Cycles三个值的和（与CompileResultDialog中的方法相同）"""
        try:
            # 查找"Longest Path Cycles:"在文本中的位置
            lines = output.split('\n')
            for line in lines:
                if "Longest Path Cycles:" in line:
                    # 提取冒号后面的部分
                    parts = line.split("Longest Path Cycles:")
                    if len(parts) > 1:
                        values_str = parts[1].strip()
                        
                        # 提取所有数字（可能用逗号、空格分隔）
                        import re
                        numbers = re.findall(r'\d+', values_str)
                        
                        if len(numbers) >= 3:
                            # 取前三个数字
                            try:
                                num1 = int(numbers[0])
                                num2 = int(numbers[1])
                                num3 = int(numbers[2])
                                return num1 + num2 + num3
                            except ValueError:
                                return None
            return None
        except Exception as e:
            print(f"计算Longest Path Cycles总和时出错: {e}")
            return None
    
    def on_frag_char_hook(self, event):
        """处理frag列表键盘事件：回车键触发双击事件（使用CHAR_HOOK）"""
        keycode = event.GetKeyCode()
        
        # 检查是否是回车键（Enter键）
        if keycode == wx.WXK_RETURN or keycode == wx.WXK_NUMPAD_ENTER:
            # 阻止事件继续传播
            event.Skip(False)
            # 触发双击事件
            self.on_frag_double_click(event)
            return
        
        # 其他按键继续正常处理
        event.Skip()
    
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
        
        # 在新线程中执行编译，避免界面卡顿
        import threading
        thread = threading.Thread(
            target=self.compile_frag_in_thread,
            args=(frag_file_name, frag_file_path, malisc_path)
        )
        thread.daemon = True
        thread.start()
    
    def compile_frag_in_thread(self, frag_file_name, frag_file_path, malisc_path):
        """在新线程中编译frag文件并显示结果"""
        try:
            # 使用powershell执行malisc.exe
            cmd = f'powershell -Command "& \'{malisc_path}\' \'{frag_file_path}\'"'
            
            # 在主线程中更新状态栏
            wx.CallAfter(self.status_bar.SetStatusText, f"正在编译: {frag_file_name}")
            
            # 执行命令
            import subprocess
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
            
            # 显示结果
            output = result.stdout
            if result.returncode != 0:
                output += f"\n\n错误代码: {result.returncode}"
                if result.stderr:
                    output += f"\n错误信息: {result.stderr}"
            
            # 在主线程中创建和显示非模态对话框
            wx.CallAfter(self.show_compile_result, frag_file_name, output)
            
            # 在主线程中更新状态栏
            wx.CallAfter(self.status_bar.SetStatusText, f"编译完成: {frag_file_name}")
            
        except Exception as e:
            error_msg = f"编译失败: {str(e)}"
            wx.CallAfter(self.status_bar.SetStatusText, error_msg)
            wx.CallAfter(wx.MessageBox, error_msg, "错误", wx.OK | wx.ICON_ERROR)
    
    def show_compile_result(self, frag_file_name, output):
        """显示编译结果对话框（非模态）"""
        # 创建非模态对话框
        dlg = CompileResultDialog(self, frag_file_name, output)
        dlg.Show()
    
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
        self.frag_sum_label.SetLabel("--")
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
        """加载指定目录中的所有 .shader 文件，并刷新frag列表"""
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
            else:
                self.status_bar.SetStatusText("未找到 .shader 文件")
            
            # 无论是否找到.shader文件，都尝试加载frag文件
            self.load_frag_files(directory)
                
        except Exception as e:
            self.status_bar.SetStatusText(f"错误: {str(e)}")


def main():
    app = wx.App(False)
    frame = ShaderBrowser(None, "Shader frag 分离器(YD)")  #创建应用程序的主窗口实例
    app.MainLoop()


if __name__ == '__main__':
    main()
