import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
token = '408b25eb64e05c943c7f1e72b436be1521939d42af140179ca4b23b4f0bef3738ed196c343b23c1ec0d6e'


def vk_auth():
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    return vk


def send_vk(text, chat_id):
    vk = vk_auth()
    vk.messages.send(chat_id=chat_id, message=text, random_id=0)


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
def check_user(users, chat_id):
    vk = vk_auth()
    groups = read_file()

    for user in users:
        for group in groups:
            is_member = vk.groups.isMember(group_id=group, user_id=user)
            if is_member:
                messages = f'Обнаружена ересь, еретик - {user_id}'
                kick_member(user, chat_id, messages)
                break


# Возвращает список новых пользователей, сравнивая пользователей до и после
def find_differehce(list_1, list_2):
    members_list_1 = []
    members_list_2 = []
    for i in list_1:
        members_list_1.append(i['member_id'])
    for i in list_2:
        members_list_2.append(i['member_id'])
    difference = list(set(members_list_1) - set(members_list_2))
    return difference


def main():
    group_id = '197440489'
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, group_id)
    print('Бот запущен')
    users_finite = None

    for event in longpoll.listen():
        chat_id = 2000000000 + int(event.chat_id)
        if event.type == VkBotEventType.MESSAGE_NEW:
            users_init = vk.messages.getConversationMembers(peer_id=chat_id, group_id='197440489')
            if users_finite and users_init != users_finite:
                if users_finite['count'] < users_init['count']:
                    new_user = find_differehce(users_init['items'], users_finite['items'])
                    check_user(new_user, event.chat_id)
                elif users_finite['count'] > users_init['count']:
                    leave_user = find_differehce(users_finite['items'], users_init['items'])
                    for user in leave_user:
                        kick_member(user, event.chat_id)
            users_finite = vk.messages.getConversationMembers(peer_id=2000000000 + int(event.chat_id),
                                                              group_id='197440489')


if __name__ == '__main__':
    main()