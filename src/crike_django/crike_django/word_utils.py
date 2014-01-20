# coding:utf-8
'''
Created on 2013-12-20

@author: bn
'''

import time
import re
import os
import threading
from multiprocessing import Process
from crike_django.models import Word, Lesson, Book
from crike_django.settings import MEDIA_ROOT
from string import capitalize
from image_download import download_images

try: 
    input = raw_input
except NameError:
    pass

try:
    import urllib.request
    #import urllib.parse
except ImportError:
    import urllib
    urllib.request = __import__('urllib2')
    urllib.parse = __import__('urlparse')
 
urlopen = urllib.request.urlopen
request = urllib.request.Request

def get_content_from_url(url):
    attempts = 0
    content = ''

    while attempts < 5:
        url_lock.acquire()
        try:
            content = urlopen(url).read().decode('utf-8', 'ignore')
            time.sleep(1)
            url_lock.release()
            break
        except Exception as e:
            attempts += 1
            time.sleep(1)
            url_lock.release()
            print(e)

    return content

def download_from_youdao(word):
    BASE_URL = 'http://dict.youdao.com/search?q='+word.name
    content = get_content_from_url(BASE_URL)

    phonetics_list = re.findall('<span class="phonetic">\[(.+?)\]</span>', content, re.M | re.S)
    if len(phonetics_list) > 0:
        word.phonetics =  phonetics_list[0]

        mean_list = []
        #pos_list = []
        #div_list = re.findall('<div class="trans-container">[\n\t ]*<ul>(.+?)</ul>[\n\t ]*</div>', content, re.M | re.S)
        index = content.find("webTransToggle")
        if index != -1:
            content = content[:index]
        label_list = re.findall('<li>([a-z]+\. .*?)</li>', content, re.M | re.S)
        if len(label_list) > 0:
            label_list = set(label_list)
            for label in label_list:
                if label.find('('+capitalize(word.name)+')') != -1:
                    continue
                mean_list.append(label)
        word.mean = mean_list
        #word.pos = pos_list
                
        word.save()
            
        if not os.path.exists(PATH+word.name+'.mp3'):
            download_audio_from_google(word)


    else:
        print('[youdao] '+word.name+' download failed!')
    
def download_from_iciba(word):
    BASE_URL = 'http://www.iciba.com/'+word.name
    content = get_content_from_url(BASE_URL)
    index = content.find("net_means_label")
    if index != -1:
        content = content[:index]

    phonetics_list = re.findall(
            "\[</strong><strong lang=\"EN-US\" xml:lang=\"EN-US\">(.+?)</strong><strong>\]", content, re.M | re.S)
    if len(phonetics_list) > 0:
        word.phonetics =  phonetics_list[0]

        pos_list = re.findall('<strong class=\"fl\">(.+?)</strong>', content, re.M | re.S)
        #word.pos = pos_list
        pos_list.reverse()

        mean_list = []
        mean_span_list = re.findall('<span class=\"label_list\">(.+?)</span>', content, re.M | re.S)
        for mean_span in mean_span_list:
            label_list = re.findall('<label>(.+?)</label>', mean_span, re.M | re.S)
            labels = ''
            if len(pos_list) > 0:
                labels = pos_list.pop()+' '
            for label in label_list:
                labels += label
            mean_list.append(labels)
        word.mean = mean_list

        word.save()

        if not os.path.exists(PATH+word.name+'.mp3'):
            audio_list = re.findall('asplay\(\'(http://res.+?\.mp3)\'\)', content, re.M | re.S)
            download_audio_from_iciba(audio_list[0], word)
    else:
        print content
        print('[iciba] '+word.name+' download failed!')

def get_data_from_req(req):
    attempts = 0
    binary = ''
    while attempts < 5:
        data_lock.acquire()
        try:
            binary = urlopen(req)
            time.sleep(0.5) # be nice to web host
            data_lock.release()
            break
        except Exception as e:
            time.sleep(0.5) # be nice to web host
            data_lock.release()
            attempts += 1
            print("Attempts: "+str(attempts))
            print(e)
    return binary

def is_file_valid(file):
    try:
        first_char = file.read(1) #get the first character
        if not first_char:
            print "file is empty" #first character is the empty string..
            return False
        else:
            file.seek(0)
            return True
    except Exception as e:
        print(e)
        return False

def download_audio_from_google(word):
    try:
        mp3file = get_data_from_req(
                "https://ssl.gstatic.com/dictionary/static/sounds/de/0/"+word.name+".mp3")
        filepath = os.path.join(PATH, word.name+'.mp3')
        file = open(filepath, 'wb')
        file.write(mp3file.read())
        file.close()
        #word.audio.put(mp3file.read(), content_type='audio/mp3')
    except Exception as e:
        print(e)

def download_audio_from_iciba(url, word):
    try:
        mp3file = get_data_from_req(url)
        print url

        filepath = os.path.join(PATH, word.name+'.mp3')
        file = open(filepath, 'wb')
        file.write(mp3file.read())
        file.close()
        #word.audio.put(mp3file.read(), content_type='audio/mp3')
    except Exception as e:
        print(e)

def download_word(wordname):
    words = Word.objects.filter(name=wordname)
    word = None
    if len(words) > 0:
        word = words[0]
    else:
        word = Word.objects.create(name=wordname)
    print('Start downloading "%s"' % wordname)
    download_from_iciba(word)
    #download_audio_from_google(word)
    word.save()

def download_thread_single_engine(word, engine):
    count = 0

    process = Process(target=engine, args=(word,))
    while not isinstance(process, Process):
        print("Process init failed")
        process = Process(target=engine, args=(word,))
    process.start()
    time.sleep(1)

    while process.is_alive():
        print str(process)+ ' ' + word.name + ' ' + str(count)
        time.sleep(5)
        count += 1
        if count == 10:
            process.terminate()
            break

def get_word_from_queue(words,engine):
    words_lock.acquire()
    wordname = None
    for word in words:
        if len(Word.objects.filter(name=word)) > 0:
           words.remove(word)
           continue
# youdao can't download phrase, iciba can!!!
        if engine == download_from_youdao and word.find(' ') != -1:
           continue
        else:
           words.remove(word)
           wordname = word
           break

    words_lock.release()
    return wordname

class download_thread_with_engine(threading.Thread):
    def __init__(self, words, engine):
        threading.Thread.__init__(self)
        self.words = words
        self.engine = engine

    def run(self):
        wordname = get_word_from_queue(self.words,self.engine)
        while wordname:
            word = Word.objects.create(name=wordname)
            print('Start downloading "%s"' % wordname)
            download_thread_single_engine(word, self.engine)
            wordname = get_word_from_queue(self.words,self.engine)


def install_proxy():
    if use_proxy == False:
        return
    proxy_support = urllib.request.ProxyHandler({"http":http_proxy})
    opener = urllib.request.build_opener(proxy_support)
    urllib.request.install_opener(opener)
    return

PATH = MEDIA_ROOT + '/audios/'
use_proxy = False
http_proxy = "http://localhost:8086"
words_lock = threading.Lock()
url_lock = threading.Lock()
data_lock = threading.Lock()

def handle_uploaded_file(bookname, lessonname, words_file):
    if use_proxy == True:
        install_proxy()

    if not os.path.exists(PATH):
        os.makedirs(PATH)

    lesson = Lesson.objects.create(name=lessonname)
    words = words_file.read().replace('\r','').split('\n')
    if '' in words:
        words.remove('')

    wordsforimage = words[:]
    download_images(wordsforimage)

    tempwords = words[:]

    thread1 = download_thread_with_engine(tempwords, download_from_iciba)
    thread1.start()
    print('Thread 1 started!')
    time.sleep(2)
    thread2 = download_thread_with_engine(tempwords, download_from_youdao)
    thread2.start()
    print('Thread 2 started!')

    thread1.join()
    print('Thread 1 Done!')
    thread2.join()
    print('Thread 2 Done!')

    for word in words:
        if len(Word.objects.filter(name=word)) > 0:
            wordrecord = Word.objects.filter(name=word)[0]
            lesson.words.append(wordrecord.id)

    if len(Book.objects.filter(name=bookname)) == 0:
        book = Book.objects.create(name=bookname)
        book.lessons.append(lesson)
        book.save()
    else:
        book = Book.objects.filter(name=bookname)[0]
        book.lessons.append(lesson)
        book.save()

