import vk_api
import sys


def authorisate():
    print('Please, enter login and password\nLogin: ')
    login = input()
    print('Password: ')
    password = input()

    for count in range(2):
        vk_session = vk_api.VkApi(login, password)
        try:
            vk_session.authorization()
            print('authorizated')
            break
        except vk_api.AuthorizationError as error_msg:
            print('Login or password is invalid.\nPlease, try again!\nLogin: ')
            login = input()
            print('Password: ')
            password = input()
    else:
        print('You used up all attemps. Try later :(')
        sys.exit(1)

    return vk_session
