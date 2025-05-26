#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
理清思路 - 安卓版 (简化测试版)
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
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock

import sqlite3
import datetime
import json
import os

class DatabaseManager:
    """简化的数据库管理器"""
    
    def __init__(self):
        self.db_path = 'tasks_simple.db'
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建简单的任务表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                created_date TEXT,
                status TEXT DEFAULT '待办'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_task(self, title, description):
        """添加任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (title, description, created_date)
            VALUES (?, ?, ?)
        ''', (title, description, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        conn.commit()
        conn.close()
    
    def get_tasks(self):
        """获取所有任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tasks ORDER BY created_date DESC')
        tasks = cursor.fetchall()
        
        conn.close()
        return tasks

class MainScreen(Screen):
    """主屏幕"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = DatabaseManager()
        self.build_ui()
    
    def build_ui(self):
        """构建用户界面"""
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 标题
        title_label = Label(
            text='理清思路 - 简化版',
            size_hint_y=None,
            height=50,
            font_size=20
        )
        main_layout.add_widget(title_label)
        
        # 输入区域
        input_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=120, spacing=5)
        
        self.title_input = TextInput(
            hint_text='任务标题',
            size_hint_y=None,
            height=40,
            multiline=False
        )
        input_layout.add_widget(self.title_input)
        
        self.desc_input = TextInput(
            hint_text='任务描述',
            size_hint_y=None,
            height=60
        )
        input_layout.add_widget(self.desc_input)
        
        main_layout.add_widget(input_layout)
        
        # 按钮区域
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        add_btn = Button(text='添加任务')
        add_btn.bind(on_press=self.add_task)
        button_layout.add_widget(add_btn)
        
        refresh_btn = Button(text='刷新列表')
        refresh_btn.bind(on_press=self.refresh_tasks)
        button_layout.add_widget(refresh_btn)
        
        main_layout.add_widget(button_layout)
        
        # 任务列表
        self.task_list = BoxLayout(orientation='vertical', size_hint_y=None)
        self.task_list.bind(minimum_height=self.task_list.setter('height'))
        
        scroll = ScrollView()
        scroll.add_widget(self.task_list)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
        
        # 加载任务
        Clock.schedule_once(self.load_tasks, 0.1)
    
    def add_task(self, instance):
        """添加任务"""
        title = self.title_input.text.strip()
        description = self.desc_input.text.strip()
        
        if not title:
            self.show_popup('错误', '请输入任务标题')
            return
        
        try:
            self.db_manager.add_task(title, description)
            self.title_input.text = ''
            self.desc_input.text = ''
            self.load_tasks()
            self.show_popup('成功', '任务添加成功！')
        except Exception as e:
            self.show_popup('错误', f'添加任务失败：{str(e)}')
    
    def refresh_tasks(self, instance):
        """刷新任务列表"""
        self.load_tasks()
    
    def load_tasks(self, dt=None):
        """加载任务列表"""
        self.task_list.clear_widgets()
        
        try:
            tasks = self.db_manager.get_tasks()
            
            if not tasks:
                no_task_label = Label(
                    text='暂无任务，请添加新任务',
                    size_hint_y=None,
                    height=50
                )
                self.task_list.add_widget(no_task_label)
                return
            
            for task in tasks:
                task_item = self.create_task_item(task)
                self.task_list.add_widget(task_item)
                
        except Exception as e:
            error_label = Label(
                text=f'加载任务失败：{str(e)}',
                size_hint_y=None,
                height=50
            )
            self.task_list.add_widget(error_label)
    
    def create_task_item(self, task):
        """创建任务项"""
        task_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=80,
            padding=5,
            spacing=2
        )
        
        # 任务标题
        title_label = Label(
            text=f'📋 {task[1]}',  # task[1] 是标题
            size_hint_y=None,
            height=30,
            text_size=(None, None),
            halign='left'
        )
        task_layout.add_widget(title_label)
        
        # 任务描述和时间
        info_text = f'📝 {task[2] or "无描述"}\n🕐 {task[3]}'  # task[2] 是描述，task[3] 是创建时间
        info_label = Label(
            text=info_text,
            size_hint_y=None,
            height=40,
            text_size=(None, None),
            halign='left',
            font_size=12
        )
        task_layout.add_widget(info_label)
        
        # 添加分隔线
        separator = Label(
            text='─' * 50,
            size_hint_y=None,
            height=10,
            font_size=10
        )
        task_layout.add_widget(separator)
        
        return task_layout
    
    def show_popup(self, title, message):
        """显示弹窗"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        message_label = Label(text=message)
        content.add_widget(message_label)
        
        close_btn = Button(text='确定', size_hint_y=None, height=40)
        content.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

class TaskManagerApp(App):
    """理清思路应用"""
    
    def build(self):
        """构建应用"""
        sm = ScreenManager()
        
        main_screen = MainScreen(name='main')
        sm.add_widget(main_screen)
        
        return sm

if __name__ == '__main__':
    TaskManagerApp().run() 