import vk_api
import json
import requests
import sys
import time


class Collect_data():
    def __init__(self):
        print('Please, enter login and password\nLogin: ')
        self.login = input()
        print('Password: ')
        self.password = input()

        for count in range(2):
            self.vk_session = vk_api.VkApi(self.login, self.password)
            try:
                self.vk_session.authorization()
                print('authorizated')
                break
            except vk_api.AuthorizationError as error_msg:
                print('Login or password is invalid.\nPlease, try again!\nLogin: ')
                self.login = input()
                print('Password: ')
                self.password = input()
        else:
            print('You used up all attemps. Try later :(')
            sys.exit(1)

        self.tools = vk_api.VkTools(self.vk_session)
        self.id, self.name = self.get_id_name('')

        # self.collect_user_ids()
        self.collect_messages()

    def get_id_name(self, id):
        if id == '':
            res = self.vk_session.get_api().users.get()[0]
            id = res['id']
        else:
            res = requests.get('http://api.vk.com/method/users.get', {
                'user_ids': id
            }).json()
            if res.get('response'):
                res = res.get('response')[0]
            else:
                print('error')
            id = res['uid']
        name = ''
        if 'first_name' in res.keys():
            name += res['first_name']
        if 'first_name' in res.keys() and 'last_name' in res.keys():
            name += '_'
        if 'last_name' in res.keys():
            name += res['last_name']
        return (id, name)

    def collect_user_ids(self):
        dialogs = self.tools.get_all('messages.getDialogs', 100)

        with open('db/dialogs', 'w') as f:
            json.dump(dialogs, f)

        user_ids = []
        for dialog in dialogs['items']:
            if dialog['message'].get('chat_id') == None:
                user_ids.append(dialog['message']['user_id'])

        print(len(user_ids))

        with open('db/user_ids', 'w') as f:
            json.dump(user_ids, f)

    def collect_messages(self):
        with open('db/user_ids', 'r') as f:
            ids = json.load(f)

        all_messages = {
            'my_id': self.id
            , 'my_name': self.name
            , 'messages': []
            , 'time': time.ctime(time.time())
        }

        num_id = 1
        for id in ids:
            print('-----', num_id)
            num_id += 1
            mess_history = self.tools.get_all('messages.getHistory', 200, {'user_id': id, 'rev': 1})
            obj = {
                'count': mess_history['count']
                , 'user_id': id
                , 'name': self.get_id_name(id)[1]
                , 'history': {
                    self.id: []
                    , id: []
                }
            }

            mess_num = 1
            for mess in mess_history['items']:
                print(mess_num)
                mess_num += 1
                new_attachment = None

                # Добавляем прикрепления
                if 'attachments' in mess.keys():
                    attachment = mess['attachments'][0]
                    type = attachment['type']
                    new_attachment = {'type': type}
                    # Тип прикрепления
                    if type == 'sticker':
                        new_attachment['id'] = attachment[type]['id']
                    elif type == 'wall':
                        if attachment[type]['to_id'] != 0:
                            new_attachment['group_id'] = attachment[type]['to_id']
                            new_attachment['text'] = attachment[type]['text']
                    elif type == 'photo' or type == 'video' or type == 'audio':
                        new_attachment['id'] = attachment[type]['id']

                obj['history'][mess['from_id']].append({'message': mess['body']
                                                        , 'date': mess['date']
                                                        , 'attachment': new_attachment
                                                        })

            all_messages['messages'].append(obj)
            with open('db/all_messages~~', 'w') as f:
                json.dump(all_messages, f)


if __name__ == '__main__':
    Collect_data()
