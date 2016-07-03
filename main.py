import json
import os
import pymorphy2
from Parse_vk_kate import parse_vk_kate

morph = pymorphy2.MorphAnalyzer()
g = open('Analyzer', 'w')

for persone in os.listdir(path='People'):
    g.write(persone[:-4] + '\n\n')
    names = '_'.join(sorted(['Даниил Ефимов', persone[:-4]]))
    if 'dum_' + names not in os.listdir(path='DB') or 'different_words_' + names not in os.listdir(path='DB'):
        parse_vk_kate(names, persone)

    with open('DB/dum_' + names, 'r') as f:
        dum = json.load(f)
    with open('DB/different_words_' + names, 'r') as f:
        different_words = json.load(f)
    users = names.split('_')
    if 'Зоя Симонова' in users:
        users = ['Даниил Ефимов', 'Принцесса Зоя']

    # Количество сообщений в диалоге
    g.write('Количество сообщений:\n')
    for user in users:
        messages = 0
        mess10 = 0
        for day in dum.keys():
            if type(dum.get(day).get(user)) == type([]):
                messages += len(dum[day][user])
        g.write(user + ' ' + str(messages) + '\n')


    # Количество различных слов
    g.writelines('\nРазличных слов:\n')
    for user in different_words.keys():
        g.write(user + '\n')
        g.write(str(len(different_words[user].keys())) + '\n')

    # Количество различных слов длины больше 10

    g.writelines('\nРазличных слов длины больше 10:\n')
    for user in different_words.keys():
        g.write(user + '\n')
        mess = 0
        for word in different_words[user].keys():
            if len(word) >= 10:
                mess += 1
        g.write(str(mess) + '\n')

    # Различные слова
    g.write('\n')
    for user in users:
        g.write(user + '\n\n')
        diff = list(reversed(sorted(different_words[user].items(), key=lambda pair: pair[1])))
        for i in range(20):
            g.write(str(diff[i][1]) + ' ' + str(diff[i][0]) + '\n')
        g.write('\n')

    g.write('____________________________________________________________________________________\n\n')
g.close()
