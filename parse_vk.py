import json
import re
import pymorphy2
morph = pymorphy2.MorphAnalyzer()


def parse_vk_kate(names, filename):
    # User (data): message
    # Массив сообщений
    with open('People/' + filename, 'r') as f:
        message = f.read().split('\n')
    mas = []

    i = 0
    while i < len(message) - 1:
        if len(re.findall('\w+ \w+ \(\d+', message[i])) != 0:
            mas.append(message[i])
            i += 1
            while message[i] != '' and i < len(message) - 1:

                if message[i].find('Прикрепления') == -1 and message[i].find('  ') != 0 and message[i] != '':
                    mas[len(mas) - 1] += ' ' + message[i]
                    i += 1
                else:
                    i += 1
            else:
                i += 1
        else:
            i += 1

    dum = {}
    users = names.split('_')
    for el in mas:
        if re.match('\w+ \w+', el):
            user = re.match('\w+ \w+', el).group(0)
            date = re.search('\d+ \w+\.? \d+', el)
            if not date:
                pass
            else:
                date = date.group(0)
            message = el[re.search('\([^\)]+\)', el).end()+1:]
            if date not in dum.keys():
                dum[date] = {user: [message]}
            else:
                if user not in dum[date].keys():
                    dum[date][user] = [message]
                else:
                    dum[date][user].append(message)



    with open('DB/dum_' + names, 'w') as f:
        json.dump(dum, f)

    with open('DB/stop_word_dic', 'r') as f:
        stop_words = f.read().split()

    different_words = {}
    for user in users:
        different_words[user] = {}

    for time in dum.keys():
        for user in users:
            if user in dum[time].keys():
                for message in dum[time][user]:
                    for word in message.split():
                        word = re.match('\w+', word)
                        if word:
                            word = morph.parse(word.group(0))[0].normal_form
                            if word not in stop_words:
                                different_words[user][word] = int(different_words[user].get(word, 0)) + 1
    with open('DB/different_words_' + names, 'w') as f:
        json.dump(different_words, f)
