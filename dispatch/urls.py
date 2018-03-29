from django.urls import path, re_path
from django.conf.urls import url
from .views import *

urlpatterns = [
    path(r'<int:courseID>/publish/',
         question_publish.as_view(), name='question_publish'),
    path(r'<int:courseID>/<int:questionID>/',
         course_info.as_view(), name='course_info_post'),
    path(r'<int:courseID>/<int:questionID>/statistics/',
         question_statistics.as_view(), name='question_statistics'),
    path(r'<int:courseID>/<int:questionID>/statistics/gradedis/',
         question_statistics_gradedis, name='question_statistics_gradedis'),
    path(r'<int:courseID>/<int:questionID>/statistics/timedis/',
         question_statistics_timedis, name='question_statistics_timedis'),

    path(r'<int:courseID>/<int:questionID>/review/',
         question_review.as_view(), name='question_review_get_answers'),
    path(r'<int:courseID>/<int:questionID>/review/fresh/',
         question_review_answers_fresh, name='question_review_answers_fresh'),
    path(r'<int:courseID>/<int:questionID>/review/reviewed/',
         question_review_answers_reviewed, name='question_review_answers_reviewed'),
    path(r'<int:courseID>/<int:questionID>/review/rejected/',
         question_review_answers_rejected, name='question_review_answers_rejected'),
    path(r'<int:courseID>/<int:questionID>/review/edit/',
         question_review_edit, name='question_review_edit'),
    path(r'<int:courseID>/<int:questionID>/review/<int:pk>/',
         question_review.as_view(), name='question_review_post_review'),
    path(r'<int:courseID>/<int:questionID>/review/delete/',
         question_delete, name='questions_review_delete'),
    path(r'<int:courseID>/<int:questionID>/review/close/',
         question_close, name='questions_review_close'),
    path(r'<int:courseID>/<int:questionID>/review/open/',
         question_open, name='questions_review_open'),

    path(r'<int:courseID>/<int:questionID>/upload/all/',
         answer_upload_all, name='answer_upload_all'),
    path(r'<int:courseID>/<int:questionID>/upload/',
         answer_upload.as_view(), name='answer_upload'),

    path(r'<int:courseID>/edit/',
         course_edit.as_view(), name='course_edit'),
    path(r'<int:courseID>/',
         course_info.as_view(), name='course_info'),

    path(r'student/', course_subscription.as_view(),
         name='course_subscription'),
    path(r'student/desubs/', course_desubscription,
         name='course_desubscription'),
    path(r'student/answer/', answer_view.as_view(), name='answer_view'),
    path(r'student/answer/<int:questionID>/',
         answer_view_retrive_answers, name='answer_view_retrive_answers'),
    path(r'student/answer/questions/', answer_view_questions,
         name='answer_view_questions'),

    path(r'answer/delete/<int:pk>/',
         answer_delete, name='answer-delete'),
    path(r'answer/grade/', answer_query_grade, name='answer_query_grade'),

    path(r'teacher/', course_teacher.as_view(),
         name='course_teacher'),
    path(r'teacher/<int:pk>/', course_teacher.as_view(),
         name='course_teacher_post'),
    path(r'teacher/query/questions/', course_teacher_query_questions,
         name='course_teacher_query_questions'),

    path(r'create/', course_create.as_view(), name='course_create'),

    path(r'query/newquestions/', query_newquestions,
         name='query_newquestions'),
    path(r'query/newanswers/', query_newanswers,
         name='query_newanswers'),
    path(r'query/warning/', query_questions_in_warning,
         name='query_questions_in_warning'),
    path(r'query/unfinished/', query_questions_unfinished,
         name='query_questions_unfinished'),
    path(r'query/rejected/', query_questions_rejected,
         name='query_questions_rejected'),

    path(r'retrive/newquestions/', retrive_newquestions,
         name='retrive_newquestions'),
    path(r'retrive/unfinished/', retrive_unfinished, name='retrive_unfinished'),
    path(r'retrive/warning/', retrive_warning, name='retrive_warning'),
    path(r'retrive/rejected/', retrive_rejected, name='retrive_rejected'),

    path(r'test/', test, name='test'),

]
