:: 删除之前的 build 和 dist 文件夹，然后重新打包
pyinstaller --clean -y RenamerMain.py
chcp 65001
c:\Users\%username%\AppData\Local\Programs\Python\Python39\Scripts\pyinstaller main.py -w -F -i mm1.ico -n ShaderFragTool

pause

move dist\ShaderFragTool.exe ShaderFragTool.exe