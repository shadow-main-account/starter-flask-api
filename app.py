from flask import Flask, request, jsonify
from discord.ext import commands
import g4f
import requests
from time import sleep

app = Flask(__name__)

AI_Memory = [
    'Use Memory to enhance responses, although if something they ask is inside of the memory but also training data, use the training data response instead. Do not use memory in each response just keep it in mind and when presented information use memory to provide better answers, Do not use your memory in every response only use it in your response if it matches the question or is related.  Memory: ',
]

g4f.check_pypi_version = False
GPT = g4f.models.gpt_4

print("GPT_VERSION: ", GPT.name)

intents = commands.Bot(command_prefix='\\', intents=discord.Intents.default())

def get_training_data():
    request_data = requests.get(
        'https://raw.githubusercontent.com/223Win/ai-training-data/main/training_data.txt'
    )
    return request_data.text

def get_memory():
    return AI_Memory

def add_memory(item: str):
    AI_Memory.append(' ' + item)

def get_memory_string():
    return ''.join(AI_Memory)

Training_Data = get_training_data()

def generate_text(input_str: str):
    GPT_CONTENT = (
        'Use Data to improve responses. Data: '
        + Training_Data
        + '\n'
        + get_memory_string()
        + '\n User Input is what the user said to you. User Input: '
        + input_str
    )
    print(GPT_CONTENT)
    try:
        response = g4f.ChatCompletion.create(
            model=GPT.name,
            provider=g4f.Provider.GeekGpt,
            messages=[{"role": "user", "content": GPT_CONTENT}],
            stream=False,
        )
        return response
    except Exception as e:
        sleep(3)
        return generate_text(input_str)

@app.route('/generate_response', methods=['POST'])
def generate_response():
    data = request.json
    user_input = data.get('user_input', '')
    if not user_input:
        return jsonify({'error': 'User input not provided'}), 400

    response = generate_text(user_input)
    add_memory(f'User: {user_input}')

    return jsonify({'response': response})

@intents.event
async def on_ready():
    print(f'Logged in as {intents.user.name}')

@intents.event
async def on_message(message):
    if message.author == intents.user:
        return

    if intents.user.mentioned_in(message):
        print("Warning: ", message.content)
        removestr = f'<@{str(intents.user.id)}>'
        removedmention = str.strip(message.content, removestr)

        if removedmention == '':
            await message.reply("hi")
        else:
            memorytext = 'User: ' + removedmention

            MAIN_TEXT = generate_text(removedmention)
            print("GPT_RESPONSE: Finished")
            print(MAIN_TEXT)
            await message.reply(MAIN_TEXT)
            print("GPT_MEMORY: Saving Message...")
            add_memory(memorytext)
            print("GPT_MEMORY: FINISHED")

if __name__ == '__main__':
    intents.run('MTE3NzIzNzMyMDg0ODY0MjA3OA.GNrAGe.VOtxR4ZBHa8-LKDH_k9ZadooouaVp85xCWmVj8')  # Start the Discord bot in the background
    app.run(debug=True)  # Start the Flask web server
