from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group, User
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from quiz import models as QMODEL
from teacher import models as TMODEL
from student.models import Student
import random
from random import shuffle

#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')

def student_signup_view(request):
    userForm=forms.StudentUserForm()
    studentForm=forms.StudentForm()
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=forms.StudentUserForm(request.POST)
        studentForm=forms.StudentForm(request.POST,request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            student=studentForm.save(commit=False)
            student.user=user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        return HttpResponseRedirect('studentlogin')
    return render(request,'student/studentsignup.html',context=mydict)

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    students=models.Student.objects.all()
    for i in students:
        if str(i)==str(request.user.first_name):
            id=i.profile_pic
            print(id)

    dict={
    'id':id,
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    }
    return render(request,'student/student_dashboard.html',context=dict)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    coursed=QMODEL.Course.objects.all()
    for i in coursed:
        print(i.__dict__)
    students=models.Student.objects.all()
    for i in students:
        if str(i)==str(request.user.first_name):
            id=i.exam
            courses1=QMODEL.Course.objects.all().filter(course_name=id)
    for i in students:
        if str(i)==str(request.user.first_name):
            id=i.profile_pic
    mdict={'id':id,'courses1':courses1}
    return render(request,'student/student_exam.html',mdict)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    questions=QMODEL.Question.objects.all()
    total_questions=QMODEL.Question.objects.all().filter(course=course).count()
    questions=QMODEL.Question.objects.all().filter(course=course)

    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks
    students=models.Student.objects.all()
    for i in students:
        if str(i)==str(request.user.first_name):
            id=i.profile_pic
    mdict={'id':id,'course':course,'total_questions':total_questions,'total_marks':total_marks}
    return render(request,'student/take_exam.html',mdict)
num=0
def set_order():
    global num
    num=random.randint(1,100)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    questions=QMODEL.Question.objects.all().filter(course=course).order_by('section')
    if course.sequence=='shuffle':
        questions=list(questions)
        print(questions)
        set_order()
        print('..........',num)
        random.Random(num).shuffle(questions)
        print(questions)
    else:
        pass
    if request.method=='POST':
        pass
    students=models.Student.objects.all()
    for i in students:
        if str(i)==str(request.user.first_name):
            id=i.profile_pic
    mdict={'id':id,'course':course,'questions':questions}
    response= render(request,'student/start_exam.html',mdict)
    response.set_cookie('course_id',course.id)
    return response


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):
    if request.COOKIES.get('course_id') is not None:
        course_id = request.COOKIES.get('course_id')
        course=QMODEL.Course.objects.get(id=course_id)
        total_marks=0
        questions=QMODEL.Question.objects.all().filter(course=course)
        if course.sequence=='shuffle':
            questions=list(questions)
            print('>>>>>',num)
            random.Random(num).shuffle(questions)
            for i in range(len(questions)):
            
                selected_ans = request.COOKIES.get(str(i+1))
                print(selected_ans)
                actual_answer = questions[i].answer
                print(actual_answer)
                if selected_ans == actual_answer:
                    total_marks = total_marks + questions[i].marks
        else:
            for i in range(len(questions)):
                selected_ans = request.COOKIES.get(str(i+1))
                actual_answer = questions[i].answer
                if selected_ans == actual_answer:
                    total_marks = total_marks + questions[i].marks

        student = models.Student.objects.get(user_id=request.user.id)
        result = QMODEL.Result()
        result.marks=total_marks
        result.exam=course
        result.student=student
        result.save()

        return HttpResponseRedirect('view-result')



@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    courses=QMODEL.Course.objects.all()
    students=models.Student.objects.all()
    for i in students:
        if str(i)==str(request.user.first_name):
            id=i.exam
            courses=QMODEL.Course.objects.all().filter(course_name=id)
    for i in students:
        if str(i)==str(request.user.first_name):
            id=i.profile_pic
    mdict={'id':id,'courses':courses}
    return render(request,'student/view_result.html',mdict)
    

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    student = models.Student.objects.get(user_id=request.user.id)
    results= QMODEL.Result.objects.all().filter(exam=course).filter(student=student)
    students = models.Student.objects.all()
    for i in students:
        if str(i)==str(request.user.first_name):
            id=i.profile_pic
    mdict={'id':id,'results':results}
    return render(request,'student/check_marks.html',mdict)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    courses=QMODEL.Course.objects.all()
    students=models.Student.objects.all()
    for i in students:
        if str(i)==str(request.user.first_name):
            id=i.exam
            courses=QMODEL.Course.objects.all().filter(course_name=id)
    for i in students:
        if str(i)==str(request.user.first_name):
            id=i.profile_pic
    mdict={'id':id,'courses':courses}      
    return render(request,'student/student_marks.html',mdict)
  