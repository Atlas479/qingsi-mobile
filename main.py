#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
理清思路 - 安卓版 (极简测试版)
基于Kivy框架的移动端应用
"""

import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

import datetime

class TaskManagerApp(App):
    """理清思路应用 - 极简版"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tasks = []  # 使用内存存储任务
    
    def build(self):
        """构建应用界面"""
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 标题
        title_label = Label(
            text='📱 理清思路 - 极简版',
            size_hint_y=None,
            height=60,
            font_size=24
        )
        main_layout.add_widget(title_label)
        
        # 输入区域
        input_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=120, spacing=5)
        
        self.title_input = TextInput(
            hint_text='输入任务标题...',
            size_hint_y=None,
            height=40,
            multiline=False
        )
        input_layout.add_widget(self.title_input)
        
        self.desc_input = TextInput(
            hint_text='输入任务描述...',
            size_hint_y=None,
            height=60
        )
        input_layout.add_widget(self.desc_input)
        
        main_layout.add_widget(input_layout)
        
        # 按钮区域
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        add_btn = Button(text='➕ 添加任务', font_size=16)
        add_btn.bind(on_press=self.add_task)
        button_layout.add_widget(add_btn)
        
        clear_btn = Button(text='🗑️ 清空列表', font_size=16)
        clear_btn.bind(on_press=self.clear_tasks)
        button_layout.add_widget(clear_btn)
        
        main_layout.add_widget(button_layout)
        
        # 任务列表
        self.task_list = BoxLayout(orientation='vertical', size_hint_y=None)
        self.task_list.bind(minimum_height=self.task_list.setter('height'))
        
        scroll = ScrollView()
        scroll.add_widget(self.task_list)
        main_layout.add_widget(scroll)
        
        # 状态栏
        status_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        
        self.status_label = Label(
            text='📊 当前任务数：0',
            font_size=14,
            halign='left'
        )
        status_layout.add_widget(self.status_label)
        
        info_btn = Button(text='ℹ️ 关于', size_hint_x=None, width=80, font_size=14)
        info_btn.bind(on_press=self.show_about)
        status_layout.add_widget(info_btn)
        
        main_layout.add_widget(status_layout)
        
        # 初始化显示
        self.update_task_list()
        
        return main_layout
    
    def add_task(self, instance):
        """添加任务"""
        title = self.title_input.text.strip()
        description = self.desc_input.text.strip()
        
        if not title:
            self.show_popup('⚠️ 提示', '请输入任务标题！')
            return
        
        # 创建任务
        task = {
            'id': len(self.tasks) + 1,
            'title': title,
            'description': description or '无描述',
            'created_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': '待办'
        }
        
        self.tasks.append(task)
        
        # 清空输入框
        self.title_input.text = ''
        self.desc_input.text = ''
        
        # 更新显示
        self.update_task_list()
        self.show_popup('✅ 成功', f'任务 "{title}" 添加成功！')
    
    def clear_tasks(self, instance):
        """清空任务列表"""
        if not self.tasks:
            self.show_popup('ℹ️ 提示', '任务列表已经是空的！')
            return
        
        self.tasks.clear()
        self.update_task_list()
        self.show_popup('🗑️ 清空', '所有任务已清空！')
    
    def update_task_list(self):
        """更新任务列表显示"""
        self.task_list.clear_widgets()
        
        if not self.tasks:
            no_task_label = Label(
                text='📝 暂无任务\n\n点击上方"添加任务"按钮开始使用！',
                size_hint_y=None,
                height=100,
                font_size=16,
                halign='center'
            )
            self.task_list.add_widget(no_task_label)
        else:
            for i, task in enumerate(reversed(self.tasks), 1):
                task_item = self.create_task_item(task, i)
                self.task_list.add_widget(task_item)
        
        # 更新状态栏
        self.status_label.text = f'📊 当前任务数：{len(self.tasks)}'
    
    def create_task_item(self, task, index):
        """创建任务项"""
        task_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=100,
            padding=10,
            spacing=5
        )
        
        # 任务标题行
        title_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        
        title_label = Label(
            text=f'{index}. 📋 {task["title"]}',
            size_hint_x=0.8,
            font_size=16,
            bold=True,
            halign='left',
            text_size=(None, None)
        )
        title_layout.add_widget(title_label)
        
        status_label = Label(
            text=f'🔄 {task["status"]}',
            size_hint_x=0.2,
            font_size=12,
            halign='right'
        )
        title_layout.add_widget(status_label)
        
        task_layout.add_widget(title_layout)
        
        # 任务描述
        desc_label = Label(
            text=f'📝 {task["description"]}',
            size_hint_y=None,
            height=25,
            font_size=14,
            halign='left',
            text_size=(None, None)
        )
        task_layout.add_widget(desc_label)
        
        # 时间信息
        time_label = Label(
            text=f'🕐 创建时间：{task["created_time"]}',
            size_hint_y=None,
            height=20,
            font_size=12,
            halign='left',
            text_size=(None, None)
        )
        task_layout.add_widget(time_label)
        
        # 分隔线
        separator = Label(
            text='─' * 60,
            size_hint_y=None,
            height=15,
            font_size=10
        )
        task_layout.add_widget(separator)
        
        return task_layout
    
    def show_popup(self, title, message):
        """显示弹窗"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        message_label = Label(
            text=message,
            font_size=16,
            halign='center'
        )
        content.add_widget(message_label)
        
        close_btn = Button(
            text='确定',
            size_hint_y=None,
            height=40,
            font_size=16
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.5),
            title_size=18
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_about(self, instance):
        """显示关于信息"""
        about_text = """
📱 理清思路 - 极简版

🎯 功能特性：
• 简单的任务管理
• 内存存储（重启后清空）
• 基于Kivy框架
• 支持Android设备

🔧 技术信息：
• Python 3 + Kivy
• 极简化设计
• 测试构建版本

💡 使用说明：
1. 输入任务标题和描述
2. 点击"添加任务"
3. 查看任务列表
4. 可以清空所有任务

🚀 这是APK构建测试版本！
        """
        
        self.show_popup('ℹ️ 关于应用', about_text.strip())

if __name__ == '__main__':
    TaskManagerApp().run() 