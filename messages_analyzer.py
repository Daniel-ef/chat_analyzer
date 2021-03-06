import json
import time
import re
import requests
import vk_api

import nltk
import pymorphy2
from nltk.corpus import stopwords
from authorisation import authorisate
import numpy

stopwords = set(stopwords.words('russian') + stopwords.words('english') + [''])

morph = pymorphy2.MorphAnalyzer()


class Analyzer:
    def __init__(self):
        with open('db/all_messages', 'r') as f:
            db = json.load(f)
        self.id = str(db['my_id'])
        self.name = db['my_name']
        self.histories = []

        self.vk_session = authorisate()

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

    def get_group_names(self, wall_ids):
        vk = self.vk_session.get_api()
        res = vk.groups.getById(group_ids=','.join(list(map(str, wall_ids))))
        group_names = {}
        for group in res:
            group_names[group['id']] = group['name']

        return group_names


# TODO: слова, присущие только этому человеку
    def statistic(self):
        # Время
        log = str(time.ctime(time.time())) + '\n________________________________________\n\n'
        hah = re.compile('(^ах[иа]*)|(^хах*)')


        # Диалоги в порядке убывания количества сообщений
        self.histories = list(reversed(sorted(self.histories, key=lambda a: len(a['messages']))))

        for history in self.histories[:30]:

            # Словари
            friend = history['name']

            feats = {}
            for feat_name in ['punctuation', 'dif_words', 'dif_words_norm', 'wall']:
                feats[feat_name] = {}
                for owner in [self.name, friend]:
                    feats[feat_name][owner] = {}

            for var_name in ['words_num', 'mess_num', 'words_num_10']:
                feats[var_name] = {}
                for owner in [self.name, friend]:
                    feats[var_name][owner] = 0

            # Прикрепления
            attachments_types = ['photo', 'video', 'audio', 'wall', 'sticker']
            attachments = dict.fromkeys(attachments_types)
            for obj in attachments.keys():
                attachments[obj] = {}
                attachments[obj][self.name] = 0
                attachments[obj][friend] = 0

            for mess in history['messages']:
                owner = self.name if mess['id'] == self.id else friend
                # Мои сообщения
                feats['mess_num'][owner] += 1
                for word in nltk.tokenize.TweetTokenizer().tokenize(mess['message']):
                    # Пунктуация
                    punct = re.sub('\w+', '', word)
                    if punct != '':
                        feats['punctuation'][owner][punct] = feats['punctuation'][owner].get(punct, 0) + 1

                    # Частота слов
                    feats['words_num'][owner] += 1
                    word = re.sub('[(\d|\W)]*', '', word).lower()
                    if word not in stopwords:
                        feats['dif_words'][owner][word] = feats['dif_words'][owner].get(word, 0) + 1
                        if len(word) > 10:
                            feats['words_num_10'][owner] += 1

                if mess['attachment'] and mess['attachment']['type'] in attachments.keys():
                    attachments[mess['attachment']['type']][owner] += 1
                    if mess['attachment']['type'] == 'wall':
                        feats['wall'][owner][mess['attachment']['group_id']] = feats['wall'][owner].get(mess['attachment']['group_id'], 0) + 1


            # Нормализация слов

            for owner in [self.name, friend]:
                for word in feats['dif_words'][owner].keys():
                    norm_word = morph.parse(word)[0].normal_form
                    if hah.search(norm_word):
                        norm_word = 'ахах'
                    feats['dif_words_norm'][owner][norm_word] = feats['dif_words_norm'][owner].get(norm_word, 0) + feats['dif_words'][owner][word]

            log += friend + '\n\n'
            log += 'Number of messages: ' + str(len(history['messages'])) + '\n\n'
            for owner in [self.name, friend]:
                log += owner + ': ' + str(feats['mess_num'][owner]) + '\n'

            log += '\nNumber of words\n\n'
            for owner in [self.name, friend]:
                log += owner + ': ' + str(feats['words_num'][owner]) + '\n'

            log += '\nNumber of different words\n\n'
            for owner in [self.name, friend]:
                log += owner + ': ' + str(len(feats['dif_words_norm'][owner].keys())) + '\n'

            log += '\nNumber of different words more than 10 symbols length\n\n'
            for owner in [self.name, friend]:
                log += owner + ': ' + str(feats['words_num_10'][owner]) + '\n'

            def add_to_log_freq_words(dic, log):
                log = ''
                for item, i in zip(reversed(sorted(dic.items(), key=lambda a: a[1])), range(20)):
                    log += ' '.join(list(map(str, item))) + '\n'
                return log

            log += '\nMost frequent normal words, except stopwords\n\n'
            for owner in [self.name, friend]:
                log += owner + ':\n'
                log += add_to_log_freq_words(feats['dif_words_norm'][owner], log) + '\n'

            log += '\nMost frequent punctuation symbols\n\n'
            for owner in [self.name, friend]:
                log += owner + ':\n'
                log += add_to_log_freq_words(feats['punctuation'][owner], log) + '\n'

            # Прикрепления
            log += '\nAttacments:\n\n'

            for obj in attachments_types:
                log += obj + '\n'
                for owner in [self.name, friend]:
                    log += owner + ' ' + str(attachments[obj][owner]) + '\n'
                log += '\n'

            log += 'Frequent wall\'s reposts\n\n'

            for owner in [self.name, friend]:
                log += owner + '\n'
                groups = []
                for item, i in zip(feats['wall'][owner].items(), range(10)):
                    if item[0] < 0:
                        groups.append(item)

                print(groups)
                if groups != []:
                    groups = numpy.array(list(reversed(sorted(groups, key=lambda a: a[1])))[:10])
                    print(groups)
                    group_names = self.get_group_names([str(el)[1:] for el in list(groups[:, 0])])
                    print(group_names, '\n')
                    for item in groups:
                        log += group_names[abs(item[0])] + ' ' + str(item[1]) + '\n'
                else:
                    log += 'No wall\'s attachments\n'
                log += '\n'

            print('\n\n')

            log += '\n________________________________________________________________________\n\n\n'

        with open('statistic', 'w') as f:
            f.write(log)


if __name__ == '__main__':
    Analyzer()
