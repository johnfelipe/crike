#coding:utf-8
from django.views.generic import *
from django.http import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

# Imaginary function to handle an uploaded file.
from crike_django.models import *
from crike_django.forms import *
from crike_django.settings import MEDIA_ROOT,STATIC_ROOT
from word_utils import *
from random import sample, randrange

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
    #word = Word.objects(name=name).first()
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

def show_all_words(request):
    template_name='crike_django/words_list.html'

    words = Word.objects.all()
    if len(words) != 0:
        request.encoding = "utf-8"

    return render(request, template_name, {'Words':words})

def show_words(request, book, lesson):
    template_name='crike_django/words_list.html'

    words = []
    for lessonob in Book.objects(name=book)[0].lessons:
        if lessonob.name == lesson:
            words = lessonob.words
    if len(words) != 0:
        request.encoding = "utf-8"

    return render(request, template_name, {'Words':words, 'book':book, 'lesson':lesson})

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
        word = Word.objects(id=id)[0]
        audiofile = MEDIA_ROOT+'/audios/'+word.name+'.mp3'
        if os.path.exists(audiofile):
            os.remove(audiofile)
        word.delete()
        return HttpResponseRedirect("/show_all_words/")

def delete_lesson(request, book, lesson):
    template = 'crike_django/lesson_delete.html'
    params = { 'book':book, 'lesson':lesson }
    return render(request, template, params)

def show_lib(request):
    return render(request, 'crike_django/lib.html', {})

def lesson_show(request, book, lesson):
    template_name='crike_django/lesson_show.html'
    words_list = []
    bookob = Book.objects(name=book).first()
    for lessonobj in bookob.lessons:
        if lessonobj.name == lesson:
            words_list = lessonobj.words

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

    return render(request, template_name,
           {'words':words, 'book':book, 'lesson':lesson})

def lesson_pick(request, book, lesson):
    template_name='crike_django/lesson_pick.html'
    words_list = []
    bookob = Book.objects(name=book).first()
    for lessonobj in bookob.lessons:
        if lessonobj.name == lesson:
            words_list = lessonobj.words

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

    words_list.remove(words[0])
    count = len(words_list)
    if count > 3:
        options = sample(words_list, 3)
    else:
        options = sample(words_list, count)
    options.insert(randrange(len(options)+1), words[0])

    return render(request, template_name,
           {'words':words, 'book':book, 'lesson':lesson, 'options':options})


class LessonView(TemplateView):
    template_name='crike_django/lesson_view.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})

    def post(self, request, *args, **kwargs):
        return HttpResponse("Not implement yet")

# for learning
class BookView(TemplateView):
    template_name='crike_django/book_view.html'

    def get(self, request, book):
        uploadform = UploadFileForm()

        try:
            bookobj = Book.objects(name=book).first()
            request.encoding = "utf-8"
            return render(request, self.template_name,
                {'Book':bookobj, 'Uploadform':uploadform})
        except Exception as e:
            print e
            return HttpResponseRedirect('/index/')#TODO error page

    #功能：上传文件，然后把文件用handle_uploaded_file处理
    def post(self, request, *args, **kwargs):
        if request.POST['extra'] == 'add':
            uploadform = UploadFileForm(request.POST, request.FILES)
            if uploadform.is_valid():
                bookname = request.POST['book']
                lesson = request.POST['lesson']
                if len(Book.objects(name=bookname)) > 0:
                    book = Book.objects(name=bookname).first()
                    for item in book.lessons:
                        if item.name == lesson:
                            return render(request, self.template_name,
                                    {'books':self.books,'Uploadform':uploadform,
                                      'Showform':'uploadform', 'Uploadwarning':'Duplicated Lesson!!'})

                handle_uploaded_file(request.POST['book'],
                        request.POST['lesson'],
                        request.FILES['file'])
                return HttpResponseRedirect('/admin/books/')
            return render(request, self.template_name,
                    {'books':self.books, 'Uploadform':uploadform, 'Showform':'uploadform'})

        elif request.POST['extra'] == 'delete':
            book = request.POST['delbook']
            lessons = request.POST.getlist('dellessons')
            bookob = Book.objects(name=book).first()
            for lesson in lessons:
                for lessonobj in bookob.lessons:
                    if lessonobj.name == lesson:
                        bookob.lessons.remove(lessonobj)
            if len(bookob.lessons) == 0:
                bookob.delete()
            else:
                bookob.save()

        return HttpResponseRedirect("/admin/books/")

# for management
class BooksView(TemplateView):
    template_name='crike_django/books_list.html'
    books = Book.objects.all()

    def get(self, request, *args, **kwargs):
        uploadform = UploadFileForm()

        if len(self.books) != 0:
            request.encoding = "utf-8"

        return render(request, self.template_name,
                {'books':self.books, 'Uploadform':uploadform})

    #功能：上传文件，然后把文件用handle_uploaded_file处理
    def post(self, request, *args, **kwargs):
        if request.POST['extra'] == 'add':
            uploadform = UploadFileForm(request.POST, request.FILES)
            if uploadform.is_valid():
                bookname = request.POST['book']
                lesson = request.POST['lesson']
                if len(Book.objects(name=bookname)) > 0:
                    book = Book.objects(name=bookname).first()
                    for item in book.lessons:
                        if item.name == lesson:
                            return render(request, self.template_name,
                                    {'books':self.books,'Uploadform':uploadform,
                                      'Showform':'uploadform', 'Uploadwarning':'Duplicated Lesson!!'})

                handle_uploaded_file(request.POST['book'],
                        request.POST['lesson'],
                        request.FILES['file'])
                return HttpResponseRedirect('/admin/books/')
            return render(request, self.template_name,
                    {'books':self.books, 'Uploadform':uploadform, 'Showform':'uploadform'})

        elif request.POST['extra'] == 'delete':
            book = request.POST['delbook']
            lessons = request.POST.getlist('dellessons')
            bookob = Book.objects(name=book).first()
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

