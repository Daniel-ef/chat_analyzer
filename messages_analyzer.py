import json
import time
import re

import nltk
import pymorphy2
from nltk.corpus import stopwords

stopwords = set(stopwords.words('russian') + stopwords.words('english') + [''])

morph = pymorphy2.MorphAnalyzer()


class Analyzer:
    def __init__(self):
        with open('db/all_messages', 'r') as f:
            db = json.load(f)
        self.my_id = str(db['my_id'])
        self.name = db['my_name']
        self.histories = []

        self.make_mas(db['messages'])
        self.statistic()

    def make_mas(self, history):
        for messages in history:
            mess_vec = []
            for key_id in messages['history'].keys():
                for mess in messages['history'][key_id]:
                    mess['id'] = key_id
                    mess_vec.append(mess)
            mess_vec.sort(key=lambda a: int(a['date']))
            self.histories.append({'name': messages['name'], 'messages': mess_vec})

    def statistic(self):
        # Время
        log = str(time.ctime(time.time())) + '\n________________________________________\n\n'

        # Диалоги в порядке убывания количества сообщений
        self.histories = list(reversed(sorted(self.histories, key=lambda a: len(a['messages']))))

        for history in self.histories[:20]:

            # Словари
            punctuation_my = {}
            punctuation_fr = {}

            dif_words_stop_my = {}
            dif_words_stop_fr = {}

            walls_my = {}
            walls_fr = {}

            # Переменные
            words_num_my = 0
            words_num_fr = 0
            mess_num_my = 0
            mess_num_fr = 0
            words_num_10_my = 0
            words_num_10_fr = 0

            attachments_types = ['photo', 'video', 'audio', 'wall', 'sticker']
            attachments = dict.fromkeys(attachments_types)
            for obj in attachments.keys():
                attachments[obj] = {}
                attachments[obj][self.name] = 0
                attachments[obj][history['name']] = 0

            for mess in history['messages']:
                # Мои сообщения
                if mess['id'] == self.my_id:
                    mess_num_my += 1
                    for word in nltk.tokenize.TweetTokenizer().tokenize(mess['message']):
                        # Пунктуация
                        punct = re.sub('\w+', '', word)
                        if punct != '':
                            punctuation_my[punct] = punctuation_my.get(punct, 0) + 1

                        # Частота слов
                        words_num_my += 1
                        word = re.sub('[(\d|\W)]*', '', word).lower()
                        if word not in stopwords:
                            dif_words_stop_my[word] = dif_words_stop_my.get(word, 0) + 1
                            if len(word) > 10:
                                words_num_10_my += 1

                    if mess['attachment'] and mess['attachment']['type'] in attachments.keys():
                        attachments[mess['attachment']['type']][self.name] += 1
                        if mess['attachment']['type'] == 'wall':
                            walls_my[mess['attachment']['from_id']] = walls_my.get(mess['attachment']['from_id'], 0) + 1


                # Сообщения друга
                else:
                    mess_num_fr += 1
                    for word in nltk.tokenize.TweetTokenizer().tokenize(mess['message']):
                        # Пунктуация
                        punct = re.sub('\w+', '', word)
                        if punct != '':
                            punctuation_fr[punct] = punctuation_fr.get(punct, 0) + 1

                        # Частота слов
                        words_num_fr += 1
                        word = re.sub('[(\d|\W)]*', '', word).lower()
                        if word not in stopwords:
                            dif_words_stop_fr[word] = dif_words_stop_fr.get(word, 0) + 1
                            if len(word) > 10:
                                words_num_10_fr += 1
                    if mess['attachment'] and mess['attachment']['type'] in attachments.keys():
                        attachments[mess['attachment']['type']][history['name']] += 1
                        if mess['attachment']['type'] == 'wall':
                            walls_fr[mess['attachment']['from_id']] = walls_fr.get(mess['attachment']['from_id'], 0) + 1

            # Нормализация слов
            my_dif_words_norm = {}
            for word in dif_words_stop_my.keys():
                norm_word = morph.parse(word)[0].normal_form
                my_dif_words_norm[norm_word] = my_dif_words_norm.get(norm_word, 0) + dif_words_stop_my[word]

            fr_dif_words_norm = {}
            for word in dif_words_stop_fr.keys():
                norm_word = morph.parse(word)[0].normal_form
                fr_dif_words_norm[norm_word] = fr_dif_words_norm.get(norm_word, 0) + dif_words_stop_fr[word]

            log += history['name'] + '\n\n'
            log += 'Number of messages: ' + str(len(history['messages'])) + '\n\n'
            log += self.name + ': ' + str(mess_num_my) + '\n'
            log += history['name'] + ': ' + str(mess_num_fr) + '\n\n'

            log += 'Number of words\n\n'
            log += self.name + ': ' + str(words_num_my) + '\n'
            log += history['name'] + ': ' + str(words_num_fr) + '\n\n'

            log += 'Number of different words\n\n'
            log += self.name + ': ' + str(len(my_dif_words_norm.keys())) + '\n'
            log += history['name'] + ': ' + str(len(fr_dif_words_norm.keys())) + '\n\n'

            log += 'Number of different words more than 10 symbols length\n\n'
            log += self.name + ': ' + str(words_num_10_my) + '\n'
            log += history['name'] + ': ' + str(words_num_10_fr) + '\n\n'

            def add_to_log_freq_words(dic, log):
                log = ''
                for item, i in zip(reversed(sorted(dic.items(), key=lambda a: a[1])), range(20)):
                    log += ' '.join(list(map(str, item))) + '\n'
                return log

            log += '\nMost frequent normal words, except stopwords\n\n'
            log += self.name + ':\n'

            log += add_to_log_freq_words(my_dif_words_norm, log)
            log += '\n' + history['name'] +':\n'
            log += add_to_log_freq_words(fr_dif_words_norm, log)

            log += '\n\nMost frequent punctuation symbols\n\n'
            log += self.name + ':\n'

            log += add_to_log_freq_words(punctuation_my, log)
            log += '\n' + history['name'] +':\n'
            log += add_to_log_freq_words(punctuation_fr, log)

            # Прикрепления
            log += '\nAttacments:\n\n'

            for obj in attachments_types:
                log += obj + '\n'
                for owner in [self.name, history['name']]:
                    log += owner + ' ' + str(attachments[obj][owner]) + '\n'
                log += '\n'

            log += 'Frequent wall\'s reposts\n\n'

            log += self.name + '\n'
            for item in sorted(walls_my.items(), key=lambda a: a[1])[:10]:
                log += str(item[0]) + ' ' + str(item[1]) + '\n'

            log += '\n' + history['name'] + '\n'
            for item in sorted(walls_fr.items(), key=lambda a: a[1])[:10]:
                log += str(item[0]) + ' ' + str(item[1]) + '\n'

            log += '________________________________________________________________________\n\n\n'

        with open('statistic', 'w') as f:
            f.write(log)


if __name__ == '__main__':
    Analyzer()
