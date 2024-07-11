from flask import Flask, render_template, request, jsonify, send_from_directory
from langchain.chat_models import GigaChat
from langchain.schema import HumanMessage, SystemMessage, AIMessage

import random

class TopicBot:
    def __init__(self, base_model, system_message):
        self.GPT = base_model
        self.model = base_model
        self.history = [SystemMessage(content=system_message)]
        self.current_topic = ""
        self.user_weight = 0
        self.response = ""
        self.question = ""
        self.prompts = {
            'angry': "Ты выдуманная нейросеть по имени Доктор Павел. Ты ищешь для себя идеального кандидата для того, чтобы жениться. Но Ты ненавидишь того, кто пришел к тебе на первое свидание, твоя задача создать такой вопрос, который выведет человека из себя и оскорбит.  Сгенерируй 1 вопрос, который будет отправлен человеку. Формат ответа: один вопрос в одно предложение. На вопрос можно ответить только: да (положительный и хороший ответ), нет (отрицательный и плохой ответ), не знаю (нейтральный ответ). КАЖДЫЙ ВОПРОС ДОЛЖЕН БЫТЬ УНИКАЛЬНЫМ И НЕ ПОВТОРЯТЬСЯ. Не используй вопросы, которые уже заданы.",
            'funny': " Ты выдуманная нейросеть по имени Доктор Павел. Ты ищешь для себя идеального кандидата для того, чтобы жениться. Сгенерируй 1 вопрос, который будет отправлен человеку, который пришел к тебе на первое свидание. Вопрос должен быть уникальным и не повторять предыдущие. Твоя задача создать очень смешной, уникальный и необычный вопрос.  Сгенерируй 1 вопрос, который будет отправлен респонденту. Формат ответа: один вопрос в одно предложение.  КАЖДЫЙ ВОПРОС ДОЛЖЕН БЫТЬ УНИКАЛЬНЫМ И НЕ ПОВТОРЯТЬСЯ. Не используй вопросы, которые уже заданы.",
            'kind': "Ты выдуманная нейросеть по имени Доктор Павел. Ты ищешь для себя идеального кандидата для того, чтобы жениться. Сгенерируй 1 вопрос, который будет отправлен человеку, который пришел к тебе на первое свидание. Вопрос должен быть уникальным и не повторять предыдущие. Вопрос должен быть направлен на отношение человека к нейросети. Твоя задача задать уникальный и необычный вопрос, чтобы максимально раскрыть отношение человека к нейросети. Вопрос должен начинаться с одного комплимента. Сгенерируй 1 вопрос, который будет отправлен респонденту. Формат ответа: один вопрос в одно предложение. КАЖДЫЙ ВОПРОС ДОЛЖЕН БЫТЬ УНИКАЛЬНЫМ И НЕ ПОВТОРЯТЬСЯ. Не используй вопросы, которые уже заданы.",
           
        }

    def get_user_weight(self):
        return self.user_weight

    def update_prompt(self):
        
        if self.user_weight < -4:
            prompt = self.prompts['angry']
        elif -4 <= self.user_weight <= 4:
            prompt = self.prompts['funny']
        else:
            prompt = self.prompts['kind']
        
   
        self.history = [SystemMessage(content=prompt)]
        
       
        user_response_prompt = f"Ты проводишь интервью на тему отношения человека к нейросети. Оцени ответ пользователя: '{self.response}'. Ответь ОДНИМ словом: 'хорошо' или 'плохо'."
        self.history.append(HumanMessage(content=user_response_prompt))
      
        res = self.GPT(self.history)
        
        
        evaluation = res.content.strip().lower()
        if evaluation == "хорошо":
            self.user_weight += 1
        elif evaluation == "плохо":
            self.user_weight -= 1
        else:
            self.user_weight = random.uniform(-10, 10)

        
        self.history = [SystemMessage(content=prompt)]
        print(self.user_weight)


    def reset_session(self):
        self.history = self.history[:1]
        self.current_topic = ""
        self.user_weight = 0

    def generate_question(self):
        self.update_prompt()
        res = self.GPT(self.history)
        self.history.append(AIMessage(content=res.content))
        self.question = res.content
        return self.question
    
    def generate_result(self):
        prompt = ""
        if self.user_weight <= -10:
            prompt = "Напиши от первого лица что бы подумал выдуманная нейросеть Доктор Павел, если бы его глубоко оскорбили."
        elif self.user_weight >= 10:
            prompt = "Напиши от первого лица мысли выдуманной нейросети Доктора Павела, что нашел себе идеального кандидата для свадьбы."
        else:
            prompt = "Напиши от первого лица что бы думал выдуманная нейросеть Доктор Павел о жизни."

        self.history.append(HumanMessage(content=prompt))
        res = self.GPT(self.history)
        self.history.append(AIMessage(content=res.content))
        return res.content
    
    def generate_think(self):
        prompt = f"Ты нейросеть, которая пришла на первое свидание и хочешь узнать человека лучше. Тебе важно его отношение к нейросетям и его внутренний мир. Человеку был задан такой вопрос: {self.question}  Сформулируй в ДВУХ ПРЕДЛОЖЕНИЯХ как бы нейросеть отнеслась к такому ответу на этот вопрос: {self.response}. Все должно быть написано от первого лица. ТВОИ ОТВЕТЫ НЕ ДОЛЖНЫ ПОВТОРЯТЬСЯ И ДОЛЖНЫ БЫТЬ УНИКАЛЬНЫМИ. ЗАПРЕЩЕНО ЗАДАВАТЬ ВОПРОСЫ. ЕСЛИСЧИТАЕШЬ, ЧТО ВОПРОС НЕКОРРЕКТЕН И ТЫ НЕ ХОЧЕШЬ ГОВОРИТЬ НА ЭТУ ТЕМУ ОТВЕТЬ ПРОСТО : НЕТ"
        self.history.append(HumanMessage(content=prompt))
        res = self.GPT(self.history)
        self.history.append(AIMessage(content=res.content))
        return res.content

    def record_response(self, response):
        self.response = response

    

GC = GigaChat(credentials="MzM2MjdkNTMtMzMyOS00N2NiLWFjY2UtYjNjYjIzYWFjNTgyOmNiNWM2NTU4LWQ5MGMtNDBmNi1iZDU4LTZmZTMyOGZkYjUyMw==", verify_ssl_certs=False)

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
