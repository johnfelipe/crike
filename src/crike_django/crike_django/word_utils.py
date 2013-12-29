# coding:gbk
'''
Created on 2013-12-20

@author: bn
'''

import time
import re
import os
from crike_django.models import Word
from crike_django.settings import MEDIA_ROOT

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
        try:
            content = urlopen(url).read().decode('utf-8', 'ignore')
            break
        except Exception as e:
            attempts += 1
            print(e)

    return content

    
def download_from_iciba(word):
    """Download full size images from Bing image search.
 
    Don't print or republish images without permission.
    I used this to train a learning algorithm.
    """
    BASE_URL = 'http://www.iciba.com/'+word.name
    content = get_content_from_url(BASE_URL)

    phonetics_list = re.findall(
            "\[</strong><strong lang=\"EN-US\" xml:lang=\"EN-US\">(.+?)</strong><strong>\]", content, re.M | re.S)
    print(phonetics_list)
    if len(phonetics_list) > 0:
        word.phonetics =  phonetics_list[0]

    mean_list = []
    mean_span_list = re.findall('<span class=\"label_list\">(.+?)</span>', content, re.M | re.S)
    print mean_span_list
    for mean_span in mean_span_list:
        label_list = re.findall('<label>(.+?)</label>', mean_span, re.M | re.S)
        labels = ''
        for label in label_list:
            labels += label
        mean_list.append(labels)
    print(mean_list)
    word.mean = mean_list

    pos_list = re.findall('<strong class=\"fl\">(.+?)</strong>', content, re.M | re.S)
    print(pos_list)
    word.pos = pos_list

    audio_list = re.findall('asplay\(\'(http://res.iciba.com/resource/amp3.+?\.mp3)\'\)', content, re.M | re.S)
    print audio_list
    download_audio_from_iciba(audio_list[0], word)


def get_data_from_req(req):
    attempts = 0
    binary = ''
    while attempts < 5:
        try:
            binary = urlopen(req)
            time.sleep(1) # be nice to web host
            break
        except Exception as e:
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
        word.audio.put(mp3file.read(), content_type='audio/mp3')
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
    word = Word(name=wordname)
    download_from_iciba(word)
    #download_audio_from_google(word)
    return word

PATH = MEDIA_ROOT + '/audios'
def handle_uploaded_file(words_file):
    if not os.path.exists(PATH):
        os.makedirs(PATH)

    words = words_file.read().split()
    for word in words:#TODO multi-thread
        if word.isalpha() == False:
            continue
        word = word.lower()
        if len(Word.objects(name=word)) == 0:
            download_word(word).save()
            time.sleep(1)

