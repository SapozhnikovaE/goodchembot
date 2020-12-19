import os
import json
import random

import telebot  

# chemistryTest @goodchemBot.

token = 'posle sdachi vyveshu'
bot = telebot.TeleBot(token)
users = dict()

# Класс для хранения данных состоянии теста конкретного пользователя:


class UserData:
    def __init__(self, questions):
        self.questions = questions
        self.answers = []

# Загрузка данных c вопросами из файла:


def load_data(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


data = load_data("data.json")

# Создаем кнопки с возможными ответами:

def create_keyboard(user_id, answers, step):
    keyboard = telebot.types.InlineKeyboardMarkup()
    for i, answer in enumerate(answers):
        callback_data = str(user_id)+' '+str(step)+' '+str(i)
        key = telebot.types.InlineKeyboardButton(text=answer,
                                                 callback_data=callback_data)
        keyboard.add(key)
    return keyboard

# Вывод информации о вопросе в консоль:

def print_question(question):
    print("Вопрос:", question["text"])
    for i, answer in enumerate(question["answers"]):
        print(f'{i}. "{answer}"')
    print("Правильный ответ:", question["right_answer"])
    print()

# Переход и отображение следующего вопроса:

def show_next_question(user_id, step, question):
    print_question(question)
    keyboard = create_keyboard(user_id, question['answers'], step)
    bot.send_message(user_id, text=question['text'], reply_markup=keyboard)

# Начало теста, вывод первого вопроса:

def start_test(message):
    questions = random.choices(range(len(data['questions'])), k=10)
    user_data = UserData(questions)
    users[message.from_user.id] = user_data
    step = 0
    question = data['questions'][user_data.questions[step]]
    show_next_question(message.from_user.id, step, question)

# Завершение тестов, вывод результатов:

def finish_test(user_id, user_data):
    points = 0 # баллы
    for i, question_index in enumerate(user_data.questions):
        right_answer = data['questions'][question_index]['right_answer']
        if user_data.answers[i] == right_answer: # ответ правильный
            points += 1
    msg = (f'Тест завершен, набрано баллов: {points}/{len(user_data.questions)}\n'
            'Что бы пройти тест еще раз введите: /test \n'
            'Для того чтобы получить справку введите: /info')
    print(f"Пользователь #{user_id} завершил тест: {points}/{len(user_data.questions)}")
    bot.send_message(user_id, msg)
    users.pop(user_id)  # Удаляем данные о пользователе

# Справка

def show_info(message):
    dir = 'info'
    files = os.listdir(dir)
    for file_name in files:
        bot.send_photo(message.from_user.id, open(os.path.join(dir,file_name), 'rb'))       

#  Функция-обработчик сообщений от пользователя.

@bot.message_handler(content_types=["text"])
def message_recived(message):
    if message.text == '/start':
        msg = ("Привет! \n"
               "Вас приветствует химический бот по изучению качественных реакций.\n"
               "Чем займемся?\n" 
               "Для прохождения теста введите /test,\n"
               "для получения справочной информации /info")
        bot.send_message(message.from_user.id, msg)      
    elif message.text == '/test':
        start_test(message)
    elif message.text == '/info':
        show_info(message)
    else:
        msg = (f'Команда "{message.text}" неверная!\n'
               'Для того чтобы начать тест введите: /test\n'
               'Для того чтобы получить справку введите: /info')
        bot.send_message(message.from_user.id, msg)

# Функция-обработчик нажатий на кнопки

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    try:
        # Преобразовывем строку от телеграмма с в данные о нажатии на кнопку-ответа
        user_id, question_index, user_answer = \
            [int(s) for s in call.data.split()]
        user_data = users.get(user_id)  # ищем данные о пользователе по его id
        if user_data:
            # Текущий шаг - он же текущий вопрос (индекс вопроса)
            step = len(user_data.answers)
            if question_index == step:
                # Запоминаем ответ пользователя на вопрос
                user_data.answers.append(user_answer)
                
                # Вывод:  "Правильно/неправильно"              
                right_answer = data['questions'][user_data.questions[step]]['right_answer']
                msg = "Правильно!" if user_answer == right_answer else "Неправильно!"                                
                bot.send_message(user_id, msg)
                
                # Переход к следующему вопросу или завершение теста
                print(f"Пользователь #{user_id} ответил: {user_answer} {msg}\n")
                step += 1
                if step < len(user_data.questions):  # следующий вопрос
                    question = data['questions'][user_data.questions[step]]
                    show_next_question(user_id, step, question)
                else:  # вопросы закончились, считаем баллы и выводим сообщения
                    finish_test(user_id, user_data)
    except Exception as e:
        print(e)


def main():
    random.seed()
    bot.polling(none_stop=True)


if __name__ == "__main__":
    main()
