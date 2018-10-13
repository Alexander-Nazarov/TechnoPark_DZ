#C:\Users\User\Desktop\Python\log_parse.py

import datetime
import collections
import re
import time
from copy import deepcopy

def get_logs(string):
    if re.fullmatch(r'\[\d\d/\w{3}/\d{4}\s\d\d:\d\d:\d\d\]\s\"\w+\s\S+\s\S+\"\s\d+\s\d+\s', string):
        return string
    return None

def get_data(log):
    start = log.find('http')
    end = log.find(' ', start+1)
    url = log[start: end]
    request_time = log[log.rfind(' '):]
    url = url.replace('https://', '')
    url = url.replace('http://', '')
    pos = url.find('?')
    url = url[0: pos]
    return url, request_time

def is_it_file(log):
    url, time = get_data(get_logs(log))
    start = utl.rfind('.')
    postfix = url[start+1:]
    if postfix.isalpha() and 3 <= len(postfix) <= 4:
            return False
    return True

def request_Type(log):
    start = log.find('\"')
    end = log.find(' ', start+1)
    Type = log[start+1: end]
    return Type

def del_www(log):
    start = log.find('//')
    Www = log[start+2: start+5]
    if Www == 'www':
        new_log = log[: start+2]
        new_log1 = log[start+6:]
        log = deepcopy(new_log + new_log1)
    return log

def what_time(log):
    return  time.strptime(log[:22], "[%d/%b/%Y %H:%M:%S]")

def response_time(log):
    start = log.rfind(' ')
    resp_time = log[start + 1:]
    return resp_time

def average_time(log, LOGS):
    sum_time = 0
    devicer = 0
    url_log, time_log = get_data(get_logs(log))
    for line in LOGS:
        url_line, time_line = get_data(get_logs(line))
        if url_log == url_line:
            sum_time += int(time_line)
            devicer += 1
    return sum_time // devicer

def parse(
    ignore_files=False,
    ignore_urls=[],
    start_at=None,
    stop_at=None,
    request_type=None,
    ignore_www=False,
    slow_queries=False
):
    '''Формирование начального списка логов'''

    LOGS=[]
    buffer = []
    URLs = []
    Top_urls = []
    f = open('C:\\Users\\User\\Desktop\\Python\\GitHub\\TechnoPark_DZ\\log.log.txt')
    LOGS = [get_logs(i) for i in f if get_logs(i) != None]

    '''Игнорирование файлов'''

    if ignore_files:
        for i in LOGS:
            if is_it_file(i):
                buffer.append(i)
        LOGS = deepcopy(buffer)
        buffer.clear()

    '''Игнорирование списка URL'''

    if ignore_urls != []:
        for i in LOGS:
            url, time = get_data(get_logs(i))
            if url in ignore_urls:
                continue
            else:
                buffer.append(i)
        LOGS = deepcopy(buffer)
        buffer.clear()

    '''Начать парсить логи начиная с указанной даты'''

    if start_at != None:
        for i in LOGS:
            if what_time(start_at) > what_time(i):
                continue
            else:
                buffer.append(i)
        LOGS = deepcopy(buffer)
        buffer.clear()
    '''Закончить парсить логи на указанной дате'''

    if stop_at != None:
        for i in LOGS:
            if what_time(stop_at) < what_time(i):
                continue
            else:
                buffer.append(i)
        LOGS = deepcopy(buffer)
        buffer.clear()

    '''Тип запроса, которые надо парсить (остальные игнорируются)'''

    if request_type != None:
        for i in LOGS:
            if request_Type(i) == request_type:
                buffer.append(i)
        LOGS = deepcopy(buffer)
        buffer.clear()

    '''Игнорировать www перед доменом (лог учитывается,
       но отбрасывается www из url лога)'''

    if ignore_www:
        for i in LOGS:
            buffer.append(del_www(i))
        LOGS = deepcopy(buffer)
        buffer.clear()

    '''Преобразование Логов в УРЛы'''

    for i in LOGS:
        url, time = get_data(get_logs(i))
        URLs.append(url)

    '''Подсчёт 5 наиболее часто встречающихся УРЛов'''

    counter = collections.Counter(URLs)
    for elem, count in counter.most_common(5):
        Top_urls.append(count)

    '''Возвращает среднее значение, потраченное на топ 5
       самых медленных запросов к серверу
    '''
    if slow_queries:
        dict = {}
        for i in LOGS:
            url, request_time = get_data(i)
            request_time = request_time
            if url in dict:
                dict[url][0] += 1
                dict[url][1] += int(request_time)
            else:
                dict[url] = [1, int(request_time)]
        list_of_several_time = [int(value[1]) // int(value[0]) for key, value in dict.items()]
        list_of_several_time.sort()
        list_of_several_time.reverse()
        return list_of_several_time[:5]
    else:
        return Top_urls

parse()
