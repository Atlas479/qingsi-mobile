# 📋 GitHub Desktop 推送代码指南

## 🎯 目标
使用GitHub Desktop将本地的简化版理清思路代码推送到GitHub，触发APK自动构建。

## 📂 当前项目路径
```
E:\课程\量化投资-自动交易\chart prime\mobile_version
```

## 🔧 操作步骤

### 第一步：添加本地仓库

1. **在GitHub Desktop中点击左上角的"File"菜单**
2. **选择"Add local repository"（添加本地仓库）**
3. **浏览并选择文件夹**：
   ```
   E:\课程\量化投资-自动交易\chart prime\mobile_version
   ```
4. **点击"Add repository"**

### 第二步：检查仓库状态

添加仓库后，您应该能看到：
- **仓库名称**：qingsi-mobile
- **当前分支**：main
- **未推送的提交**：应该显示有待推送的更改

### 第三步：查看待推送的更改

在GitHub Desktop中您应该能看到以下待推送的文件：
- ✅ `buildozer.spec` (简化配置)
- ✅ `main.py` (简化版应用)
- ✅ `.github/workflows/build-apk.yml` (修复的构建配置)
- ✅ `🔧构建问题解决方案.md` (新文档)

### 第四步：推送到GitHub

1. **点击右上角的"Push origin"按钮**
2. **等待推送完成**
   - 如果网络良好，几秒钟就能完成
   - 如果网络不稳定，GitHub Desktop会自动重试

### 第五步：验证推送成功

推送成功后：
1. **GitHub Desktop会显示"Last fetched just now"**
2. **"Push origin"按钮会变灰或消失**
3. **可以点击"View on GitHub"查看在线仓库**

## 🚀 触发构建

推送成功后，GitHub Actions会自动开始构建：

1. **访问构建页面**：
   ```
   https://github.com/Atlas479/qingsi-mobile/actions
   ```

2. **查看最新构建**：
   - 应该会看到新的构建任务
   - 提交信息："大幅简化配置和代码，使用最基本的Kivy应用进行测试构建"

3. **监控构建进度**：
   - 🟡 黄色圆点 = 正在构建中
   - ✅ 绿色勾号 = 构建成功
   - ❌ 红色叉号 = 构建失败

## 📱 预期结果

使用简化配置，预期：
- **构建时间**：8-12分钟
- **成功率**：90%+
- **APK大小**：15-25MB

## 🛠️ 如果遇到问题

### 问题1：GitHub Desktop无法找到仓库
**解决方案**：
- 确保路径正确：`E:\课程\量化投资-自动交易\chart prime\mobile_version`
- 检查该文件夹是否包含`.git`文件夹

### 问题2：推送失败
**解决方案**：
- 检查网络连接
- 在GitHub Desktop中点击"Repository" → "Repository settings" 检查远程URL
- 尝试重新推送

### 问题3：需要登录GitHub
**解决方案**：
- 在GitHub Desktop中点击"File" → "Options" → "Accounts"
- 登录您的GitHub账户

## 🎯 下一步

推送成功后：
1. **监控构建进度**
2. **构建成功后下载APK**
3. **测试应用功能**
4. **逐步恢复完整功能**

---

## 💡 提示

- GitHub Desktop比命令行更稳定，特别适合网络不稳定的情况
- 可以在"History"标签中查看所有提交历史
- 推送前可以在"Changes"标签中预览所有更改 