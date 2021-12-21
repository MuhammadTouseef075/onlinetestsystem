from django.http.response import HttpResponse
from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from quiz import models as QMODEL
from student import models as SMODEL
from quiz import forms as QFORM


#for showing signup/login button for teacher
def teacherclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'teacher/teacherclick.html')

def teacher_signup_view(request):
    userForm=forms.TeacherUserForm()
    teacherForm=forms.TeacherForm()
    mydict={'userForm':userForm,'teacherForm':teacherForm}
    if request.method=='POST':
        userForm=forms.TeacherUserForm(request.POST)
        teacherForm=forms.TeacherForm(request.POST,request.FILES)
        if userForm.is_valid() and teacherForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            teacher=teacherForm.save(commit=False)
            teacher.user=user
            teacher.save()
            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)
        return HttpResponseRedirect('teacherlogin')
    return render(request,'teacher/teachersignup.html',context=mydict)



def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    teachers=models.Teacher.objects.all()
    for i in teachers:
        if i.user_id==request.user.id:
            id=i.profile_pic

        
    dict={
    'id':id,
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    'total_student':SMODEL.Student.objects.all().count()
    }
    return render(request,'teacher/teacher_dashboard.html',context=dict)

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_exam_view(request):
    teachers=models.Teacher.objects.all()
    for i in teachers:
        if i.user_id==request.user.id:
            id=i.profile_pic
    mdict={'id':id}
    return render(request,'teacher/teacher_exam.html',mdict)


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_exam_view(request):
    courseForm=QFORM.CourseForm()
    if request.method=='POST':
        courseForm=QFORM.CourseForm(request.POST)
        if courseForm.is_valid():        
            courseForm.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/teacher/teacher-view-exam')
    teachers=models.Teacher.objects.all()
    for i in teachers:
        if i.user_id==request.user.id:
            id=i.profile_pic
    mdict={'id':id,'courseForm':courseForm}
    return render(request,'teacher/teacher_add_exam.html',mdict)

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_exam_view(request):
    courses = QMODEL.Course.objects.all()
    teachers=models.Teacher.objects.all()
    for i in teachers:
        if i.user_id==request.user.id:
            id=i.profile_pic
    mdict={'id':id,'courses':courses}
    return render(request,'teacher/teacher_view_exam.html',mdict)

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def delete_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect('/teacher/teacher-view-exam')

@login_required(login_url='adminlogin')
def teacher_question_view(request):
    teachers=models.Teacher.objects.all()
    for i in teachers:
        if i.user_id==request.user.id:
            id=i.profile_pic
    mdict={'id':id}
    return render(request,'teacher/teacher_question.html',mdict)

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_question_view(request):

    questionForm=QFORM.QuestionForm()
    course=QMODEL.Course.objects.all()
    if request.method=='POST':
        course=QMODEL.Course.objects.get(id=request.POST.get('courseID'))
        questions=QMODEL.Question.objects.all().filter(course=course)
        current_marks=request.POST.get('marks')
        total_marks=0
        for i in questions:
            total_marks=total_marks + i.marks
        total_questions=QMODEL.Question.objects.all().filter(course=course).count()
        if total_questions<course.question_number and total_marks+int(current_marks)<=course.total_marks:
            questionForm=QFORM.QuestionForm(request.POST)
            if questionForm.is_valid():
                question=questionForm.save(commit=False)
                course=QMODEL.Course.objects.get(id=request.POST.get('courseID'))
                question.course=course
                question.save() 
            else:
                return HttpResponse("questions or marks exceeded")     
        else:
            return HttpResponse("questions or marks exceeded")
        return HttpResponseRedirect('/teacher/teacher-view-question')
    teachers=models.Teacher.objects.all()
    for i in teachers:
        if i.user_id==request.user.id:
            id=i.profile_pic
    mdict={'id':id,'questionForm':questionForm}
    return render(request,'teacher/teacher_add_question.html',mdict)

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_question_view(request):
    courses= QMODEL.Course.objects.all()
    teachers=models.Teacher.objects.all()
    for i in teachers:
        if i.user_id==request.user.id:
            id=i.profile_pic
    mdict={'id':id,'courses':courses}
    return render(request,'teacher/teacher_view_question.html',mdict)

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def see_question_view(request,pk):
    questions=QMODEL.Question.objects.all().filter(course_id=pk)
    teachers=models.Teacher.objects.all()
    for i in teachers:
        if i.user_id==request.user.id:
            id=i.profile_pic
    mdict={'id':id,'questions':questions}
    return render(request,'teacher/see_question.html',mdict)

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def remove_question_view(request,pk):
    question=QMODEL.Question.objects.get(id=pk)
    question.delete()
    return HttpResponseRedirect('/teacher/teacher-view-question')
