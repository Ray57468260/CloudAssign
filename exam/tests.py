#!/usr/bin/python3
# -*- coding:utf8 -*-
import docx
import xlrd
import xlwt
import re

"""
题目前后使用{}包装起来；
选项内部请勿使用空格；
"""


def set_style(name, height, bold=False):
    style = xlwt.XFStyle()  # 初始化样式

    font = xlwt.Font()  # 为样式创建字体
    font.name = name
    font.bold = bold
    font.color_index = 4
    font.height = height

    style.font = font
    return style


# 读取模板
template = 'D:/Downloads/uploadFiles-master/media/单选题_批量导入模板.xls'
workbook_temp = xlrd.open_workbook(template)
sheet_temp = workbook_temp.sheet_by_name('Sheet1')
row0 = sheet_temp.row_values(0)
print('模板首行：', row0)

# 创建工作簿
workbook = xlwt.Workbook(encoding='utf-8')
# 创建sheet
data_sheet = workbook.add_sheet('Sheet1')
# 生成第一行
for i in range(len(row0)):
    data_sheet.write(0, i, row0[i], set_style(
        'Microsoft Yahei', 220, False))

file = 'D:/Downloads/uploadFiles-master/media/单选题_预处理题库.docx'
doc = docx.Document(file)
text = ''
for p in doc.paragraphs:
    p.text = re.sub((r'\w+、 *'), ' ', p.text)  # 替换选项标号和题目标号
    p.text = re.sub((r' *（ *） *'), '（）', p.text)  # 替换中文带空格括号
    p.text = re.sub((r' +'), ' ', p.text)  # 替换不间断空格
    p.text = re.sub((r'\t+'), '', p.text)  # 替换水平制表符(tab)
    text = text + ' ' + p.text
es = re.finditer((r"\{(.*?)\}"), text)  # 匹配预处理目标

row = 1
for match in es:
    e = match.group(1).split(' ')
    print('单个试题：', e)
    col = 0
    for i in e:
        if i:
            data_sheet.write(row, col, i, set_style(
                'Microsoft Yahei', 220, False))
            col = col + 1
        else:
            print('none exists')
    row = row + 1

# 保存文件
workbook.save('D:/Downloads/uploadFiles-master/media/单选题_格式化题库.xls')
