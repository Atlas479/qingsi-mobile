#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
理清思路 - 安卓版
基于Kivy框架的移动端应用
支持与电脑版数据同步
"""

import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform

import sqlite3
import datetime
import json
import os
import threading
import requests
from dataclasses import dataclass, asdict
from typing import List, Optional

# 数据类定义
@dataclass
class Task:
    id: Optional[int]
    title: str
    description: str
    priority: int
    category: str
    status: str
    created_date: str
    due_date: Optional[str] = None
    ai_suggestions: Optional[str] = None

@dataclass
class Idea:
    id: Optional[int]
    title: str
    content: str
    category: str
    tags: str
    status: str
    created_date: str
    priority: int
    source: str
    ai_analysis: Optional[str] = None

@dataclass
class FinanceRecord:
    id: Optional[int]
    amount: float
    category: str
    description: str
    payment_method: str
    record_type: str
    created_date: str
    ai_analysis: Optional[str] = None

@dataclass
class LifeEvent:
    id: Optional[int]
    title: str
    event_type: str
    description: str
    event_date: str
    remind_days: int
    is_recurring: bool
    created_date: str
    contact_name: Optional[str] = None
    ai_analysis: Optional[str] = None

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.db_path = self.get_db_path()
        self.init_database()
    
    def get_db_path(self):
        """获取数据库路径"""
        if platform == 'android':
            from android.storage import primary_external_storage_path
            storage_path = primary_external_storage_path()
            return os.path.join(storage_path, 'TaskManager', 'tasks_mobile.db')
        else:
            return 'tasks_mobile.db'
    
    def init_database(self):
        """初始化数据库"""
        # 确保目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建任务表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority INTEGER DEFAULT 3,
                category TEXT DEFAULT '一般',
                status TEXT DEFAULT '待办',
                created_date TEXT,
                due_date TEXT,
                ai_suggestions TEXT,
                sync_status INTEGER DEFAULT 0
            )
        ''')
        
        # 创建想法表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                category TEXT DEFAULT '未分类',
                tags TEXT DEFAULT '',
                status TEXT DEFAULT '新想法',
                created_date TEXT,
                priority INTEGER DEFAULT 3,
                source TEXT DEFAULT '手动',
                ai_analysis TEXT,
                sync_status INTEGER DEFAULT 0
            )
        ''')
        
        # 创建收支记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS finance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount FLOAT,
                category TEXT,
                description TEXT,
                payment_method TEXT,
                record_type TEXT,
                created_date TEXT,
                ai_analysis TEXT,
                sync_status INTEGER DEFAULT 0
            )
        ''')
        
        # 创建生活事件表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS life_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                event_type TEXT,
                description TEXT,
                event_date TEXT,
                remind_days INTEGER,
                is_recurring BOOLEAN,
                contact_name TEXT,
                created_date TEXT,
                ai_analysis TEXT,
                sync_status INTEGER DEFAULT 0
            )
        ''')
        
        # 创建同步配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_config (
                id INTEGER PRIMARY KEY,
                server_url TEXT,
                device_id TEXT,
                last_sync_time TEXT,
                auto_sync BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()

class SyncManager:
    """数据同步管理器"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.device_id = self.get_device_id()
    
    def get_device_id(self):
        """获取设备ID"""
        if platform == 'android':
            from jnius import autoclass
            Settings = autoclass('android.provider.Settings$Secure')
            context = autoclass('org.kivy.android.PythonActivity').mActivity
            return Settings.getString(context.getContentResolver(), Settings.ANDROID_ID)
        else:
            import uuid
            return str(uuid.uuid4())
    
    def sync_with_pc(self, server_url):
        """与电脑版同步数据"""
        try:
            # 上传本地数据
            self.upload_local_data(server_url)
            
            # 下载远程数据
            self.download_remote_data(server_url)
            
            # 更新同步时间
            self.update_sync_time()
            
            return True, "同步成功"
        except Exception as e:
            return False, f"同步失败: {str(e)}"
    
    def upload_local_data(self, server_url):
        """上传本地数据"""
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        
        # 获取未同步的数据
        tables = ['tasks', 'ideas', 'finance_records', 'life_events']
        
        for table in tables:
            cursor.execute(f"SELECT * FROM {table} WHERE sync_status = 0")
            rows = cursor.fetchall()
            
            if rows:
                # 获取列名
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                # 转换为字典列表
                data = []
                for row in rows:
                    data.append(dict(zip(columns, row)))
                
                # 发送到服务器
                response = requests.post(
                    f"{server_url}/api/sync/upload/{table}",
                    json={
                        'device_id': self.device_id,
                        'data': data
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    # 标记为已同步
                    ids = [row[0] for row in rows]
                    cursor.execute(f"UPDATE {table} SET sync_status = 1 WHERE id IN ({','.join(['?'] * len(ids))})", ids)
        
        conn.commit()
        conn.close()
    
    def download_remote_data(self, server_url):
        """下载远程数据"""
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        
        # 获取最后同步时间
        cursor.execute("SELECT last_sync_time FROM sync_config WHERE id = 1")
        result = cursor.fetchone()
        last_sync = result[0] if result else "1970-01-01 00:00:00"
        
        # 从服务器获取更新的数据
        response = requests.get(
            f"{server_url}/api/sync/download",
            params={
                'device_id': self.device_id,
                'since': last_sync
            },
            timeout=30
        )
        
        if response.status_code == 200:
            remote_data = response.json()
            
            # 更新本地数据
            for table, records in remote_data.items():
                for record in records:
                    # 检查是否已存在
                    cursor.execute(f"SELECT id FROM {table} WHERE id = ?", (record['id'],))
                    if cursor.fetchone():
                        # 更新
                        columns = list(record.keys())
                        values = list(record.values())
                        set_clause = ', '.join([f"{col} = ?" for col in columns if col != 'id'])
                        cursor.execute(f"UPDATE {table} SET {set_clause} WHERE id = ?", values[1:] + [record['id']])
                    else:
                        # 插入
                        columns = list(record.keys())
                        values = list(record.values())
                        placeholders = ', '.join(['?'] * len(values))
                        cursor.execute(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})", values)
        
        conn.commit()
        conn.close()
    
    def update_sync_time(self):
        """更新同步时间"""
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT OR REPLACE INTO sync_config (id, device_id, last_sync_time)
            VALUES (1, ?, ?)
        """, (self.device_id, current_time))
        
        conn.commit()
        conn.close()

class VoiceRecorder:
    """语音录制器（移动端适配）"""
    
    def __init__(self):
        self.is_recording = False
        self.setup_permissions()
    
    def setup_permissions(self):
        """设置权限"""
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.RECORD_AUDIO,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])
    
    def start_recording(self, callback=None):
        """开始录音"""
        if platform == 'android':
            # 使用Android原生录音
            return self.android_record(callback)
        else:
            # 使用桌面版录音
            return self.desktop_record(callback)
    
    def android_record(self, callback):
        """Android录音实现"""
        try:
            from jnius import autoclass
            
            # 使用Android MediaRecorder
            MediaRecorder = autoclass('android.media.MediaRecorder')
            AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
            OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
            AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')
            
            self.recorder = MediaRecorder()
            self.recorder.setAudioSource(AudioSource.MIC)
            self.recorder.setOutputFormat(OutputFormat.THREE_GPP)
            self.recorder.setAudioEncoder(AudioEncoder.AMR_NB)
            
            # 设置输出文件
            output_file = "/sdcard/temp_recording.3gp"
            self.recorder.setOutputFile(output_file)
            
            self.recorder.prepare()
            self.recorder.start()
            self.is_recording = True
            
            if callback:
                callback("录音开始")
            
            return True, "录音开始"
        except Exception as e:
            return False, f"录音失败: {str(e)}"
    
    def desktop_record(self, callback):
        """桌面版录音实现"""
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            microphone = sr.Microphone()
            
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source)
            
            if callback:
                callback("请说话...")
            
            with microphone as source:
                audio = recognizer.listen(source, timeout=2, phrase_time_limit=10)
            
            if callback:
                callback("正在识别...")
            
            text = recognizer.recognize_google(audio, language='zh-CN')
            
            if callback:
                callback("识别完成")
            
            return True, text
        except Exception as e:
            return False, f"录音失败: {str(e)}"
    
    def stop_recording(self):
        """停止录音"""
        if self.is_recording and hasattr(self, 'recorder'):
            try:
                self.recorder.stop()
                self.recorder.release()
                self.is_recording = False
                return True, "录音停止"
            except Exception as e:
                return False, f"停止录音失败: {str(e)}"
        return True, "录音已停止"

class MainScreen(Screen):
    """主屏幕"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        self.build_ui()
    
    def build_ui(self):
        """构建UI"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 标题
        title = Label(
            text='🎤 理清思路 - 移动版',
            font_size='24sp',
            size_hint_y=None,
            height='60dp'
        )
        layout.add_widget(title)
        
        # 功能按钮网格
        grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        # 任务管理
        task_btn = Button(
            text='📋 任务管理',
            size_hint_y=None,
            height='80dp'
        )
        task_btn.bind(on_press=self.goto_tasks)
        grid.add_widget(task_btn)
        
        # 想法记事本
        idea_btn = Button(
            text='💡 想法记事本',
            size_hint_y=None,
            height='80dp'
        )
        idea_btn.bind(on_press=self.goto_ideas)
        grid.add_widget(idea_btn)
        
        # 收支管理
        finance_btn = Button(
            text='💰 收支管理',
            size_hint_y=None,
            height='80dp'
        )
        finance_btn.bind(on_press=self.goto_finance)
        grid.add_widget(finance_btn)
        
        # 生活助手
        life_btn = Button(
            text='📅 生活助手',
            size_hint_y=None,
            height='80dp'
        )
        life_btn.bind(on_press=self.goto_life)
        grid.add_widget(life_btn)
        
        # 语音录制
        voice_btn = Button(
            text='🎤 语音录制',
            size_hint_y=None,
            height='80dp'
        )
        voice_btn.bind(on_press=self.goto_voice)
        grid.add_widget(voice_btn)
        
        # 数据同步
        sync_btn = Button(
            text='🔄 数据同步',
            size_hint_y=None,
            height='80dp'
        )
        sync_btn.bind(on_press=self.goto_sync)
        grid.add_widget(sync_btn)
        
        layout.add_widget(grid)
        
        # 今日提醒
        reminder_layout = BoxLayout(orientation='vertical', size_hint_y=None, height='200dp')
        reminder_title = Label(text='⏰ 今日提醒', font_size='18sp', size_hint_y=None, height='40dp')
        reminder_layout.add_widget(reminder_title)
        
        self.reminder_scroll = ScrollView()
        self.reminder_content = BoxLayout(orientation='vertical', size_hint_y=None)
        self.reminder_content.bind(minimum_height=self.reminder_content.setter('height'))
        self.reminder_scroll.add_widget(self.reminder_content)
        reminder_layout.add_widget(self.reminder_scroll)
        
        layout.add_widget(reminder_layout)
        
        self.add_widget(layout)
        
        # 加载今日提醒
        Clock.schedule_once(self.load_reminders, 1)
    
    def load_reminders(self, dt):
        """加载今日提醒"""
        app = App.get_running_app()
        reminders = app.get_today_reminders()
        
        self.reminder_content.clear_widgets()
        
        if not reminders:
            no_reminder = Label(
                text='今天没有提醒事项',
                size_hint_y=None,
                height='40dp'
            )
            self.reminder_content.add_widget(no_reminder)
        else:
            for reminder in reminders:
                reminder_item = Label(
                    text=f"• {reminder['title']} ({reminder['type']})",
                    size_hint_y=None,
                    height='40dp',
                    text_size=(None, None)
                )
                self.reminder_content.add_widget(reminder_item)
    
    def goto_tasks(self, instance):
        """跳转到任务管理"""
        self.manager.current = 'tasks'
    
    def goto_ideas(self, instance):
        """跳转到想法记事本"""
        self.manager.current = 'ideas'
    
    def goto_finance(self, instance):
        """跳转到收支管理"""
        self.manager.current = 'finance'
    
    def goto_life(self, instance):
        """跳转到生活助手"""
        self.manager.current = 'life'
    
    def goto_voice(self, instance):
        """跳转到语音录制"""
        self.manager.current = 'voice'
    
    def goto_sync(self, instance):
        """跳转到数据同步"""
        self.manager.current = 'sync'

class TaskScreen(Screen):
    """任务管理屏幕"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'tasks'
        self.build_ui()
    
    def build_ui(self):
        """构建UI"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 顶部栏
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        
        back_btn = Button(text='← 返回', size_hint_x=None, width='80dp')
        back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(back_btn)
        
        title = Label(text='📋 任务管理', font_size='20sp')
        top_bar.add_widget(title)
        
        add_btn = Button(text='+ 新建', size_hint_x=None, width='80dp')
        add_btn.bind(on_press=self.add_task)
        top_bar.add_widget(add_btn)
        
        layout.add_widget(top_bar)
        
        # 任务列表
        self.task_scroll = ScrollView()
        self.task_list = BoxLayout(orientation='vertical', size_hint_y=None)
        self.task_list.bind(minimum_height=self.task_list.setter('height'))
        self.task_scroll.add_widget(self.task_list)
        layout.add_widget(self.task_scroll)
        
        self.add_widget(layout)
        
        # 加载任务
        Clock.schedule_once(self.load_tasks, 0.1)
    
    def load_tasks(self, dt):
        """加载任务列表"""
        app = App.get_running_app()
        tasks = app.get_tasks()
        
        self.task_list.clear_widgets()
        
        for task in tasks:
            task_item = self.create_task_item(task)
            self.task_list.add_widget(task_item)
    
    def create_task_item(self, task):
        """创建任务项"""
        item_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height='100dp',
            padding=5
        )
        
        # 任务标题和状态
        title_layout = BoxLayout(orientation='horizontal')
        
        title_label = Label(
            text=task['title'],
            font_size='16sp',
            text_size=(None, None),
            halign='left'
        )
        title_layout.add_widget(title_label)
        
        status_label = Label(
            text=task['status'],
            size_hint_x=None,
            width='80dp',
            font_size='14sp'
        )
        title_layout.add_widget(status_label)
        
        item_layout.add_widget(title_layout)
        
        # 任务详情
        detail_label = Label(
            text=f"分类: {task['category']} | 优先级: {task['priority']} | {task['created_date'][:10]}",
            font_size='12sp',
            size_hint_y=None,
            height='30dp'
        )
        item_layout.add_widget(detail_label)
        
        # 分隔线
        separator = Label(text='─' * 50, size_hint_y=None, height='20dp')
        item_layout.add_widget(separator)
        
        return item_layout
    
    def add_task(self, instance):
        """添加新任务"""
        self.show_task_dialog()
    
    def show_task_dialog(self, task=None):
        """显示任务编辑对话框"""
        content = BoxLayout(orientation='vertical', spacing=10)
        
        # 标题输入
        title_input = TextInput(
            hint_text='任务标题',
            multiline=False,
            size_hint_y=None,
            height='40dp'
        )
        content.add_widget(title_input)
        
        # 描述输入
        desc_input = TextInput(
            hint_text='任务描述',
            size_hint_y=None,
            height='100dp'
        )
        content.add_widget(desc_input)
        
        # 分类选择
        category_spinner = Spinner(
            text='选择分类',
            values=['工作', '学习', '生活', '健康', '娱乐', '一般'],
            size_hint_y=None,
            height='40dp'
        )
        content.add_widget(category_spinner)
        
        # 优先级选择
        priority_spinner = Spinner(
            text='选择优先级',
            values=['1-最高', '2-高', '3-中', '4-低', '5-最低'],
            size_hint_y=None,
            height='40dp'
        )
        content.add_widget(priority_spinner)
        
        # 按钮
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        
        save_btn = Button(text='保存')
        save_btn.bind(on_press=lambda x: self.save_task(
            title_input.text,
            desc_input.text,
            category_spinner.text,
            priority_spinner.text,
            popup
        ))
        btn_layout.add_widget(save_btn)
        
        cancel_btn = Button(text='取消')
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(cancel_btn)
        
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='新建任务',
            content=content,
            size_hint=(0.9, 0.8)
        )
        popup.open()
    
    def save_task(self, title, description, category, priority, popup):
        """保存任务"""
        if not title.strip():
            return
        
        app = App.get_running_app()
        
        task_data = {
            'title': title,
            'description': description,
            'category': category if category != '选择分类' else '一般',
            'priority': int(priority[0]) if priority != '选择优先级' else 3,
            'status': '待办',
            'created_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        app.add_task(task_data)
        popup.dismiss()
        self.load_tasks(None)
    
    def go_back(self, instance):
        """返回主屏幕"""
        self.manager.current = 'main'

class TaskManagerApp(App):
    """主应用类"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = DatabaseManager()
        self.sync_manager = SyncManager(self.db_manager)
        self.voice_recorder = VoiceRecorder()
    
    def build(self):
        """构建应用"""
        sm = ScreenManager()
        
        # 添加屏幕
        sm.add_widget(MainScreen())
        sm.add_widget(TaskScreen())
        # 这里可以添加更多屏幕
        
        return sm
    
    def get_tasks(self):
        """获取任务列表"""
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tasks ORDER BY created_date DESC")
        rows = cursor.fetchall()
        
        # 获取列名
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [col[1] for col in cursor.fetchall()]
        
        tasks = []
        for row in rows:
            tasks.append(dict(zip(columns, row)))
        
        conn.close()
        return tasks
    
    def add_task(self, task_data):
        """添加任务"""
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO tasks (title, description, priority, category, status, created_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            task_data['title'],
            task_data['description'],
            task_data['priority'],
            task_data['category'],
            task_data['status'],
            task_data['created_date']
        ))
        
        conn.commit()
        conn.close()
    
    def get_today_reminders(self):
        """获取今日提醒"""
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        
        today = datetime.datetime.now().date()
        
        # 获取今日到期的任务
        cursor.execute("""
            SELECT title, 'task' as type FROM tasks 
            WHERE due_date = ? AND status != '已完成'
        """, (today.strftime("%Y-%m-%d"),))
        
        reminders = []
        for row in cursor.fetchall():
            reminders.append({
                'title': row[0],
                'type': '任务'
            })
        
        # 获取今日生活事件
        cursor.execute("""
            SELECT title, event_type FROM life_events 
            WHERE event_date = ?
        """, (today.strftime("%Y-%m-%d"),))
        
        for row in cursor.fetchall():
            reminders.append({
                'title': row[0],
                'type': row[1]
            })
        
        conn.close()
        return reminders

if __name__ == '__main__':
    TaskManagerApp().run() 