@echo off
chcp 65001 >nul
echo 准备上传理清思路手机版到GitHub...
echo.

echo 请按以下步骤操作：
echo.
echo 1. 在GitHub上创建新仓库：
echo    - 访问 https://github.com/new
echo    - 仓库名：qingsi-mobile
echo    - 设为公开仓库（Public）
echo    - 不要初始化README
echo.

echo 2. 复制仓库地址，然后按任意键继续...
pause >nul
echo.

set /p repo_url="请粘贴您的GitHub仓库地址: "
echo.

echo 初始化Git仓库...
git init
if errorlevel 1 (
    echo Git初始化失败，请确保已安装Git
    pause
    exit /b 1
)

echo 添加文件...
git add .
git commit -m "初始提交：理清思路Android版"

echo 连接远程仓库...
git remote add origin %repo_url%

echo 推送代码...
git branch -M main
git push -u origin main

if errorlevel 1 (
    echo.
    echo 推送失败，可能的原因：
    echo    - 仓库地址错误
    echo    - 网络连接问题
    echo    - 需要GitHub认证
    echo.
    pause
    exit /b 1
)

echo.
echo 代码上传成功！
echo.
echo 下一步：
echo    1. 访问您的GitHub仓库
echo    2. 点击 Actions 标签页
echo    3. 等待APK自动构建完成
echo    4. 在Artifacts中下载APK文件
echo.
pause 