# CloudAssign

1. 一个基于Django框架的网络教学辅助系统
- 暨南大学2014届信息工程本科毕业设计项目
- 作者：邓焯锐，联系邮箱：ray57468260@gmail.com
2.关于项目的依赖库详情，查看requirements.txt

### 移植开发环境的说明：
0.从开发机器中移植虚拟环境
使用以下命令生成依赖集成文件，请先确认已激活虚拟环境：

pip freeze > requirements.txt 

1.在新设备中，使用本文件夹下的Python安装程序安装python3.6和pip。

2.添加python和pip到环境变量的PATH
python的默认安装路径为C:\Users\Administrator\AppData\Local\Programs\Python\Python36；
pip的默认安装路径为C:\Users\Administrator\AppData\Local\Programs\Python\Python36\Scripts；
以上两个路径直接添加到PATH中，不需要再添加python.exe或pip.exe。


2.5手动安装pip步骤
进入https://pypi.python.org/pypi/pip，下载匹配的pip版本（当前文件夹下已有10.0.1版本）
解压下载的文件
然后进入pip-10.0.1解压文件，执行python3 setup.py install,进行安装


3.安装虚拟环境包
重启cmd或powershell后执行如下命令：
pip install virtualenv


4.在新设备上安装依赖：
使用以下命令创建新的虚拟环境：

virtualenv nameofenv

激活新的虚拟环境，然后在虚拟环境中使用以下命令安装所有依赖包（先导航到requirements.txt所在目录）：

pip install -r requirements.txt

5.就此完成开发环境的移植；


移植数据库
1.使用安装器安装MySQL5.6版本，root密码设置为2014051903，创建一个名为project01的库

2.激活虚拟环境，使用以下命令创建表：
python manage.py migrate


