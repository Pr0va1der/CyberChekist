import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from random import randint
from time import sleep

token = '408b25eb64e05c943c7f1e72b436be1521939d42af140179ca4b23b4f0bef3738ed196c343b23c1ec0d6e'


def vk_auth():
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    return vk


def send_vk(text, chat_id, is_alert=0):
    vk = vk_auth()
    vk.messages.send(chat_id=chat_id, message=text, random_id=0, disable_mentions=is_alert)


def read_file():
    with open('bad_groups.txt', 'r', encoding='UTF-8') as file:
        list = file.read().splitlines()
        return list


def kick_member(user_id, chat_id, messages=None):
    vk = vk_auth()
    if messages:
        send_vk(messages, chat_id)
    vk.messages.removeChatUser(chat_id=chat_id, member_id=user_id)


# Проверка пользователя на ересь в подписках
def check_users(users, chat_id):
    vk = vk_auth()
    groups = read_file()
    for user in users:
        for group in groups:
            is_member = vk.groups.isMember(group_id=group, user_id=user)
            if white_list(user):
                break
            elif is_member:
                messages = 'Обнаружена ересь! Нейтрализация еретика...'
                kick_member(user, chat_id, messages)
                messages = 'Еретик нейтрализован'
                break


def white_list(user):
    with open('white_list.txt', 'r', encoding='UTF-8') as file:
        list = file.read().splitlines()
        if str(user) in list:
            return True


# Возвращает список новых пользователей, сравнивая пользователей до и после
def find_difference(list_1, list_2):
    members_list_1 = []
    members_list_2 = []
    for i in list_1:
        members_list_1.append(i['member_id'])
    for i in list_2:
        members_list_2.append(i['member_id'])
    difference = list(set(members_list_1) - set(members_list_2))
    return difference


def sender_is_admin(list, user_id):
    for user in list['items']:
        if user_id == user['member_id'] and 'is_admin' in user:
            admin = True
            return admin


# can_kick(users_list, event.obj.from_id, user_id, chat_id)
def can_kick(list, user_id, user_kick, chat_id):
    is_admin = None
    is_kick = None
    for user in list['items']:
        if user_id == user['member_id'] and 'is_admin' in user:
            is_admin = True
        elif user_id == user['member_id'] and not 'is_admin' in user:
            messages = 'Вы не администратор'
            send_vk(messages, chat_id)

        if user_kick == user['member_id'] and 'can_kick' in user:
            is_kick = True
        elif user_kick * (-1) == user['member_id'] and 'can_kick' in user:
            is_kick = True
        elif user_kick == user['member_id'] or user_kick * (-1) == user['member_id']:
            messages = 'Этого пользователя невозможно исключить'
            send_vk(messages, chat_id)

    if is_admin and is_kick:
        return True
    else:
        return False


def user_in_list(list, user):
    flag = False
    for i in range(len(list['profiles'])):
        if user == list['profiles'][i]['id']:
            flag = True
            break
        else:
            flag = False
    return flag


def main():
    is_kicked = None
    group_id = '197440489'
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, group_id)
    print('Бот запущен')
    users_finite = None

    for event in longpoll.listen():
        try:
            try:
                peer_id = 2000000000 + int(event.chat_id)
                chat_id = event.chat_id
                is_chat = True
            except:
                user_id = event.obj.user_id
                is_chat = False
            if is_chat:
                users_init = vk.messages.getConversationMembers(peer_id=peer_id, group_id=group_id)
                if users_finite and users_init != users_finite:
                    if users_finite['count'] < users_init['count']:
                        new_user = find_difference(users_init['items'], users_finite['items'])
                        check_users(new_user, chat_id)
                    elif users_finite['count'] > users_init['count']:
                        if not is_kicked and not sender_is_admin(users_init, event.obj.from_id):
                            leave_user = find_difference(users_finite['items'], users_init['items'])
                            for user in leave_user:
                                kick_member(user, chat_id)
                users_finite = vk.messages.getConversationMembers(peer_id=peer_id, group_id=group_id)
                is_kicked = False

            if event.type == VkBotEventType.MESSAGE_NEW and event.obj.text:

                if is_chat:

                    if event.obj.text.lower().split()[0] == '/помощь':
                        with open('help_commands.txt', 'r', encoding='UTF-8') as file:
                            messages = file.read()
                            send_vk(messages, chat_id)
                    elif event.obj.text.lower().split()[0] == '/онлайн':
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
                                online_users += f'•{device_status}[{user["screen_name"]}|{user["first_name"]} {user["last_name"]}] {online_status}'
                        send_vk(online_users, chat_id, is_alert=1)
                    elif event.obj.text.lower().split()[0] == '/монетка':
                        if randint(0, 1):
                            random_flip = 'Орел'
                        else:
                            random_flip = 'Решка'
                        messages = f'Тебе выпало: {random_flip}'
                        send_vk(messages, chat_id)
                    elif event.obj.text.lower().split()[0] == '/ролл':
                        try:
                            if event.obj.text.lower().split()[1]:
                                if int(event.obj.text.lower().split()[1]) < 1000:
                                    try:
                                        messages = f'Случайное число: {randint(1, int(event.obj.text.lower().split()[1]))}'
                                        send_vk(messages, chat_id)
                                    except:
                                        messages = 'Вы ввели неверное число. Повторите попытку'
                                        send_vk(messages, chat_id)
                                else:
                                    messages = 'Слишком большое число. Повторите попытку'
                                    send_vk(messages, chat_id)
                        except:
                            messages = 'Вы не ввели число. Повторите попытку'
                            send_vk(messages, chat_id)
                    elif event.obj.text.lower().split()[0] == '/кто':
                        vk = vk_auth()
                        users_list = vk.messages.getConversationMembers(peer_id=peer_id, group_id=group_id)
                        who_number = randint(1, len(users_list['profiles'])) - 1
                        users = users_list['profiles']
                        user = f'[{users[who_number]["screen_name"]}|{users[who_number]["first_name"]} {users[who_number]["last_name"]}]'
                        messages = f'Это {user}'
                        send_vk(messages, chat_id, is_alert=1)
                    elif event.obj.text.lower().split()[0] == '/шанс':
                        messages = f'Вероятность - {randint(1, 100)}%'
                        send_vk(messages, chat_id)
                    elif event.obj.text.lower().split()[0] == '/кик':
                        if len(event.obj.text.lower().split()) > 1:
                            if event.obj.text.lower().split()[1].split('/')[0] == 'https:' and \
                                    event.obj.text.lower().split()[1].split('/')[2] == 'vk.com':
                                users_list = vk.messages.getConversationMembers(peer_id=peer_id, group_id=group_id)
                                user_nick = event.obj.text.lower().split()[1].split('/')[3]
                                user_id = vk.utils.resolveScreenName(screen_name=user_nick)['object_id']
                                user_in_list(users_list, user_id)
                                if user_in_list(users_list, user_id):
                                    if can_kick(users_list, event.obj.from_id, user_id, chat_id):
                                        vk.messages.removeChatUser(chat_id=chat_id, member_id=user_id)
                                        is_kicked = True
                                else:
                                    messages = 'Пользователь не участник беседы'
                                    send_vk(messages, chat_id)
                            else:
                                messages = 'Неверная ссылка. Повторите попытку'
                                send_vk(messages, chat_id)
                        else:
                            messages = 'Вы не ввели ссылку. Повторите попытку'
                            send_vk(messages, chat_id)
        except Exception as exception:
            print('Exception: ', exception)
            sleep(120)
            main()


if __name__ == '__main__':
    main()