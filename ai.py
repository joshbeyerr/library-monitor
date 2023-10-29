import requests

# ignore, just a fun ai file

def ask(content):
    api_key = ''
    api_url = 'https://api.openai.com/v1/chat/completions'
    s = requests.session()

    s.headers.update({
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(api_key)
    })

    data = {
         "model": "gpt-3.5-turbo",
         "messages": [
             {"role": "user", "content": "{}".format(content)}
            ],
         "temperature": 2
       }

    thing = (s.post(api_url, json=data)).json()

    print(thing)
    quit()

    return thing['choices'][0]['message']['content']


inpt = input()
ask(inpt)



