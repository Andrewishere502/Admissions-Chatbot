import requests


def translate(lang_from, content, lang_to):
    if lang_from == lang_to:
        return content
    url = "https://translated-mymemory---translation-memory.p.rapidapi.com/api/get"

    querystring = {"mt":"1","onlyprivate":"0","langpair": "|".join((lang_from, lang_to)),"q":content}

    headers = {
        'x-rapidapi-host': "translated-mymemory---translation-memory.p.rapidapi.com",
        'x-rapidapi-key': "123c79a176msh0bf66792293477cp1052d6jsn272977deea20"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    translated_content = response.text
    translated_content = translated_content.split("translatedText\":\"")
    translated_content = translated_content[1]
    translated_content = translated_content.split("\",\"match")
    translated_content = translated_content[0]
    return translated_content


def microsoft_translate(lang_from, content, lang_to):
    if lang_from == lang_to:
        return content
    url = "https://microsoft-translator-text.p.rapidapi.com/translate"

    querystring = {"from": lang_from,
                   "profanityAction": "NoAction",
                   "textType": "plain",
                   "to": lang_to,
                   "api-version": "3.0"
                    }
    body = [
        {"text": content}
        ]

    headers = {
        'x-rapidapi-host': "microsoft-translator-text.p.rapidapi.com",
        'x-rapidapi-key': "123c79a176msh0bf66792293477cp1052d6jsn272977deea20",
        'content-type': "application/json",
        }

    response = requests.post(url, headers=headers, params=querystring, json=body)
    translated_message = response.json()[0]["translations"][0]["text"]
    return translated_message


if __name__ == "__main__":
    print(translate("en", "Hello, how are you?", "es"))
    # print(translate("en", "Hello, how are you?", "es").encode("utf-8").decode("utf-8"))

    # print(microsoft_translate("en", "Hello, how are you?", "es").encode("utf-8").decode("utf-8"))
