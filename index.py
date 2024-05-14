import datetime

def quarter():
    today = datetime.date.today()

    if datetime.date(2024, 3, 25) <= today <= datetime.date(2024, 6, 20):
        return 4
    elif datetime.date(2023, 12, 21) <= today <= datetime.date(2024, 3, 24):
        return 3
    elif datetime.date(2023, 10, 25) <= today <= datetime.date(2023, 12, 20):
        return 2
    else:
        return 1


def make_response(text, tts=None, session_state=None, user_state_update=None, end_session=None):
    response = {
        'text': text,
        'tts': tts if tts is not None else text,

    }

    webhook_response = {
        'response': response,
        'version': '1.0',

    }
    if session_state is not None:
        webhook_response['session'] = state 

    if end_session is not None:
        webhook_response['end_session'] = end_session # заполняется, если был задан, по ключу

    if user_state_update is not None:  # заполняется если был задан
        webhook_response['user_state_update'] = user_state_update

    return webhook_response


def what_curs(event):
    text = "Я ещё не знаю, на каком курсе ты учишься. Подскажешь мне?"
    return make_response(text)


def end_event(event):
    text = "Очень жаль! Увидимся в следующий раз"
    return make_response(text, end_session = True)


def fallback(event):
    return make_response(
        "Извините, я не поняла! Переформулируйте запрос, пожалуйста")


def what_level(event):
    intent = event['request']['nlu']['intents']
    curs = intent['course']['slots']['course']['value']
    curs_text = event['request']['original_utterance']
    event['user_state_update']: {'curs_for_search': curs}  # обновление состояния пользователя - был указан курс
    return make_response(text='Замечательно! Подскажи, ты учишься на бакалавриате или магистратуре?',
                         user_state_update={'curs_for_search': curs, 'curs_text': curs_text})


def what_direction(event):
    intent = event['request']['nlu']['intents']
    curs = intent['course']['slots']['course']['value']
    curs_text = event['request']['original_utterance']
    return make_response(
        text='Отлично! Теперь скажи направление и формат, на котором ты учишься. Например, скажи: бакалавриат, бизнес-информатика, очно',
        user_state_update={'curs_for_search': curs, 'curs_text': curs_text})


def spravka(event):
    return make_response(
        "Привет, я помогу тебе узнать расписание основных дисциплин, если ты - студент Нижегородской Вышки. Например, ты хочешь узнать расписание по философии. Скажи: Алиса, когда у меня философия? Или: Алиса, что у меня во вторник? Я с радостью помогу! Чтобы поменять данные, скажи: хочу поменять данные")


def change_data(event):
    return make_response(text="Данные обнулены. Назови курс, на котором учишься",
                         user_state_update={'curs_for_search': None, 'napravlenie_for_search': None,
                                            'level_for_search': None, 'group_for_search': None, 'day_today': None,
                                            'month_today': None, 'quater_today': None, 'format_for_search': None,
                                            'link': None})



def start_raspisanie(event):
    intent = event['request']['nlu']['intents']
    group = intent['what_group']['slots']['groups']['value']
    group_text = event['request']['original_utterance']
    return make_response(text='Отлично! Теперь можем начать. Что ты хочешь узнать?',
                         user_state_update={'group_for_search': group, 'group_text': group_text})

   
def start_rasp_with_weekday(event):
    weekday = event['request']['nlu']['intents']['when_weekday']['slots']['weekday']['value']
    zapros = "Запрос на расписание по дню недели. Код дня недели: " + str(weekday)
    return make_response(text=zapros)


def is_holidays(month, date):
    arr = ["0803", "2302", "3112", "0101", "0201", "0301", "0401", "0501", "0601", "0701", "0801", "0901", "0905"]
    for a in arr:
        if (date == a):
            return 1
    if (month == "07" or month == "08"):
        return 1

    return 0


def start_rasp_with_date(event):
    day = event['request']['nlu']['intents']['when_date']['slots']['date']['value']['day']
    form = event.get('state').get('user', {}).get('format_for_search')
    day_relative = event['request']['nlu']['intents']['when_date']['slots']['date']['value']['day_is_relative']
    schedule_arr_OZ = event.get('state').get('user', {}).get('schedule_arr_OZ')
    date_today = "ddmm"
    date_for_search = "ddmm"
    day_for_search = "dd"
    month_for_search = "mm"
    # нужно привести все данные к формату DDMM:

    if (day_relative is True):  # если запрос формата завтра/послезавтра
        date_today = datetime.datetime.now()
        relative_days = datetime.timedelta(day)
        date_for_search = date_today + relative_days

        day_today = str(date_today.day)
        month_today = str(date_today.month)
        day_for_search = str(date_for_search.day)
        month_for_search = str(date_for_search.month)

        if (len(day_today) is 1):
            day_today = "0" + day_today
        if (len(month_today) is 1):
            month_today = "0" + month_today
        if (len(day_for_search) is 1):
            day_for_search = "0" + day_for_search
        if (len(month_for_search) is 1):
            month_for_search = "0" + month_for_search

        # day_for_search = int(day_today) + day
        # month_for_search = month_today #ДОБАВИТЬ ИЗМЕНЕНИЕ МЕСЯЦА, ЕСЛИ НАПРИМЕР ЗАПРОС НА РАСПИСАНИЕ ЗАВТРА, А У НАС 31 ЯНВАРЯ
        date_today = day_today + month_today
        date_for_search = day_for_search + month_for_search
        # date_for_search = str(day_for_search) + month_for_search

    elif (day_relative is False):  # если запрос формата "что будет пятого марта"
        month = event['request']['nlu']['intents']['when_date']['slots']['date']['value']['month']
        day = str(day)
        month = str(month)
        if (len(day) is 1):
            day = "0" + day
        if (len(month) is 1):
            month = "0" + month

        day_for_search = day
        month_for_search = month
        date_for_search = day + month

    a = is_holidays(month_for_search, date_for_search)  # проверяем, является ли указанная дата праздником

    if (a is 1):
        text = "В этот день точно нет пар!"
        return make_response(text)

    else:
        zapros = str(day) + " - запрос на получение расписания по дате, " + str(date_today) + " - день сегодня, " + str(
                date_for_search) + " - искомая дата"
        return make_response(zapros)
        

def start_rasp_with_master(event):
    intent = event['request']['nlu']['intents']
    master_surname = intent['when_master']['slots']['surname']['value']['last_name']
    zapros = master_surname + " - запрос на получение расписания по фамилии преподавателя"
    return make_response(text=zapros)


def start_rasp_sub(event):
    sub = event['request'].get('nlu', {}).get('tokens')[-1]
    zapros = sub + " -  запрос на расписание по названию предмета"
    return make_response(text=zapros)



def handler(event, context):
    intents = event['request'].get('nlu', {}).get('intents')  # интенты
    form = event.get('state').get('user', {}).get('format_for_search')
    curs = event.get('state').get('user', {}).get('curs_for_search')  # какой курс у пользователя
    group = event.get('state').get('user', {}).get('group_for_search')  # какая группа у пользователя
    level = event.get('state').get('user', {}).get('level_for_search')  # какой уровень образования у пользователя
    level_text = event.get('state').get('user', {}).get('level_text')
    group_text = event.get('state').get('user', {}).get('group_text')
    curs_text = event.get('state').get('user', {}).get('curs_text')
    napravlenie = event.get('state').get('user', {}).get('napravlenie_for_search')
    napr_text = event.get('state').get('user', {}).get('napr_text')
    
    if event['session']['new']:
        txt = "Привет! Я подскажу расписание Высшей Школы Экономики. Чтобы подробнее узнать о том, что я умею, ты можешь попросить меня показать справку." 
        return make_response(
            text = txt, tts = "Привет! Я расскажу тебе о расписании ВШЭ. Чтобы вызвать справку и подробнее узнать, как мной пользоваться, скажи - покажи справку.")
        


    elif 'when_master' in intents and 'when_subject' in intents:  # путает преподавателя с назанием предмета - вызываются обе функции, если не сделать такое условие
        if (napravlenie is None or curs is None or group is None or level is None):
            return make_response(text="Стой, мы же пока не знакомы! Для начала скажи, на каком курсе ты учишься?");
        else:
            return start_rasp_with_master(event)

    elif 'when_subject' in intents:
        if (napravlenie is None or curs is None or group is None or level is None):
            return make_response(text="Стой, мы же пока не знакомы! Для начала скажи, на каком курсе ты учишься?");
        else:
            return start_rasp_sub(event) 

    elif 'when_date' in intents:
        if (napravlenie is None or curs is None or group is None or level is None):
            return make_response(text="Стой, мы же пока не знакомы! Для начала скажи, на каком курсе ты учишься?");
        else:
            return start_rasp_with_date(event)

    elif 'when_weekday' in intents:
        if (napravlenie is None or curs is None or group is None or level is None):
            return make_response(text="Стой, мы же пока не знакомы! Для начала скажи, на каком курсе ты учишься?");
        else:
            return start_rasp_with_weekday(event)



    elif 'course' in intents and curs is None:  # если в запросе пользователя есть номер курса
        return what_direction(event)

    elif 'direction' in intents and napravlenie is None:
        intent = event['request']['nlu']['intents']
        napravlenie = intent['direction']['slots']['direction']['value']
        napr_text = event['request']['original_utterance']
        form = intent['direction']['slots']['format']['value']
        level = intent['direction']['slots']['level']['value']
        return make_response(text='Внимательно запоминаю информацию. Последний вопрос - в какой группе ты учишься?',
                             user_state_update={'napravlenie_for_search': napravlenie, 'napr_text': napr_text,
                                                'format_for_search': form, 'level_for_search': level})  # если в запросе есть направление


    elif 'what_group' in intents and group is None:
        return start_raspisanie(event)




    elif ('course' in intents and curs is not None) or ('direction' in intents and napravlenie is not None) or (
            'what_group' in intents and group is not None) or ('what_level' in intents and level is not None) or (
            'what_format' in intents and napr_text is not None):  # если пользователь называет данные, которые уже есть
        return make_response("Кажется, вы уже рассказали мне о себе! Вы учитесь " +
                             str(curs_text) + " курсе,  " + str(napr_text) + " " +
                             str(group_text) + " группе? Если хотите поменять данные, скажите: поменять данные")




    elif 'change_data' in intents:  # запрос на смену данных
        return change_data(event)

    elif 'end_rasp' in intents:  # выход из функции
        return end_event(event)

    elif 'what_you_can' in intents:  # справка
        return spravka(event)


    else:  # если непонятно, что сказал пользователь
        return fallback(event)

    return {
        'response': {
            'text': text,

        },
        'version': '1.0',
    }
