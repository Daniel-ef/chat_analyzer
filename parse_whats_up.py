import json
import pymorphy2
import re
morph = pymorphy2.MorphAnalyzer()

names = '_'.join(sorted(['Даниил Ефимов', 'Принцесса Зоя']))


# Список сообщений
with open('People/Принцесса Зоя.txt', 'r') as f:
    db = re.split('\n', f.read())
text1 = []
for el in db:
    if len(re.findall('\d\d\.\d\d', el)) != 0:
        text1.append(el)
    else:
        text1[len(text1) - 1] += el

# Словарь {день: {юзер: [сообщения]}}
dum = {}
for el in text1:
    date = el[:10]
    if 'Принцесса Зоя' in el:
        user = names.split('_')[1]
    else:
        user = names.split('_')[0]
    text = re.search(': [^$]+$', el).group(0)[2:]
    if date not in dum.keys():
        dum[date] = {user:[text]}
    else:
        if user not in dum[date].keys():
            dum[date][user] = [text]
        else:
            dum[date][user].append(text)

with open('DB/dum_' + names, 'w') as f:
    json.dump(dum, f)

users = names.split('_')

different_words = {}
for user in users:
    different_words[user] = {}

with open('DB/stop_word_dic', 'r') as f:
    stop_words = f.read().split()


for time in dum.keys():
    for user in dum[time].keys():
        for message in dum[time][user]:
            for word in message.split():
                word = re.match('\w+', word)
                if word != None:
                    word = morph.parse(word.group(0))[0].normal_form
                    if word.find('ax') != -1:
                        print(word)
                        word = 'ахаха'
                    if word not in stop_words and word != 'пропустить':
                        different_words[user][word] = int(different_words[user].get(word, 0)) + 1

with open('DB/different_words_' + names, 'w') as f:
    json.dump(different_words, f)
