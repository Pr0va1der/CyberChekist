import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from random import randint
from time import sleep
from pyowm import OWM

token = '408b25eb64e05c943c7f1e72b436be1521939d42af140179ca4b23b4f0bef3738ed196c343b23c1ec0d6e'


def vk_auth():
    print('function vk_auth')
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    return vk


def send_vk(text, chat_id, is_alert=0):
    print('function send_vk')
    vk = vk_auth()
    vk.messages.send(chat_id=chat_id, message=text, random_id=0, disable_mentions=is_alert,
                     peer_id=2000000000 + int(chat_id))


def read_file(file_name):
    print('function read_file')
    with open(file_name, 'r', encoding='UTF-8') as file:
        list = file.read().splitlines()
        return list


def kick_member(user_id, chat_id, messages=None):
    print('function kick_member')
    vk = vk_auth()
    if messages:
        send_vk(messages, chat_id)
    vk.messages.removeChatUser(chat_id=chat_id, member_id=user_id)


# Проверка пользователя на ересь в подписках
def check_user(user, chat_id):
    if user != -197440489:
        print('function check_user')
        vk = vk_auth()
        groups = read_file('bad_groups.txt')
        if user in read_file('white_list.txt'):
            return False
        for group in groups:
            is_member = vk.groups.isMember(group_id=group, user_id=user)
            if is_member:
                messages = 'Обнаружена ересь! Нейтрализация еретика...'
                kick_member(user, chat_id, messages)
                messages = 'Еретик нейтрализован'
                send_vk(messages, chat_id)
                break
        if chat_id == 8:
            messages = 'Аве, Легионер. В нашей беседе действует режим радиомолчания - писать могут только офицеры'
        else:
            messages = 'Добро пожаловать в наш Легион. Правила в закрепе, а мои команды - /помощь'
        send_vk(messages, chat_id)


def can_kick(list, user_id, user_kick, chat_id):
    print('function can_kick')
    is_admin = None
    is_kick = None
    for user in list['items']:
        member_id = user['member_id']
        if user_id == member_id and 'is_admin' in user:
            is_admin = True
        elif user_id == member_id and not 'is_admin' in user:
            messages = 'Вы не администратор'
            send_vk(messages, chat_id)

        if user_kick == member_id and 'can_kick' in user:
            is_kick = True
        elif user_kick * (-1) == member_id and 'can_kick' in user:
            is_kick = True
        elif user_kick == member_id or user_kick * (-1) == member_id:
            messages = 'Этого пользователя невозможно исключить'
            send_vk(messages, chat_id)

    if is_admin and is_kick:
        return True
    else:
        return False


def user_in_list(user_list, user):
    print('function user_in_list')
    flag = False
    for i in range(len(user_list['profiles'])):
        if user == user_list['profiles'][i]['id']:
            flag = True
            break
        else:
            flag = False
    return flag


def command_help(chat_id):
    print('function command_help')
    with open('help_commands.txt', 'r', encoding='UTF-8') as file:
        messages = file.read()
        send_vk(messages, chat_id)


def command_online(peer_id, group_id, chat_id):
    print('function command_online')
    vk = vk_auth()
    users_list = vk.messages.getConversationMembers(peer_id=peer_id, group_id=group_id)
    online_users = 'Список пользователей в сети:\n'
    for user in users_list['profiles']:
        if user['online']:
            if user['online_info']['is_mobile']:
                online_status = 'через телефон\n'
                device_status = '📱'
            else:
                online_status = 'через сайт\n'
                device_status = '🖥'
            online_users += f'•{device_status}[{user["screen_name"]}|{user["first_name"]}' \
                            f' {user["last_name"]}] {online_status}'
    send_vk(online_users, chat_id, is_alert=1)


def command_flip(chat_id):
    print('function command_flip')
    if randint(0, 1):
        random_flip = 'Орел'
    else:
        random_flip = 'Решка'

    messages = f'Тебе выпало: {random_flip}'
    send_vk(messages, chat_id)


def command_roll(text, chat_id):
    print('function command_roll')
    split_text = text.lower().split()
    if len(split_text) > 1:
        if split_text[1].isdigit():
            if int(text.lower().split()[1]) < 1000:
                messages = f'Случайное число: {randint(1, int(split_text[1]))}'
                send_vk(messages, chat_id)
            else:
                messages = 'Слишком большое число. Повторите попытку'
                send_vk(messages, chat_id)
        else:
            messages = 'Вы ввели неверное число. Повторите попытку'
            send_vk(messages, chat_id)
    else:
        messages = 'Вы не ввели число. Повторите попытку'
        send_vk(messages, chat_id)


def command_who(peer_id, group_id, chat_id):
    print('function command_who')
    vk = vk_auth()
    users_list = vk.messages.getConversationMembers(peer_id=peer_id, group_id=group_id)
    users = users_list['profiles']
    who_number = randint(1, len(users)) - 1
    user = f'[{users[who_number]["screen_name"]}|{users[who_number]["first_name"]} {users[who_number]["last_name"]}]'
    messages = f'Это {user}'
    send_vk(messages, chat_id, is_alert=1)


def command_kick(text, peer_id, group_id, from_id, chat_id):
    print('function command_kick')
    vk = vk_auth()
    split_text = text.lower().split()
    if len(split_text) > 1:
        if split_text[1].split('/')[0] == 'https:' and \
                split_text[1].split('/')[2] == 'vk.com':
            users_list = vk.messages.getConversationMembers(peer_id=peer_id, group_id=group_id)
            user_nick = split_text[1].split('/')[3]
            user_id = vk.utils.resolveScreenName(screen_name=user_nick)['object_id']
            if user_in_list(users_list, user_id):
                if can_kick(users_list, from_id, user_id, chat_id):
                    vk.messages.removeChatUser(chat_id=chat_id, member_id=user_id)
            else:
                messages = 'Пользователь не участник беседы'
                send_vk(messages, chat_id)
        else:
            messages = 'Неверная ссылка. Повторите попытку'
            send_vk(messages, chat_id)
    else:
        messages = 'Вы не ввели ссылку. Повторите попытку'
        send_vk(messages, chat_id)

def weather_status_translate(status_eng):
    print('function weather_status_translate')
    if status_eng == 'Rain':
        status_ru = 'дождь'
    elif status_eng == 'Snow':
        status_ru = 'снег'
    elif status_eng == 'Clouds':
        status_ru = 'облачно'
    elif status_eng == 'Clear':
        status_ru = 'ясно'
    else:
        return status_eng
    return status_ru


def command_weather(city, chat_id):
    print('function command_weather')
    owm = OWM('81f11d7784f6974ebe8a826caea14b42')
    try:
        weather = owm.weather_manager().weather_at_place(name=city).weather
    except:
        messages = 'Неверный город. Повторите попытку'
        send_vk(messages, chat_id)
        return
    temperature = int(weather.temp['temp'] - 272)
    status = weather_status_translate(weather.status)
    messages = f'Погода в {city.title()}:\n' \
               f'Сейчас: {temperature}°C, {status}' \
               f''
    send_vk(messages, chat_id)



def init_longpoll():
    print('function init_longpoll')
    group_id = '197440489'
    vk_session = vk_api.VkApi(token=token)
    longpoll = VkBotLongPoll(vk_session, group_id)
    return longpoll

def emergency_notification_protocol(peer_id, group_id, chat_id, status, user_id):
    print('function emergency_notification_protocol')
    vk = vk_auth()
    users = vk.messages.getConversationMembers(peer_id=peer_id, group_id=group_id)
    for user in users['items']:
        if user_id == user['member_id']:
            if not 'is_admin' in user:
                messages = 'Вы не админ'
                send_vk(messages, chat_id)
                return
            break
    messages = 'Чрезвычайная ситуация! Запускается протокол всеобщего оповещения... '
    send_vk(messages, chat_id)
    if status == '/красныйпиксель':
        messages = '@all ОБНАРУЖЕН КРАСНЫЙ ПИКСЕЛЬ'
    elif status == "/нампизда":
        messages = '@all НАМ ПИЗДА'
    elif status == '/форпостгорит':
        messages = '@all ФОРПОСТ ГОРИТ'
    send_vk(messages, chat_id)


def main():
    print('function main')
    try:
        vk = vk_auth()
        longpoll = init_longpoll()
        print('Бот запущен')
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and event.obj.text:
                try:
                    peer_id = 2000000000 + int(event.chat_id)
                    group_id = '197440489'
                    chat_id = event.chat_id
                    from_id = event.obj.from_id
                    is_chat = True
                except:
                    user_id = event.obj.from_id
                    messages = 'Я работаю только в чатах'
                    vk = vk_auth()
                    vk.messages.send(user_id=event.obj.from_id, message=messages, random_id=0, peer_id=user_id)
                    is_chat = False

                if is_chat:
                    peer_id = 2000000000 + int(event.chat_id)
                    group_id = '197440489'
                    chat_id = event.chat_id
                    from_id = event.obj.from_id
                    text = event.obj.text
                    first_word = event.obj.text.lower().split()[0]
                    if first_word == '/помощь':
                        command_help(chat_id)
                    elif first_word == '/онлайн':
                        command_online(peer_id, group_id, chat_id)
                    elif first_word == '/монетка':
                        command_flip(chat_id)
                    elif first_word == '/ролл':
                        command_roll(text, chat_id)
                    elif first_word == '/кто':
                        command_who(peer_id, group_id, chat_id)
                    elif first_word == '/шанс':
                        messages = f'Вероятность - {randint(1, 100)}%'
                        send_vk(messages, chat_id)
                    elif first_word == '/кик':
                        command_kick(text, peer_id, group_id, from_id, chat_id)
                    elif first_word == '/погода':
                        second_word = event.obj.text.lower().split()[1]
                        command_weather(second_word, chat_id)
                    elif text == '/нампизда' or text == '/форпостгорит' or text == '/красныйпиксель':
                        emergency_notification_protocol(peer_id, group_id, chat_id, text, from_id)
                    elif text == '/самоликвидация':
                        users = vk.messages.getConversationMembers(peer_id=peer_id, group_id=group_id)
                        for user in users['items']:
                            if from_id == user['member_id']:
                                if not 'is_admin' in user:
                                    messages = 'Вы не админ'
                                    send_vk(messages, chat_id)
                                    return
                                break
                        messages = 'Черезвычайная ситуация! Запускается протокол самоликвидации...'
                        send_vk(messages, chat_id)
                        print(f'Самоликвидация, инициатор - {from_id}')
                        break
            elif 'attachments' in event.obj and event.obj['attachments']:
                chat_id = event.chat_id
                attachments = event.obj['attachments'][0]
                if attachments['type'] == 'audio_message':
                    messages = 'Буквы бесплатные, пошел нахуй'
                    send_vk(messages, chat_id)

            action = event.obj.action
            if action:
                if action['type'] == 'chat_invite_user':
                    check_user(action['member_id'], event.chat_id)
                elif action['type'] == 'chat_invite_user_by_link':
                    check_user(event.obj['from_id'], event.chat_id)
                elif action['type'] == 'chat_kick_user':
                    try:
                        vk.messages.removeChatUser(chat_id=chat_id, member_id=action['member_id'])
                    except:
                        pass
    except Exception as exception:
        print('Exception - \n', exception)
        sleep(1)
        vk.messages.send(user_id=283174597, message=exception, random_id=0, peer_id=283174597)
        main()






if __name__ == '__main__':
    main()
