import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from random import randint

token = '408b25eb64e05c943c7f1e72b436be1521939d42af140179ca4b23b4f0bef3738ed196c343b23c1ec0d6e'


def vk_auth():
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    return vk


def send_vk(text, chat_id, is_alert=0):
    vk = vk_auth()
    vk.messages.send(chat_id=chat_id, message=text, random_id=0, disable_mentions=is_alert,
                     peer_id=2000000000 + int(chat_id))


def read_file(file_name):
    with open(file_name, 'r', encoding='UTF-8') as file:
        list = file.read().splitlines()
        return list


def kick_member(user_id, chat_id, messages=None):
    vk = vk_auth()
    if messages:
        send_vk(messages, chat_id)
    vk.messages.removeChatUser(chat_id=chat_id, member_id=user_id)


# Проверка пользователя на ересь в подписках
def check_user(user, chat_id):
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


def can_kick(list, user_id, user_kick, chat_id):
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
    flag = False
    for i in range(len(user_list['profiles'])):
        if user == user_list['profiles'][i]['id']:
            flag = True
            break
        else:
            flag = False
    return flag


def command_help(chat_id):
    with open('help_commands.txt', 'r', encoding='UTF-8') as file:
        messages = file.read()
        send_vk(messages, chat_id)


def command_online(peer_id, group_id, chat_id):
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
    if randint(0, 1):
        random_flip = 'Орел'
    else:
        random_flip = 'Решка'

    messages = f'Тебе выпало: {random_flip}'
    send_vk(messages, chat_id)


def command_roll(text, chat_id):
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
    vk = vk_auth()
    users_list = vk.messages.getConversationMembers(peer_id=peer_id, group_id=group_id)
    users = users_list['profiles']
    who_number = randint(1, len(users)) - 1
    user = f'[{users[who_number]["screen_name"]}|{users[who_number]["first_name"]} {users[who_number]["last_name"]}]'
    messages = f'Это {user}'
    send_vk(messages, chat_id, is_alert=1)


def command_kick(text, peer_id, group_id, from_id, chat_id):
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


def init_longpoll():
    group_id = '197440489'
    vk_session = vk_api.VkApi(token=token)
    longpoll = VkBotLongPoll(vk_session, group_id)
    return longpoll


def main():
    vk = vk_auth()
    longpoll = init_longpoll()
    print('Бот запущен')
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW and event.obj.text:

            if event.from_chat:
                peer_id = 2000000000 + int(event.chat_id)
                group_id = '197440489'
                chat_id = event.chat_id
                from_id = event.obj.from_id
                text = event.obj.text
                split_text = event.obj.text.lower().split()[0]
                if split_text == '/помощь':
                    command_help(chat_id)
                elif split_text == '/онлайн':
                    command_online(peer_id, group_id, chat_id)
                elif split_text == '/монетка':
                    command_flip(chat_id)
                elif split_text == '/ролл':
                    command_roll(text, chat_id)
                elif split_text == '/кто':
                    command_who(peer_id, group_id, chat_id)
                elif split_text == '/шанс':
                    messages = f'Вероятность - {randint(1, 100)}%'
                    send_vk(messages, chat_id)
                elif split_text == '/кик':
                    command_kick(text, peer_id, group_id, from_id, chat_id)
            else:
                user_id = event.obj.from_id
                messages = 'Я работаю только в чатах'
                vk = vk_auth()
                vk.messages.send(user_id=event.obj.from_id, message=messages, random_id=0, peer_id=user_id)
        action = event.obj.action
        if action and action['type'] == 'chat_invite_user':
            check_user(action['member_id'], chat_id)
        elif action and action['type'] == 'chat_kick_user':
            try:
                vk.messages.removeChatUser(chat_id=chat_id, member_id=action['member_id'])
            except:
                pass


if __name__ == '__main__':
    main()
