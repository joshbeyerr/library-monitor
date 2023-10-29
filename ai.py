import requests


def ask(content):
    api_key = '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'
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





#fake
# openai.api_key = api_key
#
# # Define a prompt
# prompt = "Translate the following English text to French: 'Hello, how are you?'"
#
# # Make an API call
# response = openai.Completion.create(
#     engine="davinci",  # You can choose a different engine if needed
#     prompt=prompt,
#     max_tokens=50  # Adjust as needed
# )

# Extract and print the AI's response
# ai_response = response.choices[0].text
# print(ai_response)