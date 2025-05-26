#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
理清思路 - Hello World版本
使用Kivy官方最简单的示例确保构建成功
"""

import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

class HelloWorldApp(App):
    """最简单的Kivy应用"""
    
    def build(self):
        """构建应用界面"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # 欢迎标签
        welcome_label = Label(
            text='🎉 理清思路APK构建成功！\n\n这是一个测试版本\n证明我们的构建流程正常工作',
            font_size=18,
            halign='center'
        )
        layout.add_widget(welcome_label)
        
        # 测试按钮
        test_button = Button(
            text='点击测试',
            size_hint_y=None,
            height=50,
            font_size=16
        )
        test_button.bind(on_press=self.on_button_click)
        layout.add_widget(test_button)
        
        # 状态标签
        self.status_label = Label(
            text='准备就绪',
            font_size=14
        )
        layout.add_widget(self.status_label)
        
        return layout
    
    def on_button_click(self, instance):
        """按钮点击事件"""
        self.status_label.text = '✅ 按钮点击成功！\nKivy应用运行正常！'

if __name__ == '__main__':
    HelloWorldApp().run() 