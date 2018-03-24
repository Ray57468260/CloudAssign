from django.shortcuts import render, redirect, reverse
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.views import View
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from guardian.models import UserObjectPermission
from guardian.decorators import *
from .forms import *
from .models import *
from users.models import User
from dispatch.models import Course
import random
import json
import xlrd
import xlwt
import docx
from docxtpl import DocxTemplate
import re
import pythoncom
from win32com import client
import os


def is_teacher(func):
    """
    教师权限认证函数装饰器
    """
    def auth(request, *args, **kwargs):
        is_teacher = User.objects.get(user_id=request.user.user_id).is_teacher
        if not is_teacher:
            return redirect(reverse("users_login"))
        return func(request, *args, **kwargs)
    return auth


class Auth(View):
    """
    教师权限认证类装饰器
    """

    def dispatch(self, request, *args, **kwargs):
        is_teacher = User.objects.get(user_id=request.user.user_id).is_teacher
        if not is_teacher:
            return redirect(reverse("users_login"))
        return super(Auth, self).dispatch(request, *args, **kwargs)


class LoginRequiredMixin(object):
    """
    登录认证类装饰器
    """

    @method_decorator(login_required(login_url="/accounts/login/"))
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class exam_draft(Auth, LoginRequiredMixin, View):

    def get(self, request, courseID, draft_id):
        courses = Course.objects.filter(teacher=request.user.user_id)
        if draft_id != 0:
            draft = Draft.objects.filter(id=draft_id)
        else:
            draft = Draft.objects.filter(
                courseID=courseID, status=True).order_by('-created_at')[0]
        return render(request, 'exam_build.html', {'courses': courses, 'draft': draft})

    def post(self, request, courseID, draft_id):
        data = request.body.decode('utf-8')
        json_request = json.loads(data)
        form = DraftForm(data=json_request)
        print(json_request)
        if form.is_valid():
            draft = form.save(commit=False)
            e_dict = json_request['dict']
            e_string = json.dumps(e_dict)
            draft.draft_string = e_string
            draft.save()
            result = {'result': draft.id}
        else:
            print(form.errors)
            result = {'result': False}
        return JsonResponse(result)


@is_teacher
def exam_auto_generate(request):
    if request.method == 'POST':

        def pickle_in_random(querysets, length, count):
            this = es[e_type]
            if length > count:
                pickle_list = [random.randint(0, length - 1)
                               for _ in range(count)]
                while len(set(pickle_list)) != count:
                    pickle_list = [random.randint(0, length - 1)
                                   for _ in range(count)]
                for pickle in pickle_list:
                    this[querysets[pickle].id] = querysets[pickle].descri
            else:
                for e in querysets:
                    this[e.id] = e.descri
            return this

        def case1(courseID, e_type, count):
            es[e_type] = {}
            choices = Choice.objects.filter(courseID=courseID, is_single=True)
            es[e_type] = pickle_in_random(choices, choices.count(), count)
            return es[e_type]

        def case2(courseID, e_type, count):
            es[e_type] = {}
            choices = Choice.objects.filter(courseID=courseID, is_single=False)
            es[e_type] = pickle_in_random(choices, choices.count(), count)
            return es[e_type]

        def case3(courseID, e_type, count):
            es[e_type] = {}
            judges = Judge.objects.filter(courseID=courseID)
            es[e_type] = pickle_in_random(judges, judges.count(), count)
            return es[e_type]

        def case4(courseID, e_type, count):
            es[e_type] = {}
            s_answers = S_answer.objects.filter(courseID=courseID)
            es[e_type] = pickle_in_random(s_answers, s_answers.count(), count)
            return es[e_type]

        def case5(courseID, e_type, count):
            es[e_type] = {}
            blanks = Blank.objects.filter(courseID=courseID)
            es[e_type] = pickle_in_random(blanks, blanks.count(), count)
            return es[e_type]

        switch = {
            's-choice': case1,
            'm-choice': case2,
            'judge': case3,
            's-answer': case4,
            'blank': case5,
        }

        data = request.body.decode('utf-8')
        json_request = json.loads(data)
        courseID = json_request['courseID']
        e_dict = json_request['dict']
        es = {}
        for e_type in e_dict:
            count = int(e_dict[e_type])
            es[e_type] = switch[e_type](courseID, e_type, count)
        result = {'result': es}
        return JsonResponse(result)


class exam_build(Auth, LoginRequiredMixin, View):
    """
    POST方法创建试卷对象
    """

    def get(self, request):
        courses = Course.objects.filter(teacher=request.user.user_id)
        return render(request, 'exam_build.html', {'courses': courses})

    def post(self, request):

        def case1(distrib):
            for e_id in distrib:
                point = distrib[e_id]
                obj = Choice.objects.get(id=e_id)
                obj.point = point
                obj.save()
                exam.choices.add(obj)

        def case2(distrib):
            for e_id in distrib:
                point = distrib[e_id]
                obj = Choice.objects.get(id=e_id)
                obj.point = point
                obj.save()
                exam.choices.add(obj)

        def case3(distrib):
            for e_id in distrib:
                point = distrib[e_id]
                obj = Judge.objects.get(id=e_id)
                obj.point = point
                obj.save()
                exam.judges.add(obj)

        def case4(distrib):
            for e_id in distrib:
                point = distrib[e_id]
                obj = S_answer.objects.get(id=e_id)
                obj.point = point
                obj.save()
                exam.s_answers.add(obj)

        def case5(distrib):
            for e_id in distrib:
                point = distrib[e_id]
                obj = Blank.objects.get(id=e_id)
                obj.point = point
                obj.save()
                exam.blanks.add(obj)

        switch = {
            's-choice': case1,
            'm-choice': case2,
            'judge': case3,
            's-answer': case4,
            'blank': case5,
        }

        data = request.body.decode('utf-8')
        json_request = json.loads(data)
        courseID = json_request['courseID']
        course = Course.objects.get(courseID=courseID)
        title = json_request['title']
        intro = json_request['intro']
        e_dict = json_request['dict']
        exam = Exam(courseID=course, title=title, intro=intro)
        exam.save()
        UserObjectPermission.objects.assign_perm(
            'delete_exam', request.user, obj=exam)

        for e_type in e_dict:
            switch[e_type](e_dict[e_type])
        result = {'exam_id': exam.id}
        return JsonResponse(result)


@permission_required('delete_exam',
                     (Exam, 'id', 'id'),
                     accept_global_perms=True, return_403=True, return_404=False)
def exam_delete(request, courseID, id):
    if request.method == 'POST':
        exam_id = request.POST['exam_id']
        exam = Exam.objects.get(id=exam_id)
        exam.delete()
        result = {'result': True}
        return JsonResponse(result)


class exam_manage(Auth, LoginRequiredMixin, View):
    """
    POST方法创建docx试卷
    """

    def get(self, request, courseID):
        exams = Exam.objects.prefetch_related(
            'courseID').filter(courseID=courseID)
        return render(request, 'exam_manage.html', {'exams': exams})

    def post(self, request, courseID):

        def convert_to_pdf(doc):
            """
            docx转pdf
            """
            try:
                pythoncom.CoInitialize()
                word = client.Dispatch("Word.Application")
                new_name = doc.replace(".docx", r".pdf")
                worddoc = word.Documents.Open(doc)
                worddoc.SaveAs(new_name, FileFormat=17)
                worddoc.Close()
                pdf_path = path.replace(".docx", r".pdf")
            except Exception as e:
                print(e)
                pdf_path = False
            finally:
                word.Quit()
                return pdf_path

        def cal_points(querysets):
            try:
                count = querysets.count()
                point = querysets[0].point
                add_up = count * point
                return add_up
            except IndexError:
                pass
        exam_id = request.POST['exam_id']
        exam_format = request.POST['format']
        exam = Exam.objects.get(id=exam_id)

        s_choices = exam.choices.filter(is_single=True).order_by('?')
        m_choices = exam.choices.filter(is_single=False).order_by('?')
        blanks = exam.blanks.all().order_by('?')
        judges = exam.judges.all().order_by('?')
        s_answers = exam.s_answers.all().order_by('?')

        e_points = {
            's_choices': cal_points(s_choices),
            'm_choices': cal_points(m_choices),
            'blanks': cal_points(blanks),
            'judges': cal_points(judges),
            's_answers': cal_points(s_answers),
        }

        context = {
            'exam': exam,
            'e_points': e_points,
            's_choices': s_choices,
            'm_choices': m_choices,
            'blanks': blanks,
            'judges': judges,
            's_answers': s_answers,
        }

        doc = DocxTemplate('media/exam_template.docx')
        doc.render(context)
        path = 'media/user_%s/%s.docx' % (request.user.user_id, exam.title)
        doc.save(path)

        if exam_format == 'docx':
            result = {'title': exam.title, 'path': path}
        elif exam_format == 'pdf':
            new_doc = os.path.abspath(path)
            pdf_path = convert_to_pdf(new_doc)
            result = {'title': exam.title, 'path': pdf_path}
        else:
            result = {'title': '预览试卷', 'context_json': context_json}
        return JsonResponse(result)


@is_teacher
def exam_retrieve(request):
    if request.method == 'GET':

        def case1():
            choices = Choice.objects.filter(id=e_id).values(
                'descri', 'A', 'B', 'C', 'D', 'E', 'F', 'answer')
            return choices

        def case2():
            choices = Choice.objects.filter(id=e_id).values(
                'descri', 'A', 'B', 'C', 'D', 'E', 'F', 'answer')
            return choices

        def case3():
            judges = Judge.objects.filter(id=e_id).values('descri', 'answer')
            return judges

        def case4():
            s_answers = S_answer.objects.filter(
                id=e_id).values('descri', 'answer')
            return s_answers

        def case5():
            blanks = Blank.objects.filter(id=e_id).values(
                'descri', 'blank1', 'blank2', 'blank3', 'blank4', 'blank5')
            return blanks

        switch = {
            's-choice': case1,
            'm-choice': case2,
            'judge': case3,
            's-answer': case4,
            'blank': case5,
        }

        e_type = request.GET['e_type']
        e_id = request.GET['id']
        querysetsV = switch[e_type]()
        print(querysetsV)
        result = json.dumps(list(querysetsV))
        print(result)
        return JsonResponse(result, safe=False)


class bank_manage(Auth, LoginRequiredMixin, View):

    def get(self, request):
        courses = Course.objects.filter(
            teacher=request.user.user_id).values('courseID', 'course')
        return render(request, 'bank_manage.html', {'courses': courses})

    @is_teacher
    def post(delf, request):
        if request.method == 'POST':

            def case1(e_list):
                for e_id in e_list:
                    print(e_id)
                    Choice.objects.filter(id=e_id).delete()
                return True

            def case2(e_list):
                for e_id in e_list:
                    Choice.objects.filter(id=e_id).delete()
                return True

            def case3(e_list):
                for e_id in e_list:
                    Judge.objects.filter(id=e_id).delete()
                return True

            def case4(e_list):
                for e_id in e_list:
                    S_answer.objects.filter(id=e_id).delete()
                return True

            def case5(e_list):
                for e_id in e_list:
                    Blank.objects.filter(id=e_id).delete()
                return True

            switch = {
                's-choice': case1,
                'm-choice': case2,
                'judge': case3,
                's-answer': case4,
                'blank': case5,
            }

            data = request.body.decode('utf-8')
            json_request = json.loads(data)
            e_type = json_request['e_type']
            try:
                e_list = json_request['e_list']
                result = {'result': switch[e_type](e_list)}
            except MultiValueDictKeyError:
                result = {'result': False}
            return JsonResponse(result)


class bank_bulk(Auth, LoginRequiredMixin, View):

    def post(self, request):

        def case1():
            WorkLish = []
            for n in range(1, rows_num):
                row = sheet.row_values(n)
                # 批量写入数据库， 需定制
                WorkLish.append(Choice(courseID=course, is_single=True, descri=row[0], A=row[
                                1], B=row[2], C=row[3], D=row[4], E=row[5], F=row[6], answer=row[7]))
            Choice.objects.bulk_create(WorkLish)
            return {"result": True}

        def case2():
            WorkLish = []
            for n in range(1, rows_num):
                row = sheet.row_values(n)
                # 批量写入数据库， 需定制
                WorkLish.append(Choice(courseID=course, is_single=False, descri=row[0], A=row[
                                1], B=row[2], C=row[3], D=row[4], E=row[5], F=row[6], answer=row[7]))
            Choice.objects.bulk_create(WorkLish)
            return {"result": True}

        def case3():
            WorkLish = []
            for n in range(1, rows_num):
                row = sheet.row_values(n)
                # 批量写入数据库， 需定制
                WorkLish.append(
                    Judge(courseID=course, descri=row[0], answer=row[1]))
            Judge.objects.bulk_create(WorkLish)
            return {"result": True}

        def case4():
            WorkLish = []
            for n in range(1, rows_num):
                row = sheet.row_values(n)
                # 批量写入数据库， 需定制
                WorkLish.append(
                    S_answer(courseID=course, descri=row[0], answer=row[1]))
            S_answer.objects.bulk_create(WorkLish)
            return {"result": True}

        def case5():
            WorkLish = []
            for n in range(1, rows_num):
                row = sheet.row_values(n)
                # 批量写入数据库， 需定制
                WorkLish.append(Blank(courseID=course, descri=row[0], blank1=row[1], blank2=row[
                                2], blank3=row[3], blank4=row[4], blank5=row[5], blank6=row[6]))
            Blank.objects.bulk_create(WorkLish)
            return {"result": True}

        switch = {
            's-choice': case1,
            'm-choice': case2,
            'judge': case3,
            's-answer': case4,
            'blank': case5,
        }

        form = BankProcessForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            try:
                raw_bank = form.save()
                course = Course.objects.get(courseID=raw_bank.courseID)
                # 获取硬盘中的绝对地址
                path = raw_bank.file.path
                print(path)
                # 操作完不需要手动关闭
                excel = xlrd.open_workbook(
                    filename=str(path), encoding_override='utf8')
                # 使用第一张表
                sheet = excel.sheet_by_index(0)
                rows_num = sheet.nrows
                result = switch[form.cleaned_data['e_type']]()
            except xlrd.biffh.XLRDError as e:
                result = {'result': 'Do not support'}
        else:
            result = {'result': 'not valid form'}
            print(form)
        return JsonResponse(result)


@is_teacher
def bank_query(request, template_name='partials/e_candidate.html'):

    if request.method == 'POST':

        def case1(courseID, keyword):
            choices = Choice.objects.filter(
                courseID=courseID, descri__icontains=keyword, is_single=True)
            return choices

        def case2(courseID, keyword):
            choices = Choice.objects.filter(
                courseID=courseID, descri__icontains=keyword, is_single=False)
            return choices

        def case3(courseID, keyword):
            judges = Judge.objects.filter(
                courseID=courseID, descri__icontains=keyword)
            return judges

        def case4(courseID, keyword):
            s_answers = S_answer.objects.filter(
                courseID=courseID, descri__icontains=keyword)
            return s_answers

        def case5(courseID, keyword):
            blanks = Blank.objects.filter(
                courseID=courseID, descri__icontains=keyword)
            return blanks

        switch = {
            's-choice': case1,
            'm-choice': case2,
            'judge': case3,
            's-answer': case4,
            'blank': case5,
        }

        data = request.body.decode('utf-8')
        json_request = json.loads(data)
        courseID = json_request['courseID']
        e_type = json_request['e_type']
        keyword = json_request['keyword']
        items = switch[e_type](courseID, keyword)
        return render(request, template_name, {'items': items, 'e_type': e_type})


@is_teacher
def bank_add(request, e_type):
    """
    添加单条试题
    """
    if request.method == 'GET':
        def case1():
            form = ChoiceForm()
            return form

        def case2():
            form = ChoiceForm()
            return form

        def case3():
            form = JudgeForm()
            return form

        def case4():
            form = S_answerForm()
            return form

        def case5():
            form = BlankForm()
            return form

        switch = {
            's-choice': case1,
            'm-choice': case2,
            'judge': case3,
            's-answer': case4,
            'blank': case5,
        }
        form = switch[e_type]()

        return HttpResponse(str(form))

    if request.method == 'POST':
        def case1():
            form = ChoiceForm(data=request.POST)
            return form

        def case2():
            form = ChoiceForm(data=request.POST)
            return form

        def case3():
            form = JudgeForm(data=request.POST)
            return form

        def case4():
            form = S_answerForm(data=request.POST)
            return form

        def case5():
            form = BlankForm(data=request.POST)
            return form

        switch = {
            's-choice': case1,
            'm-choice': case2,
            'judge': case3,
            's-answer': case4,
            'blank': case5,
        }
        form = switch[e_type]()
        if form.is_valid():
            form.save()
            result = {'result': True}
        else:
            result = {'result': False}
            print(form.errors)
        return JsonResponse(result)


@is_teacher
def bank_edit(request, e_type, e_id):
    """
    编辑单条试题
    """
    if request.method == 'GET':
        def case1(e_id):
            form = ChoiceForm()
            queryset = Choice.objects.get(id=e_id)
            return form, queryset

        def case2(e_id):
            form = ChoiceForm()
            queryset = Choice.objects.get(id=e_id)
            return form, queryset

        def case3(e_id):
            form = JudgeForm()
            queryset = Judge.objects.get(id=e_id)
            return form, queryset

        def case4(e_id):
            form = S_answerForm()
            queryset = S_answer.objects.get(id=e_id)
            return form, queryset

        def case5(e_id):
            form = BlankForm()
            queryset = Blank.objects.get(id=e_id)
            return form, queryset

        switch = {
            's-choice': case1,
            'm-choice': case2,
            'judge': case3,
            's-answer': case4,
            'blank': case5,
        }
        form, queryset = switch[e_type](e_id)
        return render(request, 'partials/one_form_edit.html', {'form': form, 'queryset': queryset})

    if request.method == 'POST':

        def case1(e_id):
            form = ChoiceForm(data=request.POST)
            if form.is_valid():
                choice = Choice.objects.get(id=e_id)
                choice.descri = form.cleaned_data['descri']
                choice.A = form.cleaned_data['A']
                choice.B = form.cleaned_data['B']
                choice.C = form.cleaned_data['C']
                choice.D = form.cleaned_data['D']
                choice.E = form.cleaned_data['E']
                choice.F = form.cleaned_data['F']
                choice.answer = form.cleaned_data['answer']
                choice.save()
                result = {'result': True}
            else:
                result = {'result': False}
                print(form.errors)
            return result

        def case2(e_id):
            form = ChoiceForm(data=request.POST)
            if form.is_valid():
                choice = Choice.objects.get(id=e_id)
                choice.descri = form.cleaned_data['descri']
                choice.A = form.cleaned_data['A']
                choice.B = form.cleaned_data['B']
                choice.C = form.cleaned_data['C']
                choice.D = form.cleaned_data['D']
                choice.E = form.cleaned_data['D']
                choice.F = form.cleaned_data['F']
                choice.answer = form.cleaned_data['answer']
                choice.save()
                print(form)
                result = {'result': True}
            else:
                result = {'result': False}
                print(form.errors)
            return result

        def case3(e_id):
            form = JudgeForm(data=request.POST)
            if form.is_valid():
                judge = Judge.objects.get(id=e_id)
                judge.descri = form.cleaned_data['descri']
                judge.answer = form.cleaned_data['answer']
                print(form.cleaned_data['answer'])
                print(form)
                judge.save()
                result = {'result': True}
            else:
                result = {'result': False}
                print(form.errors)
            return result

        def case4(e_id):
            form = S_answerForm(data=request.POST)
            if form.is_valid():
                s_answer = S_answer.objects.get(id=e_id)
                s_answer.descri = form.cleaned_data['descri']
                s_answer.answer = form.cleaned_data['answer']
                s_answer.save()
                result = {'result': True}
            else:
                result = {'result': False}
                print(form.errors)
            return result

        def case5(e_id):
            form = BlankForm(data=request.POST)
            if form.is_valid():
                blank = Blank.objects.get(id=e_id)
                blank.descri = form.cleaned_data['descri']
                blank.blank1 = form.cleaned_data['blank1']
                blank.blank2 = form.cleaned_data['blank2']
                blank.blank3 = form.cleaned_data['blank3']
                blank.blank4 = form.cleaned_data['blank4']
                blank.blank5 = form.cleaned_data['blank5']
                blank.blank6 = form.cleaned_data['blank6']
                blank.save()
                result = {'result': True}
            else:
                result = {'result': False}
                print(form.errors)
            return result

        switch = {
            's-choice': case1,
            'm-choice': case2,
            'judge': case3,
            's-answer': case4,
            'blank': case5,
        }
        result = switch[e_type](e_id)
        return JsonResponse(result)


@is_teacher
def bank_drop(request):
    if request.method == 'POST':
        courseID = request.POST['courseID']
        try:
            Choice.objects.filter(courseID=courseID).delete()
            Judge.objects.filter(courseID=courseID).delete()
            S_answer.objects.filter(courseID=courseID).delete()
            Blank.objects.filter(courseID=courseID).delete()
            result = {'result': True}
        except:
            result = {'result': False}
        return JsonResponse(result)


@is_teacher
def bank_export(request):

    def case1():
        choices = Choice.objects.filter(
            courseID=courseID, is_single=True).values()
        return choices

    def case2():
        choices = Choice.objects.filter(
            courseID=courseID, is_single=False).values()
        return choices

    def case3():
        judges = Judge.objects.filter(courseID=courseID).values()
        return judges

    def case4():
        s_answers = S_answer.objects.filter(courseID=courseID).values()
        return s_answers

    def case5():
        blanks = Blank.objects.filter(courseID=courseID).values()
        return blanks

    def set_style(name, height, bold=False):
        style = xlwt.XFStyle()  # 初始化样式

        font = xlwt.Font()  # 为样式创建字体
        font.name = name
        font.bold = bold
        font.color_index = 4
        font.height = height

        style.font = font
        return style

    def get_row0(queryset):
        raw_data = queryset
        raw_data.pop('created_at')
        raw_data.pop('courseID_id')
        raw_data.pop('id')
        raw_data.pop('point')
        try:
            raw_data.pop('is_single')
        finally:
            row0 = []
            for key in raw_data:
                row0.append(key)
            return row0

    def clean_raw_data(queryset):
        raw_data = queryset
        raw_data.pop('created_at')
        raw_data.pop('courseID_id')
        raw_data.pop('id')
        raw_data.pop('point')
        try:
            raw_data.pop('is_single')
        finally:
            return raw_data

    def write_excel(e_type, querysets):
        # 创建工作簿
        workbook = xlwt.Workbook(encoding='utf-8')
        # 创建sheet
        data_sheet = workbook.add_sheet('Sheet1')
        row0 = get_row0(querysets[0])
        # 生成第一行
        for i in range(len(row0)):
            data_sheet.write(0, i, row0[i], set_style(
                'Microsoft Yahei', 220, False))

        for n in range(querysets.count()):
            data = clean_raw_data(querysets[n])
            for i in range(len(row0)):
                data_sheet.write(n + 1, i, data[row0[i]], set_style(
                    'Microsoft Yahei', 220, False))
        # 保存文件
        workbook.save('media/user_%s/%s.xls' % (request.user.user_id, e_type))

    def export(e_type, querysets):
        try:
            write_excel(e_type, querysets)
            return True
        except IndexError:
            return False

    if request.method == 'POST':
        result = {}
        courseID = request.POST['courseID']
        switch = {
            's-choice': case1,
            'm-choice': case2,
            'judge': case3,
            's-answer': case4,
            'blank': case5,
        }

        for key in switch:
            querysets = switch[key]()
            result[key] = export(key, querysets)

        return JsonResponse(result)


class extract_from_docx(Auth, LoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'docx_2_xls.html')

    def post(self, request):

        def set_style(name, height, bold=False):
            style = xlwt.XFStyle()  # 初始化样式

            font = xlwt.Font()  # 为样式创建字体
            font.name = name
            font.bold = bold
            font.color_index = 4
            font.height = height

            style.font = font
            return style

        def docx_2_xls(e_type_name, pre_file):
            try:
                # 读取模板
                template = 'media/%s_批量导入模板.xls' % e_type_name
                workbook_temp = xlrd.open_workbook(template)
                sheet_temp = workbook_temp.sheet_by_name('Sheet1')
                row0 = sheet_temp.row_values(0)

                # 创建工作簿
                workbook = xlwt.Workbook(encoding='utf-8')
                # 创建sheet
                data_sheet = workbook.add_sheet('Sheet1')
                # 生成第一行
                for i in range(len(row0)):
                    data_sheet.write(0, i, row0[i], set_style(
                        'Microsoft Yahei', 220, False))

                # 读取docx预处理文件
                doc = docx.Document(pre_file)
                text = ''
                for p in doc.paragraphs:
                    p.text = re.sub((r'[0-9A-Z]+、 *'), ' ',
                                    p.text)  # 替换选项标号和题目标号
                    p.text = re.sub((r' *（ *） *'), '（）', p.text)  # 替换中文带空格括号
                    p.text = re.sub((r' +'), ' ', p.text)  # 替换不间断空格
                    p.text = re.sub((r'\t+'), '', p.text)  # 替换水平制表符(tab)
                    text = text + ' ' + p.text
                es = re.finditer((r"\{(.*?)\}"), text)  # 匹配预处理目标

                # 写入到新的xls模板中
                row = 1
                for match in es:
                    e = match.group(1).split(' ')
                    col = 0
                    for i in e:
                        if i:
                            data_sheet.write(row, col, i, set_style(
                                'Microsoft Yahei', 220, False))
                            col = col + 1
                        else:
                            pass
                    row = row + 1

                # 保存文件
                path = 'media/user_%s/%s_格式化题库.xls' % (
                    request.user.user_id, e_type_name)
                workbook.save(path)
                errors = 'clear'
                return path, errors
            except FileNotFoundError:
                path = ''
                errors = 'wrong filename'
                return path, errors

        form = DocxForm(request.POST, request.FILES)
        if form.is_valid():
            pre_file = request.FILES.get('file')
            e_type_name = pre_file.name.split('.')[0]
            print(e_type_name, pre_file)
            path, errors = docx_2_xls(e_type_name, pre_file)
            result = {'e_type_name': e_type_name,
                      'path': path, 'errors': errors}
            return JsonResponse(result)
