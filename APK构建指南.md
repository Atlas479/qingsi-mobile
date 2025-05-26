# 📱 理清思路APK构建指南

## 🎯 快速开始

### 方法1：GitHub Actions自动构建（推荐）

1. **创建GitHub仓库**
   - 访问 https://github.com/new
   - 仓库名：`qingsi-mobile` 或 `理清思路-手机版`
   - 设为公开仓库（Public）
   - 不要初始化README

2. **上传代码**
   ```bash
   # 运行上传脚本
   上传到GitHub.bat
   ```
   或手动执行：
   ```bash
   git init
   git add .
   git commit -m "🎉 初始提交：理清思路Android版"
   git remote add origin https://github.com/用户名/仓库名.git
   git branch -M main
   git push -u origin main
   ```

3. **等待构建**
   - 访问GitHub仓库
   - 点击 "Actions" 标签页
   - 等待构建完成（约10-15分钟）

4. **下载APK**
   - 构建完成后，点击最新的构建任务
   - 在 "Artifacts" 部分下载 "理清思路-APK"
   - 解压得到APK文件

## 🔧 构建配置说明

### buildozer.spec关键配置
```ini
[app]
title = 理清思路
package.name = qingsi
package.domain = com.qingsi

version = 1.0
requirements = python3,kivy==2.1.0,kivymd,requests,sqlite3

[buildozer]
log_level = 2
```

### GitHub Actions配置
- 文件位置：`.github/workflows/build-apk.yml`
- 自动触发：推送到main分支
- 构建环境：Ubuntu Latest + Python 3.10
- 输出：APK文件上传到Artifacts

## 📱 APK安装

1. **下载APK**
   - 从GitHub Actions Artifacts下载
   - 文件名：`理清思路-debug.apk`

2. **安装到手机**
   - 开启"未知来源"安装权限
   - 点击APK文件安装
   - 授予必要权限（存储、麦克风）

3. **首次使用**
   - 打开应用
   - 允许权限请求
   - 开始使用各项功能

## 🛠️ 故障排除

### 构建失败
- 检查buildozer.spec配置
- 查看Actions日志中的错误信息
- 确保所有依赖都在requirements中

### 安装失败
- 确保Android版本7.0+
- 检查存储空间是否充足
- 重新下载APK文件

### 权限问题
- 手动在设置中授予权限
- 重启应用后重试

## 📊 构建状态

| 组件 | 状态 | 说明 |
|------|------|------|
| 主应用 | ✅ | 基础功能完整 |
| 语音功能 | ✅ | 支持语音转文字 |
| 数据同步 | ✅ | HTTP API同步 |
| AI助手 | ✅ | 集成多AI服务 |

## 🔄 更新流程

1. 修改代码
2. 推送到GitHub
3. 自动触发新构建
4. 下载新版APK
5. 覆盖安装

---

💡 **提示**：首次构建可能需要较长时间，后续构建会利用缓存加速。 