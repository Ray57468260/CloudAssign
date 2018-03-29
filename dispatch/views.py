from django.shortcuts import render, redirect, reverse
from django.core import serializers
from django.views import View
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.forms.models import model_to_dict
from django.db.models import Max, Min, Count, Avg
from guardian.models import UserObjectPermission
from guardian.decorators import *
from .forms import AnswerForm, QuestionForm, CourseForm
from .models import Question, Course, Answer
from users.models import User
import random
import datetime
import json


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


class answer_upload(LoginRequiredMixin, View):

    """
    提交答案，GET方法获取提交答案需填写的表格及自动填写需要的问题信息，POST方法创建答案，同时授予当前用户删除答案的权限
    """

    def get(self, request, courseID, questionID):
        question = Question.objects.select_related(
            'courseID').filter(questionID=questionID)
        answers_query = Answer.objects.filter(
            questionID=questionID, user_id=request.user.user_id).order_by('-created_at')
        if answers_query.exists():
            pass
        else:
            answers_query = False

        form = AnswerForm()
        return render(request, 'dispatch/answer_upload.html', {'question': question, 'answers_query': answers_query, 'form': form})

    def post(self, request, courseID, questionID):
        question = Question.objects.get(questionID=questionID)
        if question.status:
            form = AnswerForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                print(request.POST['questionID'])
                result = {'is_valid': True}
                form.save()
                answer = Answer.objects.select_related(
                    'questionID', 'questionID__courseID', 'questionID__courseID__teacher').latest()
                teacher = answer.questionID.courseID.teacher
                UserObjectPermission.objects.assign_perm(
                    'delete_answer', request.user, obj=answer)
                UserObjectPermission.objects.assign_perm(
                    'change_answer', teacher, obj=answer)
            else:
                print('invalid form')
                result = {'is_valid': False}
                print(form.errors)
            return JsonResponse(result)
        else:
            pass


@login_required
def answer_upload_all(request, courseID, questionID):
    if request.method == 'GET':
        answers = Answer.objects.filter(
            questionID=questionID, user_id=request.user.user_id).order_by('-created_at')
        return render(request, 'dispatch/partials/answers_all.html', {'answers': answers})


class answer_view(LoginRequiredMixin, View):

    def get(self, request):
        courses = Course.objects.filter(
            student=request.user.user_id)
        answers = Answer.objects.select_related('user_id', 'questionID', 'questionID__courseID').filter(
            user_id=request.user.user_id).order_by('questionID')
        if answers.exists():
            return render(request, 'dispatch/answer_view.html', {'answers': answers, 'courses': courses})
        else:
            return render(request, 'dispatch/answer_view.html')

    def post(self, request):
        courseID = request.POST['courseID']
        questions = Question.objects.filter(courseID=courseID)
        questions_json = json.loads(serializers.serialize("json", questions))
        return JsonResponse(questions_json, safe=False)


@login_required
def answer_view_questions(request):
    courseID = request.POST['courseID']
    questions_queryset = Course.objects.get(
        courseID=courseID).Question_courseID.all()
    questions = json.loads(serializers.serialize("json", questions_queryset))
    return JsonResponse(questions, safe=False)


@login_required
def answer_view_retrive_answers(request, questionID):
    answers = Question.objects.get(
        questionID=questionID).Answer_questionID.filter(user_id=request.user.user_id).order_by('-created_at')
    return render(request, 'dispatch/partials/answers_check.html', {'answers': answers})


def answer_query_grade(request):
    questionID = request.POST['questionID']
    answers = Answer.objects.filter(
        questionID=questionID, user_id=request.user.user_id).order_by('-grade')
    if answers.exists():
        best_grade = answers[0]
        result = {'id': best_grade.id, 'subject': best_grade.subject,
                  'created_at': best_grade.created_at, 'grade': best_grade.get_grade_display()}
    else:
        result = {'errors': '未提交答案，或答案尚未批改'}
    return JsonResponse(result)


@permission_required('delete_answer',
                     (Answer, 'pk', 'pk'),
                     accept_global_perms=True, return_403=True, return_404=False)
def answer_delete(request, pk):
    """
    删除答案的POST，仅限提交答案的用户操作，仅允许删除未批改和被驳回的答案
    """
    if request.method == 'POST':
        answer_id = request.POST['pk']
        answer = Answer.objects.get(id=answer_id)
        if answer.status or not answer.accepted:
            answer.delete()
            result = {'result': True}
        else:
            answer.delete()
            result = {'result': True}
        return JsonResponse(result)
    else:
        return HttpResponse('Get')


class question_publish(Auth, LoginRequiredMixin, View):

    """
    发布问题，GET方法获得发布问题需要填写的表单，POST方法发布问题，同时授予该用户的修改及删除的权限
    """

    def get(self, request, courseID):
        form = QuestionForm()
        questions_query = Question.objects.filter(
            courseID=courseID)
        number = questions_query.count()  # 统计当前课程下已发布的问题数，方便创建新问题时进行编号；有bug，因此具体实现还是用随机数
        return render(request, 'dispatch/question_publish.html', {'form': form, 'courseID': courseID, 'questions_query': questions_query, 'number': number})

    def post(self, request, courseID):
        form = QuestionForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            courseID = courseID
            questionID = form.cleaned_data['questionID']
            form.save()
            question = Question.objects.latest()
            UserObjectPermission.objects.assign_perm(
                'change_question', request.user, obj=question)
            UserObjectPermission.objects.assign_perm(
                'delete_question', request.user, obj=question)
            result = {'result': True}
        else:
            print(form.errors)
            result = {'result': False}
        return JsonResponse(result)


class question_review(Auth, LoginRequiredMixin, View):
    """
    问题评分，GET方法返回问题和答案信息，POST方法提交评分
    """

    def get(self, request, courseID, questionID):
        try:
            question = Question.objects.get(questionID=questionID)
            course = Question.objects.get(
                questionID=questionID, courseID=question.courseID.courseID)
            answers = Answer.objects.select_related('user_id').filter(
                questionID=questionID).order_by('created_at')
        except Question.DoesNotExist:
            question = False
        return render(request, 'dispatch/question_review.html', {'course': course, 'question': question, 'answers': answers})

    @method_decorator(permission_required('change_answer',
                                          (Answer, 'pk', 'pk'),
                                          accept_global_perms=True, return_403=True, return_404=False))
    def post(self, request, courseID, questionID, pk):
        answer_id = request.POST['id']
        grade = int(request.POST['grade'])
        suggestions = request.POST['suggestions']
        answer = Answer.objects.get(id=answer_id)
        print(type(grade))
        if grade == 1:
            answer.accepted = False
        else:
            pass
        answer.grade = grade
        answer.suggestions = suggestions
        answer.status = False
        answer.save()
        result = {'result': True, 'id': answer_id}
        return JsonResponse(result)


@permission_required('delete_question',
                     (Question, 'questionID', 'questionID'),
                     accept_global_perms=True, return_403=True, return_404=False)
def question_delete(request, courseID, questionID):
    """
    删除问题，仅允许创建课程的教师
    """
    if request.method == 'POST':
        question = Question.objects.get(questionID=questionID)
        question.delete()
        result = {'redict': 'course/teacher'}
        return JsonResponse(result)


@permission_required('change_question',
                     (Question, 'questionID', 'questionID'),
                     accept_global_perms=True, return_403=True, return_404=False)
def question_close(request, courseID, questionID):
    if request.method == 'POST':
        question = Question.objects.get(questionID=questionID)
        question.status = False
        question.save()
        result = {'result': True}
        return JsonResponse(result)


@permission_required('change_question',
                     (Question, 'questionID', 'questionID'),
                     accept_global_perms=True, return_403=True, return_404=False)
def question_open(request, courseID, questionID):
    if request.method == 'POST':
        question = Question.objects.get(questionID=questionID)
        question.status = True
        question.save()
        result = {'result': True}
        return JsonResponse(result)


@permission_required('change_question',
                     (Question, 'questionID', 'questionID'),
                     accept_global_perms=True, return_403=True, return_404=False)
def question_review_edit(request, courseID, questionID):
    """
    模态窗形式修改问题信息
    """
    if request.method == 'POST':
        quesionID = questionID
        subject = request.POST['subject']
        content = request.POST['content']
        ddl = request.POST['ddl']
        question = Question.objects.get(questionID=quesionID)
        question.subject = subject
        question.content = content
        question.ddl = ddl
        question.save()
        result = {'result': True}
        return JsonResponse(result)


class question_statistics(Auth, LoginRequiredMixin, View):

    def get(self, request, courseID, questionID):
        if request.method == 'GET':
            candidate = []
            question = Question.objects.get(questionID=questionID)
            uploaded = Answer.objects.select_related(
                'user_id').filter(questionID=questionID)

            for a in uploaded:
                candidate.append(a.user_id_id)
            candidate = list(set(candidate))
            uploaded_students = User.objects.filter(user_id__in=candidate)

            undone_students = Course.objects.get(
                courseID=courseID).student.exclude(user_id__in=candidate)

            reviewed = Answer.objects.select_related('user_id').filter(
                questionID=questionID, status=False, accepted=True).order_by('-grade')

            remained = Answer.objects.select_related(
                'user_id').filter(questionID=questionID, status=True)
            rejected = Answer.objects.select_related('user_id').filter(
                questionID=questionID, accepted=False)
            result = {'question': question, 'reviewed': reviewed,
                      'uploaded': uploaded, 'remained': remained, 'rejected': rejected, 'uploaded_students': uploaded_students, 'undone_students': undone_students}
            return render(request, 'dispatch/question_statistics.html', result)

    def post(request, courseID, questionID):
        pass


@is_teacher
def question_statistics_gradedis(request, courseID, questionID):
    if request.method == 'GET':
        result = {}
        grade_map = {
            'C': 55,
            'B': 65,
            'A': 75,
            'A+': 85,
            'A++': 95,
        }  # 请与models.py中Answer类的GRADE_CHOICES同步修改
        for key in grade_map:
            count = Answer.objects.filter(questionID=questionID,
                                          grade=grade_map[key]).aggregate(Count('user_id_id'))
            result[key] = count
            """
        result['avg'] = Answer.objects.filter(
            questionID=questionID, status=False, accepted=True).aggregate(Avg('grade'))
        result['max'] = Answer.objects.filter(
            questionID=questionID, status=False, accepted=True).aggregate(Max('grade'))
        result['min'] = Answer.objects.filter(
            questionID=questionID, status=False, accepted=True).aggregate(Min('grade'))
            """
    return JsonResponse(result, safe=False)


@is_teacher
def question_statistics_timedis(request, courseID, questionID):
    if request.method == 'GET':
        result = {}
        cache = []
        timestamp = list(Answer.objects.filter(
            questionID=questionID).order_by('created_at').values('created_at'))
        for t in timestamp:
            date = t['created_at'].strftime('%x')
            cache.append(date)
            result[date] = cache.count(date)
        return JsonResponse(result)


class course_create(Auth, LoginRequiredMixin, View):
    """
    教师创建课程，GET方法返回创建信息表格，POST方法创建课程，若courseID重复可自行修正
    """

    def get(self, request):
        form = CourseForm()
        return render(request, 'dispatch/course_create.html', {'form': form})

    def post(self, request):
        form = CourseForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            result = {'is_valid': True}
            form.save()
            course = Course.objects.latest()
            UserObjectPermission.objects.assign_perm(
                'change_course', request.user, obj=course)
            UserObjectPermission.objects.assign_perm(
                'delete_course', request.user, obj=course)
            return redirect(reverse("course_teacher"))
        else:
            print(form.errors)
            new_courseID = int(
                request.POST['courseID']) + (random.randint(0, 100))
            course = form.cleaned_data['course']
            intro = form.cleaned_data['intro']
            teacher = form.cleaned_data['teacher']
            new_course = Course(courseID=new_courseID,
                                course=course, intro=intro, teacher=teacher)
            new_course.save()
            course = Course.objects.latest()
            UserObjectPermission.objects.assign_perm(
                'change_course', request.user, obj=course)
            UserObjectPermission.objects.assign_perm(
                'delete_course', request.user, obj=course)
            result = {'is_valid': True}
            return redirect(reverse("course_teacher"))
        result = {'is_valid': form.errors}
        print(form.errors)
        return JsonResponse(result)


class course_edit(Auth, LoginRequiredMixin, View):
    """
    编辑课程模块，GET方法返回已有信息，POST方法更新信息
    """

    def get(self, request, courseID):
        course = Course.objects.filter(courseID=courseID)
        course_json = json.loads(serializers.serialize("json", course))
        return JsonResponse(course_json, safe=False)

    def post(self, request, courseID):
        course = Course.objects.get(courseID=courseID)
        new_course = request.POST['course']
        new_intro = request.POST['intro']
        course.course = new_course
        course.intro = new_intro
        course.save()
        result = {'result': True}
        return JsonResponse(result)


class course_teacher(Auth, LoginRequiredMixin, View):
    """
    教师课程板块，GET方法返回课程信息，POST方法删除课程
    """

    def get(self, request):
        courses = Course.objects.select_related(
            'teacher').filter(teacher=request.user.user_id)
        return render(request, 'dispatch/course_teacher.html', {'courses': courses})

    @method_decorator(permission_required('delete_course',
                                          (Course, 'pk', 'pk'),
                                          accept_global_perms=True, return_403=True, return_404=False))
    def post(self, request, pk):
        courseID = request.POST['pk']
        try:
            course = Course.objects.get(courseID=courseID)
            course.delete()
            result = {'result': True}
        except Course.DoesNotExist:
            result = {'result': False}
        return JsonResponse(result)


def course_teacher_query_questions(request):
    """
    教师课程板块，Ajax查询作业列表
    """
    if request.method == 'POST':
        courseID = request.POST['courseID']
        questions = Question.objects.filter(
            courseID=courseID).order_by('created_at')
        questions_json = json.loads(serializers.serialize(
            "json", questions))
        return JsonResponse(questions_json, safe=False)


class course_info(LoginRequiredMixin, View):
    """
    课程信息展示，学生版是教师版的缩水版
    """

    def get(self, request, courseID):
        course = Course.objects.prefetch_related(
            'student').get(courseID=courseID)
        course_students = course.student.all().order_by('user_id')
        course_students_num = course_students.count()
        questions_query = Question.objects.filter(courseID=courseID)
        if questions_query.exists():
            pass
        else:
            questions_query = False
        return render(request, 'dispatch/course_info.html', {'course': course, 'course_students': course_students, 'course_students_num': course_students_num, 'questions_query': questions_query})

    @method_decorator(permission_required('delete_question',
                                          (Question, 'questionID', 'questionID'),
                                          accept_global_perms=True, return_403=True, return_404=False))
    def post(self, request, courseID, questionID):
        answer = Question.objects.get(questionID=questionID)
        answer.delete()
        result = {'is_valid': True}
        return JsonResponse(result)


class course_subscription(LoginRequiredMixin, View):
    """
    学生课程板块
    """

    def get(self, request):
        my_courses = Course.objects.select_related(
            'teacher').filter(student=request.user.user_id)
        if my_courses.exists():
            pass
        courses_list = Course.objects.all()
        return render(request, 'dispatch/course_student.html', {'my_courses': my_courses, 'courses_list': courses_list})

    def post(self, request):
        courseID = request.POST['courseID']
        course_selec = Course.objects.filter(courseID=courseID)
        if course_selec.exists():
            if Course.objects.filter(student=request.user.user_id, courseID=courseID).exists():
                result = {'result': False}
            else:
                course_selec = Course.objects.get(courseID=courseID)
                course_selec.student.add(request.user.user_id)
                result = {'result': True}
        else:
            result = {'result': 'fatal failure'}
        return JsonResponse(result)


@login_required
def course_desubscription(request):
    """
    学生取消订阅
    """
    if request.method == 'POST':
        courseID = request.POST['courseID']
        course = Course.objects.get(courseID=courseID)
        course.student.remove(request.user.user_id)
        result = {'result': True}
        return JsonResponse(result)


def cache(request):
    return render(request, 'dispatch/cache.html')


@login_required
def query_newquestions(request):
    """
    侧边栏jQuery查询最近7天发布的作业，实现：先查询订阅课程，再查询下属符合截至条件的问题
    """
    if request.method == 'POST':
        # 设置筛选条件
        check_year = datetime.datetime.now().date().year
        check_month = datetime.datetime.now().date().month
        check_day = datetime.datetime.now().date().day - 6
        questions_list = []
        courses = Course.objects.filter(
            student=request.user.user_id)
        if courses.exists():
            for course in courses:
                questions = course.Question_courseID.filter(status=1,
                                                            created_at__year=check_year, created_at__month=check_month, created_at__day__gte=check_day).values('questionID')
                print(questions)
                if questions.exists():
                    for q in questions:
                        questions_list.append(q)
                else:
                    pass
            return JsonResponse(questions_list, safe=False)
        else:
            return JsonResponse(questions_list, safe=False)


@login_required
def retrive_newquestions(request):
    """
    模态窗取回最新七天的作业，实现：根据请求的data中的questionID取出Question实例
    """
    if request.method == 'POST':
        questionID = request.POST['questionID']
        question = Question.objects.select_related(
            'courseID').get(questionID=questionID)
        result = {'courseID': question.courseID.courseID, 'questionID': question.questionID, 'subject': question.subject,
                  'content': question.content, 'ddl': question.ddl, 'created_at': question.created_at}
        return JsonResponse(result)


@login_required
def query_newanswers(request):
    """
    侧边栏jQuery查询最近提交的七个答案，实现：直接查询符合条件的答案
    """
    if request.method == 'POST':
        # 设置筛选条件
        answers = Answer.objects.filter(
            user_id=request.user.user_id).order_by('-created_at')[:7]
        return render(request, 'partials/newanswers_modal.html', {'answers': answers})


@login_required
def query_questions_in_warning(request):
    """
    侧边栏jQuery查询临近截至的作业，实现：先查询订阅课程，再查询下属符合截至条件的问题
    """
    if request.method == 'POST':
        # 设置筛选条件
        check_year = datetime.datetime.now().date().year
        check_month = datetime.datetime.now().date().month
        check_day = datetime.datetime.now().date().day + 1
        questions_list = []
        courses = Course.objects.filter(
            student=request.user.user_id)
        for course in courses:
            questions = course.Question_courseID.filter(status=1,
                                                        ddl__year=check_year, ddl__month=check_month, ddl__day=check_day).values('questionID')
            if questions.exists():
                for q in questions:
                    questions_list.append(q)
            else:
                pass
        return JsonResponse(questions_list, safe=False)


@login_required
def query_questions_unfinished(request):
    """
    侧边栏jquery查询未完成作业，实现：先查询用户已提交的答案，再查询用户订阅的课程下进行中的问题，排除已提交答案的问题即得到未完成的问题
    """
    if request.method == 'POST':
        already_list = []
        closed_list = []
        filter_list = []
        unfinished_list = []
        closed_questions = Question.objects.filter(
            status=False).values('questionID')
        if closed_questions.exists():
            for q in closed_questions:
                closed_list.append(q['questionID'])
        else:
            pass
        already_questions = Answer.objects.filter(
            user_id=request.user.user_id).values('questionID')
        if already_questions.exists():
            for q in already_questions:
                already_list.append(q['questionID'])
            filter_list = list(set(closed_list + already_list))
            courses = Course.objects.filter(
                student=request.user.user_id)
            for course in courses:
                unfinished_questions = course.Question_courseID.exclude(
                    questionID__in=filter_list).values('questionID')
                if unfinished_questions.exists():
                    for q in unfinished_questions:
                        unfinished_list.append(q)
                else:
                    pass
                return JsonResponse(unfinished_list, safe=False)
        else:
            result = {'result': False}
            return JsonResponse(result)


@login_required
def query_questions_rejected(request):
    """
    侧边栏jQuery查询被驳回的答案，实现：直接查询用户被驳回的答案
    """
    if request.method == 'POST':
        rejected_list = []
        answers = Answer.objects.filter(
            user_id=request.user.user_id, accepted=False).values('questionID')
        if answers.exists():
            for a in answers:
                rejected_list.append(a)
        else:
            pass
        return JsonResponse(rejected_list, safe=False)
    result = {'result': False}
    return JsonResponse(result)


@login_required
def retrive_unfinished(request):
    """
    模态窗取回未完成的作业，实现：根据请求的data中的questionID取出Question实例
    """
    if request.method == 'POST':
        questionID = request.POST['questionID']
        question = Question.objects.select_related(
            'courseID').get(questionID=questionID)
        result = {'courseID': question.courseID.courseID, 'questionID': question.questionID, 'subject': question.subject,
                  'content': question.content, 'ddl': question.ddl}
        return JsonResponse(result)


@login_required
def retrive_warning(request):
    """
    模态窗取回临近截至的作业，实现：根据请求的data中的questionID取出Question实例
    """
    if request.method == 'POST':
        questionID = request.POST['questionID']
        question = Question.objects.select_related(
            'courseID').get(questionID=questionID)
        result = {'courseID': question.courseID.courseID, 'questionID': question.questionID, 'subject': question.subject,
                  'content': question.content, 'ddl': question.ddl}
        return JsonResponse(result)


@login_required
def retrive_rejected(request):
    """
    模态窗取回答案被驳回的作业，实现：根据请求的data中的questionID取出Question实例
    """
    if request.method == 'POST':
        questionID = request.POST['questionID']
        question = Question.objects.select_related(
            'courseID').get(questionID=questionID)
        result = {'courseID': question.courseID.courseID, 'questionID': question.questionID, 'subject': question.subject,
                  'content': question.content, 'ddl': question.ddl}
        return JsonResponse(result)


@login_required
def question_review_answers_fresh(request, courseID, questionID):
    if request.method == 'POST':
        order = request.POST['order']
        print(order)

        def case1():
            answers = Answer.objects.prefetch_related('user_id').filter(
                questionID=questionID, status=1).order_by('-created_at')
            return answers

        def case2():
            answers = Answer.objects.prefetch_related('user_id').filter(
                questionID=questionID, status=1).order_by('created_at')
            return answers

        def case3():
            answers = Answer.objects.prefetch_related('user_id').filter(
                questionID=questionID, status=1).order_by('user_id_id')
            return answers

        switch = {
            'time': case1,
            '-time': case2,
            'user_id': case3,
        }

        return render(request, 'dispatch/partials/answers_fresh.html', {'answers': switch[order]})


@login_required
def question_review_answers_reviewed(request, courseID, questionID):
    if request.method == 'POST':
        order = request.POST['order']
        print(order)

        def case1():
            answers = Answer.objects.prefetch_related('user_id').filter(
                questionID=questionID, status=0, accepted=1).order_by('-created_at')
            return answers

        def case2():
            answers = Answer.objects.prefetch_related('user_id').filter(
                questionID=questionID, status=0, accepted=1).order_by('created_at')
            return answers

        def case3():
            answers = Answer.objects.prefetch_related('user_id').filter(
                questionID=questionID, status=0, accepted=1).order_by('user_id_id')
            return answers

        switch = {
            'time': case1,
            '-time': case2,
            'user_id': case3,
        }

        return render(request, 'dispatch/partials/answers_reviewed.html', {'answers': switch[order]})


@login_required
def question_review_answers_rejected(request, courseID, questionID):
    if request.method == 'POST':
        order = request.POST['order']
        print(order)

        def case1():
            answers = Answer.objects.prefetch_related('user_id').filter(
                questionID=questionID, accepted=0).order_by('-created_at')
            return answers

        def case2():
            answers = Answer.objects.prefetch_related('user_id').filter(
                questionID=questionID, accepted=0).order_by('created_at')
            return answers

        def case3():
            answers = Answer.objects.prefetch_related('user_id').filter(
                questionID=questionID, accepted=0).order_by('user_id_id')
            return answers

        switch = {
            'time': case1,
            '-time': case2,
            'user_id': case3,
        }

        return render(request, 'dispatch/partials/answers_rejected.html', {'answers': switch[order]})


def test(request):
    if request.method == 'GET':
        return render(request, 'dispatch/test.html')

    if request.method == 'POST':
        new_id = request.POST['id']
        new_email = request.POST['email']
        new_adress = request.POST['adress']
        result = {'id': new_id, 'email': new_email, 'adress': new_adress}
        return render(request, 'dispatch/test.html', {'result': result})
