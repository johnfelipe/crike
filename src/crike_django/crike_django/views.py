#coding:utf-8
from django.views.generic import *
from django.http import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.http import HttpResponseRedirect

# Imaginary function to handle an uploaded file.
from crike_django.models import *
from crike_django.forms import *
from crike_django.settings import MEDIA_ROOT,STATIC_ROOT
from word_utils import *
from random import sample, randrange, choice
import string
import sys

# Utils
def get_or_none(model, **kwargs):
    try:
        return model.objects.filter(**kwargs)
    except model.DoesNotExist:
        return None

# TODO: Upload file的view
# 规定具体的get/post对应事件

class HomeView(TemplateView):
    template_name = 'registration/index.html'

    def get(self, request, *args, **kwargs):
        books = Book.objects.all()
        return render(request, self.template_name, {'books':books})

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

class StudentView(TemplateView):
    template_name = 'crike_django/student_view.html'

    def get(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

class TeacherView(TemplateView):
    template_name = 'crike_django/teacher_view.html'

    def get(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

def hello_crike(request):
    print request
    return HttpResponse("Hello crike!")

def play_audio(request, name):
    #word = Word.objects.filter(name=name)[0]
    #return HttpResponse(word.audio.read(), content_type="audio/mpeg")
    path = MEDIA_ROOT+'/audios/'+name
    if os.path.exists(path):
        file = open(path, 'rb')
        return HttpResponse(file.read(), content_type="audio/mpeg")
    else:
        return HttpResponse(None)

   #def display_image(request, name):
   #    path = STATIC_ROOT+'/images/'+name
   #    if os.path.exists(path):
   #        file = open(path, 'rb')
   #        return HttpResponse(file.read(), content_type='image/jpeg')
   #    else:
   #        return HttpResponse(None)

class WordsAdminView(TemplateView):
    template_name = 'crike_django/words_admin.html'

    def get(self, request, *args, **kwargs):
        words = Word.objects.all()
        if len(words) != 0:
            request.encoding = "utf-8"

        return render(request, self.template_name, {'Words':words})

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

def show_lessons(request, book):#TODO
    template_name='crike_django/lessons_list.html'

    words = Word.objects.all()
    if len(words) != 0:
        request.encoding = "utf-8"

    return render(request, template_name, {'Words':words})

class WordDeleteView(TemplateView):

    def get(self, request, *args, **kwargs):
        id = request.GET['id']
        template = 'crike_django/word_delete.html'
        params = { 'id': id }
        return render(request, template, params)

    def post(self, request, *args, **kwargs):
        id = request.POST['id']
        word = Word.objects.filter(id=id)[0]
        audiofile = MEDIA_ROOT+'/audios/'+word.name+'.mp3'
        if os.path.exists(audiofile):
            os.remove(audiofile)
        word.delete()
        return HttpResponseRedirect("/admin/words/")

def delete_lesson(request, book, lesson):
    template = 'crike_django/lesson_delete.html'
    params = { 'book':book, 'lesson':lesson }
    return render(request, template, params)


# for learning
class LessonShowView(TemplateView):
    template_name='crike_django/lesson_show.html'

    def get(self, request, book, lesson):
        words_list = []
        bookob = Book.objects.filter(name=book)[0]
        for lessonobj in bookob.lessons:
            if lessonobj.name == lesson:
                # https://bitbucket.org/wkornewald/djangotoolbox/pull-request/3/allow-setting-an-actual-object-in-a/diff
                words_list = Word.objects.filter(id__in=lessonobj.words)

        paginator = Paginator(words_list, 1)

        page = request.GET.get('page')
        try:
            words = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            words = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            words = paginator.page(paginator.num_pages)

        return render(request, self.template_name,
               {'words':words, 'book':book, 'lesson':lesson})

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

class LessonPickView(TemplateView):
    template_name='crike_django/lesson_pick.html'

    def get(self, request, book, lesson):
        words_list = []
        bookob = Book.objects.filter(name=book)[0]
        for lessonobj in bookob.lessons:
            if lessonobj.name == lesson:
                words_list = Word.objects.filter(id__in=lessonobj.words)

        paginator = Paginator(words_list, 1)

        page = request.GET.get('page')
        try:
            words = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            words = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            words = paginator.page(paginator.num_pages)

        words_list = filter(lambda x: x.name !=words[0].name, words_list)
        count = len(words_list)
        if count > 3:
            options = sample(words_list, 3)
        else:
            options = sample(words_list, count)

        options.insert(randrange(len(options)+1), words[0])

        return render(request, self.template_name,
                {'words':words, 'book':book, 'lesson':lesson, 'options':options})

    def post(self, request, book, lesson):
        page = request.POST.get('page')
        num = request.POST.get('num')
# TODO put this word into this student's strange list if num > 1, and store the num
        print "nnnnnnnnnnnnnnnn"
        print num
        print "nnnnnnnnnnnnnnnn"
        if page == '0':
            return HttpResponseRedirect('/study/book/'+book+'/lesson/'+lesson+'/show')
        return HttpResponseRedirect('/study/book/'+book+'/lesson/'+lesson+'/pick?page='+page)


class LessonFillView(TemplateView):
    template_name='crike_django/lesson_fill.html'

    def get(self, request, book, lesson):
        words_list = []
        bookob = Book.objects.filter(name=book)[0]
        for lessonobj in bookob.lessons:
            if lessonobj.name == lesson:
                words_list = Word.objects.filter(id__in=lessonobj.words)

        paginator = Paginator(words_list, 1)

        page = request.GET.get('page')
        try:
            words = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            words = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            words = paginator.page(paginator.num_pages)

        options = sys.modules['__builtin__'].list(words[0].name)
        options = sample(options, len(options))
        options.insert(randrange(len(options)+1), choice(string.letters).lower())
        options.insert(randrange(len(options)+1), choice(string.letters).lower())
        options.insert(randrange(len(options)+1), choice(string.letters).lower())

        return render(request, self.template_name,
                {'words':words, 'book':book, 'lesson':lesson, 'options':options})

    def post(self, request, book, lesson):
        page = request.POST.get('page')
        num = request.POST.get('num')
# TODO put this word into this student's strange list if num > 1, and store the num
        print "nnnnnnnnnnnnnnnn"
        print num
        print "nnnnnnnnnnnnnnnn"
        if page == '0':
            return HttpResponseRedirect('/study/book/'+book+'/lesson/'+lesson+'/show')
        return HttpResponseRedirect('/study/book/'+book+'/lesson/'+lesson+'/fill?page='+page)

class LessonDictationView(TemplateView):
    template_name='crike_django/lesson_dictation.html'

    def get(self, request, book, lesson):
        words_list = []
        bookob = Book.objects.filter(name=book)[0]
        for lessonobj in bookob.lessons:
            if lessonobj.name == lesson:
                words_list = Word.objects.filter(id__in=lessonobj.words)

        paginator = Paginator(words_list, 8)

        page = request.GET.get('page')
        try:
            words = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            words = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            words = paginator.page(paginator.num_pages)

        options = []
        for word in words:
            options.append(word)
        options = sample(options, len(options))

        return render(request, self.template_name,
                {'words':words, 'book':book, 'lesson':lesson, 'options':options})

    def post(self, request, book, lesson):
        page = request.POST.get('page')
        num = request.POST.get('num')
# TODO put this word into this student's strange list if num > 1, and store the num
        print "nnnnnnnnnnnnnnnn"
        print num
        print "nnnnnnnnnnnnnnnn"
        if page == '0':
            return HttpResponseRedirect('/study/book/'+book+'/lesson/'+lesson+'/show')
        return HttpResponseRedirect('/study/book/'+book+'/lesson/'+lesson+'/dictation?page='+page)

class BooksStudyView(TemplateView):
    template_name='crike_django/books_study.html'

    def get(self, request):
#TODO only enable the student's available books!!!
        """
        if not book:
            book = Book.objects.first().name;#TODO get this from student infor

        try:
            bookobj = Book.objects.filter(name=book)[0]
            request.encoding = "utf-8"
            return render(request, self.template_name,{'book':bookobj})
        except Exception as e:
            print e
            return HttpResponseRedirect('/error/')#TODO error page
        """
        books = Book.objects.all()
        return render(request, self.template_name, {'books':books})
        

    def post(self, request, *args, **kwargs):
        return HttpResponseRedirect("/study/books/")

class ExamDictationView(TemplateView):
    template_name='crike_django/Exam_dictation.html'

    def get(self, request, book, lessons):
        words_list = []
        bookob = Book.objects.filter(name=book)[0]
        for lessonobj in bookob.lessons:
            if lessonobj.name in lessons:
                words_list.append(Word.objects.filter(id__in=lessonobj.words))

        paginator = Paginator(words_list, 8)

        page = request.GET.get('page')
        try:
            words = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            words = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            words = paginator.page(paginator.num_pages)

        options = []
        for word in words:
            options.append(word)
        options = sample(options, len(options))

        return render(request, self.template_name,
                {'words':words, 'book':book, 'lesson':lesson, 'options':options})

    def post(self, request, book, lesson):
        page = request.POST.get('page')
        num = request.POST.get('num')
# TODO put this word into this student's strange list if num > 1, and store the num
        print "nnnnnnnnnnnnnnnn"
        print num
        print "nnnnnnnnnnnnnnnn"
        if page == '0':
            return HttpResponseRedirect('/study/book/'+book+'/lesson/'+lesson+'/show')
        return HttpResponseRedirect('/study/book/'+book+'/lesson/'+lesson+'/fill?page='+page)

# for management
class LessonAdminView(TemplateView):
    template_name='crike_django/lesson_admin.html'

    def get(self, request, book, lesson):
        words = []
        bookobj = Book.objects.filter(name=book)[0]
        lessonobjs =  filter(lambda x: x.name == lesson, bookobj.lessons)
        words = Word.objects.filter(id__in=lessonobjs[0].words)
        if len(words) != 0:
            request.encoding = "utf-8"

        return render(request, self.template_name,
                {'words':words, 'book':book, 'lesson':lesson})

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

class BooksAdminView(TemplateView):
    template_name='crike_django/books_admin.html'

    def get(self, request, *args, **kwargs):
        books = Book.objects.all()
        uploadform = UploadFileForm()

        if len(books) != 0:
            request.encoding = "utf-8"

        return render(request, self.template_name,
                {'books':books, 'Uploadform':uploadform})

    #功能：上传文件，然后把文件用handle_uploaded_file处理
    def post(self, request, *args, **kwargs):
        books = Book.objects.all()
        if request.POST['extra'] == 'add':
            uploadform = UploadFileForm(request.POST, request.FILES)
            if not uploadform.is_valid():
                return render(request, self.template_name,
                        {'books':books, 'Uploadform':uploadform, 'Showform':'uploadform'})
                
            bookname = request.POST['book']
            lesson = request.POST['lesson']
            if get_or_none(Book, name=bookname):
                book = Book.objects.filter(name=bookname)[0]
                if filter(lambda x: x.name == lesson, book.lessons):
                    return render(request, self.template_name,
                            {'books':books,'Uploadform':uploadform,
                             'Showform':'uploadform', 'Uploadwarning':'Duplicated Lesson!!'})

            handle_uploaded_file(request.POST['book'],
                    request.POST['lesson'],
                    request.FILES['file'])
            return HttpResponseRedirect('/admin/books/')

        elif request.POST['extra'] == 'delete':
            book = request.POST['delbook']
            lessons = request.POST.getlist('dellessons')
            bookob = Book.objects.filter(name=book)[0]
            for lesson in lessons:
                for lessonobj in bookob.lessons:
                    if lessonobj.name == lesson:
                        bookob.lessons.remove(lessonobj)
            if len(bookob.lessons) == 0:
                bookob.delete()
            else:
                bookob.save()

        return HttpResponseRedirect("/admin/books/")

class ExamView(TemplateView):
    template_name='crike_django/exam_view.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

