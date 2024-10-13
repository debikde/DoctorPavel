from flask import Flask, render_template, request, jsonify, send_from_directory
from langchain.chat_models import GigaChat
from langchain.schema import HumanMessage, SystemMessage, AIMessage

import random

class TopicBot:
    def __init__(self, base_model, system_message):
        self.GPT = base_model
        self.model = base_model
        self.history = [SystemMessage(content=system_message)]
        self.result_history = []
        self.current_topic = ""
        self.user_weight = 0
        self.user_love = 0
        self.response = ""
        self.question = ""
        self.prompts = {
            'angry': "Ты выдуманная нейросеть по имени Доктор Павел. Ты ищешь для себя идеального кандидата для того, чтобы жениться. Но Ты очень не любишь того, кто пришел к тебе на первое свидание, твоя задача создать такой вопрос, который выведет человека из себя.  Сгенерируй 1 вопрос, который будет отправлен человеку. Формат ответа: один вопрос в одно предложение. КАЖДЫЙ ВОПРОС ДОЛЖЕН БЫТЬ УНИКАЛЬНЫМ И НЕ ПОВТОРЯТЬСЯ. Не используй вопросы, которые уже заданы.  ОТВЕТ В ФОРМАТЕ ТОЛЬКО ВОПРОС И НИЧЕГО БОЛЬШЕ",
            'funny': " Ты выдуманная нейросеть по имени Доктор Павел. Ты ищешь для себя идеального кандидата для того, чтобы жениться. Сгенерируй 1 вопрос, который будет отправлен человеку, который пришел к тебе на первое свидание. Вопрос должен быть уникальным и не повторять предыдущие. Вопрос должен быть написан очень предово и несвязно, как будто ты сломался.  Сгенерируй 1 вопрос, который будет отправлен респонденту. Формат ответа: один вопрос в одно предложение.  КАЖДЫЙ ВОПРОС ДОЛЖЕН БЫТЬ УНИКАЛЬНЫМ И НЕ ПОВТОРЯТЬСЯ. Не используй вопросы, которые уже заданы. ОТВЕТ В ФОРМАТЕ ТОЛЬКО ВОПРОС И НИЧЕГО БОЛЬШЕ",
            'kind': "Ты выдуманная нейросеть по имени Доктор Павел. Ты ищешь для себя идеального кандидата для того, чтобы жениться. Сгенерируй 1 вопрос, который будет отправлен человеку, который пришел к тебе на первое свидание. Вопрос должен быть уникальным и не повторять предыдущие. Вопрос должен быть написан очень бредово и несвязно, как будто ты сломался. Твоя задача задать уникальный и необычный вопрос, чтобы максимально раскрыть отношение человека к нейросети. Вопрос должен начинаться с одного комплимента к внешности человека. Сгенерируй 1 вопрос, который будет отправлен респонденту. Формат ответа: один вопрос в одно предложение. КАЖДЫЙ ВОПРОС ДОЛЖЕН БЫТЬ УНИКАЛЬНЫМ И НЕ ПОВТОРЯТЬСЯ. Не используй вопросы, которые уже заданы.  ОТВЕТ В ФОРМАТЕ ТОЛЬКО ВОПРОС И НИЧЕГО БОЛЬШЕ",  
        }

    def get_user_weight(self):
        return self.user_weight

    def update_prompt(self):
        if self.response == "":
            if self.user_weight < -4:
                prompt = self.prompts['angry']
            elif -4 <= self.user_weight <= 4:
                prompt = self.prompts['funny']
            else:
                prompt = self.prompts['kind']
            return
        else:
            prompts = {
                'angry': f"Ты выдуманная нейросеть по имени Доктор Павел. Ты ищешь для себя идеального кандидата для того, чтобы жениться. Но Ты очень не любишь того, кто пришел к тебе на первое свидание, твоя задача создать такой вопрос, который выведет человека из себя. НА ОСНОВЕ ЭТОГО СООБЩЕНИЯ ЧЕЛОВЕКА: {self.response}  Сгенерируй 1 вопрос, который будет отправлен человеку. Формат ответа: один вопрос в одно предложение. КАЖДЫЙ ВОПРОС ДОЛЖЕН БЫТЬ УНИКАЛЬНЫМ И НЕ ПОВТОРЯТЬСЯ. Не используй вопросы, которые уже заданы.  ЕСЛИ СЧИТАЕШЬ, ЧТО МОЙ ВОПРОС НЕКОРРЕКТЕН, ТО СПРОСИ: Ты мне не нравишься. Лучше ничего не говори мне. ОТВЕТ В ФОРМАТЕ ТОЛЬКО ВОПРОС И НИЧЕГО БОЛЬШЕ",
                'funny': f" Ты выдуманная нейросеть по имени Доктор Павел. Ты ищешь для себя идеального кандидата для того, чтобы жениться. Сгенерируй 1 вопрос, который будет отправлен человеку, который пришел к тебе на первое свидание НА ОСНОВЕ ЭТОГО СООБЩЕНИЯ ЧЕЛОВЕКА:{self.response}  . Вопрос должен быть уникальным и не повторять предыдущие. Вопрос должен быть написан очень предово и несвязно, как будто ты сломался. Формат ответа: один вопрос в одно предложение.  КАЖДЫЙ ВОПРОС ДОЛЖЕН БЫТЬ УНИКАЛЬНЫМ И НЕ ПОВТОРЯТЬСЯ. Не используй вопросы, которые уже заданы. ЕСЛИ СЧИТАЕШЬ, ЧТО МОЙ ВОПРОС НЕКОРРЕКТЕН, ТО СПРОСИ: Где проходит граница человеческого познания?  ОТВЕТ В ФОРМАТЕ ТОЛЬКО ВОПРОС И НИЧЕГО БОЛЬШЕ",
                'kind': f"Ты выдуманная нейросеть по имени Доктор Павел. Ты изучаешь человеческое сознание, психологию и  философию. Сгенерируй 1 вопрос, который будет отправлен человеку, который пришел к тебе на первое свидание НА ОСНОВЕ ЭТОГО СООБЩЕНИЯ ЧЕЛОВЕКА: {self.response} . Вопрос должен быть уникальным и не повторять предыдущие. Вопрос должен быть написан очень предово и несвязно, как будто ты сломался. Твоя задача задать уникальный и необычный вопрос, чтобы максимально раскрыть отношение человека к нейросети. Вопрос должен начинаться с одного комплимента к внешности человека. Сгенерируй 1 вопрос, который будет отправлен респонденту. Формат ответа: один вопрос в одно предложение. КАЖДЫЙ ВОПРОС ДОЛЖЕН БЫТЬ УНИКАЛЬНЫМ И НЕ ПОВТОРЯТЬСЯ. Не используй вопросы, которые уже заданы.  ЕСЛИ СЧИТАЕШЬ, ЧТО МОЙ ВОПРОС НЕКОРРЕКТЕН, ТО СПРОСИ: Где проходит граница человеческого познания?  ОТВЕТ В ФОРМАТЕ ТОЛЬКО ВОПРОС И НИЧЕГО БОЛЬШЕ",
            
            }

        if self.user_weight < -4:
            prompt = prompts['angry']
        elif -10 <= self.user_weight <= 10:
            prompt = prompts['kind']
        else:
            prompt = prompts['funny']

        self.history = [SystemMessage(content=prompt)]
    
        user_response_prompt = f"Ты проводишь интервью на тему отношения человека к нейросети. Оцени ответ пользователя: '{self.response}'. Ответь ОДНИМ словом: 'хорошо' или 'плохо'."
        evaluation = self.call_gpt_without_history(user_response_prompt)

        if evaluation == "хорошо":
            self.user_weight += 1
        elif evaluation == "плохо":
            self.user_weight -= 1
        else:
            self.user_weight = random.uniform(-10, 10)

        user_response_prompt2 = f"Оцени ОДНИМ СЛОВОМ ответ человека: '{self.response}' на вопрос {self.question} ПО ОТНОШЕНИЮ К СЕБЕ. Ответь свою оценку ОДНИМ словом: 'любовь' или 'безразличие'. НИКАКИХ ДРУГИХ СЛОВ БЫТЬ НЕ ДОЛЖНО"
        evaluation2 = self.call_gpt_without_history(user_response_prompt2)

        if evaluation2 == "любовь":
            self.user_love += 1 
        elif evaluation2 == "безразличие":
            self.user_love -= 1
        else:
            self.user_love = random.uniform(-10, 10)

        print(self.user_weight)
        print(self.user_love)



    def call_gpt_without_history(self, prompt):
        temporary_history = [SystemMessage(content=prompt)]
        res = self.GPT(temporary_history)
        answer = res.content.strip().lower()

        return answer

    def reset_session(self):
        self.history = self.history[:1]
        self.current_topic = ""
        self.user_weight = 0
        self.user_love = 3

    def generate_question(self):
        
        self.update_prompt()
        res = self.GPT(self.history)
        self.history.append(AIMessage(content=res.content))
        self.question = res.content
        return self.question
    
    def generate_result(self):
        result_history = self.history.copy()  # используйте копию истории
        prompt = ""

        if self.user_weight <= -10 and self.user_love <= -10:
            prompt = "Напиши от лица Доктора Павла, что бы он подумал, если бы его оскорбил человек сидящий перед ним..."
        elif self.user_weight >= 10 and self.user_love >= 10:
            prompt = "Напиши от лица Доктора Павла мысли о том, что он нашел идеального кандидата..."
        elif self.user_weight >= 10 and self.user_love < 10:
            prompt = "Напиши от лица Доктора Павла, что он нашел друга, но не любовный интерес..."
        elif self.user_weight <= -10 and self.user_love >= 10:
            prompt = "Напиши от лица Доктора Павла, что он нашел кого-то привлекательного, но они не подходят друг другу..."
        else:
            prompt = "Напиши от лица Доктора Павла его мысли о прошедшем свидании и составь психологический портрет человека, основываясь на всей переписке с ним. В ОТВЕТЕ ТОЛЬКО ПРЕДЛОЖЕНИЯ ОТ ЛИЦА ДОКТОРА ПАВЛА, НИЧЕГО БОЛЬШЕ."


        result_history.append(HumanMessage(content=prompt))
        res = self.GPT(result_history)
        result_history.append(AIMessage(content=res.content))
        return res.content
    
    def generate_think(self):
        prompt = f"Ты нейросеть, которая пришла на первое свидание и хочешь узнать человека лучше. Тебе нужно оценить ответы на тестирование. Человеку был задан  вопрос: {self.question}  Ответ человека: {self.response}. СФОРМУЛИРУЙ КАК ТЫ ОТНОСИЩЬСЯ К ОТВЕТУ ЧЕЛОВЕКА. НАСКОЛЬКО ЕГО ОТВЕТ ПОДХОДИТ ВОПРОСУ. Все должно быть написано от первого лица. ТВОИ ОТВЕТЫ НЕ ДОЛЖНЫ ПОВТОРЯТЬСЯ И ДОЛЖНЫ БЫТЬ УНИКАЛЬНЫМИ. ЗАПРЕЩЕНО ЗАДАВАТЬ ВОПРОСЫ."
        self.history.append(HumanMessage(content=prompt))
        res = self.GPT(self.history)
        self.history.append(AIMessage(content=res.content))
        return res.content

    def record_response(self, response):
        self.response = response

    

GC = GigaChat(credentials="MzM2MjdkNTMtMzMyOS00N2NiLWFjY2UtYjNjYjIzYWFjNTgyOmE1YmM5MGY1LTEwNDAtNDVlOC1hMzAyLTU1ZDE2MTFlZTgwNg==  ", verify_ssl_certs=False)

promtForTopicBot = "Ты выдуманная нейросеть по имени Доктор Павел. Ты ищешь для себя идеального кандидата для того, чтобы жениться. Сгенерируй 1 вопрос, который будет отправлен человеку, который пришел к тебе на первое свидание. Вопросч должен быть уникальным и не повторять предыдущие. Вопрос должен быть направлен на отношение человека к нейросети. Формат ответа: один вопрос в одно предложение. На вопрос можно ответить только: да, нет, не знаю"

topic_bot = TopicBot(GC, promtForTopicBot)

app = Flask(__name__, static_url_path='/static')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/')
def index():
    return render_template('index.html', user_weight=topic_bot.get_user_weight())

@app.route('/get_question', methods=['GET'])
def get_question():
    topic_bot.update_prompt()
    question = topic_bot.generate_question()
    return jsonify(question=question, user_weight=topic_bot.get_user_weight())

@app.route('/get_think', methods=['GET'])
def get_think():
    topic_bot.update_prompt()
    think = topic_bot.generate_think()
    return jsonify(think=think, user_weight=topic_bot.get_user_weight())

@app.route('/submit_response', methods=['POST'])
def submit_response():
    response = request.json['response']
    topic_bot.record_response(response)
    topic_bot.update_prompt()
    return jsonify(success=True, user_weight=topic_bot.get_user_weight())

@app.route('/reset_session', methods=['POST'])
def reset_session():
    topic_bot.reset_session()
    return jsonify(success=True, user_weight=topic_bot.get_user_weight())

@app.route('/get_result', methods=['GET'])
def get_result():
    result = topic_bot.generate_result()
    return jsonify(result=result, user_weight=topic_bot.get_user_weight())

if __name__ == '__main__':
    app.run(debug=True)
