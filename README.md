---
### 更新：2019/03/28
重新编写了READ.MD，补充了移植到Linux系统的操作步骤；
修改了exam应用的模块引用逻辑和生成试卷文件的逻辑，增加了对Linux系统的支持；
更新了依赖列表requirements；添加了针对Linux系统的依赖列表requirements4linux；

***
# CloudAssign-网络教学辅助系统

### 创建时间：2018/05/25 
1. 基于Django框架的网络教学辅助系统
- 暨南大学2014届信息工程本科毕业设计项目
- 作者：邓焯锐，联系邮箱：ray57468260@gmail.com

2. 暨南大学石牌校区的师生可通过校内网络访问已部署的系统："http://172.18.59.57:8000"

### 我该怎样克隆该系统到我的机器中
首先需要一个支持Django框架工作的系统环境（Windows10、Ubuntu 12或其他Linux系统）。
按照以下步骤指引配置好你的系统环境，把本系统部署到本地机器中（部署上线需要Nginx与uwsgi，以后补充）

### 移植工作环境：

1. 在新环境中安装python3.6与相应的pip，确认他们已经被添加到系统路径PATH中。

>Windows 10 系统中通过环境变量查看PATH变量，用户变量和系统变量任选一添加即可；

>Linux系统中查看系统路径可使用命令：
>'echo $PATH'


2. 安装虚拟环境包

Windows10系统，重开cmd或powershell后执行命令：
'pip install virtualenv'

Linux系统，在terminal中执行命令：
'pip install virtualenv'

>当系统存在多个版本的pip，上面的命令可能无效，通过指定pip版本可以解决问题
>'pip3 install virtualenv'


3. 创建虚拟环境并激活

---
创建新的虚拟环境：

virtualenv nameofenv

>当系统存在多个版本的python，上面的命令可能生成一个过时Python版本的虚拟环境，这一问题在默认安装python2.7的Ubuntu系统上更加明显。通过指定解释器版本创建与之相符的虚拟环境：
>'virtualenv -p python3.6 nameofenv'
>这里的python3.6是已添加到系统路径中的解释器

---
激活新的虚拟环境

Windows系统：
'.../nameofenv/Scripts/activate'
在cmd或power shell中可直接执行脚本

Linux系统：
'. .../nameofenv/bin/activate'
>注意最前面是一个带空格的dot，表示执行shell脚本

工作目录前出现(nameofenv)表示虚拟环境已激活，这会把虚拟环境中的python解释器和pip临时添加到系统路径的前两行


4. 安装依赖

激活虚拟环境后执行命令：
'pip install -r requirements'

>由于exam应用引入了基于Windows平台的python模块(comtypes、pythoncom)，以上依赖仅使用于Windows10系统；
>Linux系统的依赖文件列表请使用requirements4linux；另外Linux还需安装LibreOffice实现对doc文档的操作：
>'sudo apt-get install libreoffice'



### 安装数据库并配置
1. 安装MySQL5.6版本，设置root密码为2014051903并创建一个名为project01的数据库；这些设置都可以在/CloudAssign/CloudAssign/settings.py中修改

2. 激活虚拟环境，使用以下命令创建系统运行所需数据表：
'python manage.py migrate'

### 运行本地测试服务器

先启动MySQL服务，默认情况下MySQL服务都是开机自启动的；

cmd/terminal执行命令：
'python manage.py runserver'
这会检查文件正确性，检查通过后将在本地创建一个wsgi服务器，通过浏览器输入127.0.0.1:8000可以访问到系统首页。
