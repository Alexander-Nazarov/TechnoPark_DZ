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

def Is_it_file(log):
    a, b = get_data(get_logs(log))
    start = a.rfind('.')
    postfix = a[start+1:]
    if postfix.isalpha() and 3 <= len(postfix) <= 4:
            return False
    return True

def Request_type(log):
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

def Time(log):
    return  time.strptime(log[:22], "[%d/%b/%Y %H:%M:%S]")

def response_time(log):
    start = log.rfind(' ')
    resp_time = log[start + 1:]
    return resp_time

def average_time(log, LOGS):
    sum_time = 0
    devicer = 0
    a, b = get_data(get_logs(log))
    for line in LOGS:
        c, d = get_data(get_logs(line))
        if a == c:
            sum_time += int(d)
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
    f = open('C:\\Users\\User\\Desktop\\Python\\log.log.txt')
    for i in f:
        if get_logs(i) == None:
            continue
        LOGS.append(get_logs(i))

    '''Игнорирование файлов'''

    if ignore_files:
        for i in LOGS:
            if Is_it_file(i):
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
            if Time(start_at) > Time(i):
                continue
            else:
                buffer.append(i)
        LOGS = deepcopy(buffer)
        buffer.clear()
    '''Закончить парсить логи на указанной дате'''

    if stop_at != None:
        for i in LOGS:
            if Time(stop_at) < Time(i):
                continue
            else:
                buffer.append(i)
        LOGS = deepcopy(buffer)
        buffer.clear()

    '''Тип запроса, которые надо парсить (остальные игнорируются)'''

    if request_type != None:
        for i in LOGS:
            if Request_type(i) == request_type:
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
       (сортирует по убыванию среднего времени) '''

    if slow_queries == True:
        slow_quer = [0] * 5
        slow_logs = [0] * 5
        slow = []
        h = 0
        buffer = deepcopy(LOGS)
        for i in range(5):
            for j in range(1, len(buffer)-h):
                if int(slow_quer[i]) < int(response_time(buffer[j])):
                    slow_quer[i] = int(response_time(buffer[j]))
                    h = j
                    slow_logs[i] = buffer[j]
            buffer.pop(h)

        for i in range(5):
            slow.append(average_time(slow_logs[i], LOGS))
        slow.sort()
        slow.reverse()
        return slow
    else:
        return Top_urls

parse()
