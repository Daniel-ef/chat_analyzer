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
        self.histories = list(reversed(sorted(self.histories, key=lambda a: len(a['messages']))))
        for history in self.histories[:20]:
            log += history['name'] + '\n\n'
            log += 'Number of messages: ' + str(len(history['messages'])) + '\n\n'

            # Словари слов
            my_punctuation = {}
            fr_punctuation = {}
            my_dif_words_stop = {}
            fr_dif_words_stop = {}
            my_words_num = 0
            fr_words_num = 0
            my_num_dif_words_10 = fr_num_dif_words_10 = 0
            for mess in history['messages']:
                if mess['id'] == self.my_id:
                    for word in nltk.tokenize.TweetTokenizer().tokenize(mess['message']):
                        punct = re.sub('\w+', '', word)
                        if punct != '':
                            my_punctuation[punct] = my_punctuation.get(punct, 0) + 1

                        my_words_num += 1
                        word = re.sub('[(\d|\W)]*', '', word).lower()
                        if word not in stopwords:
                            my_dif_words_stop[word] = my_dif_words_stop.get(word, 0) + 1
                else:
                    for word in nltk.tokenize.TweetTokenizer().tokenize(mess['message']):
                        punct = re.sub('\w+', '', word)
                        if punct != '':
                            fr_punctuation[punct] = fr_punctuation.get(punct, 0) + 1

                        fr_words_num += 1
                        word = re.sub('[(\d|\W)]*', '', word).lower()
                        if word not in stopwords:
                            fr_dif_words_stop[word] = fr_dif_words_stop.get(word, 0) + 1

            # Нормализация слов
            my_dif_words_norm = {}
            for word in my_dif_words_stop.keys():
                norm_word = morph.parse(word)[0].normal_form
                my_dif_words_norm[norm_word] = my_dif_words_norm.get(norm_word, 0) + my_dif_words_stop[word]

            fr_dif_words_norm = {}
            for word in fr_dif_words_stop.keys():
                norm_word = morph.parse(word)[0].normal_form
                fr_dif_words_norm[norm_word] = fr_dif_words_norm.get(norm_word, 0) + fr_dif_words_stop[word]

            log += 'Number of words\n\n'
            log += self.name + ': ' + str(my_words_num) + '\n'
            log += history['name'] + ': ' + str(fr_words_num) + '\n\n'

            log += 'Number of different words\n\n'
            log += self.name + ': ' + str(len(my_dif_words_norm.keys())) + '\n'
            log += history['name'] + ': ' + str(len(fr_dif_words_norm.keys())) + '\n\n'

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

            log += add_to_log_freq_words(my_punctuation, log)
            log += '\n' + history['name'] +':\n'
            log += add_to_log_freq_words(fr_punctuation, log)

            log += '________________________________________________________________________\n\n\n'

        with open('statistic', 'w') as f:
            f.write(log)


if __name__ == '__main__':
    Analyzer()
