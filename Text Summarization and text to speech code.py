import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
from openai import OpenAI

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

# Check the key

if not api_key:
    print("No API key was found")
elif not api_key.startswith("sk-proj-"):
    print("An API key was found, but it doesn't start sk-proj-; please check you're using the right key")
elif api_key.strip() != api_key:
    print("An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them")
else:
    print("API key found successfully")
	

openai = OpenAI()

headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

class Website:        
    def __init__(self, url):

        self.url = url
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            self.title = soup.title.string if soup.title else "No title found"
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            print(f"Website {url} not found.")
            return False
			

website_name = input("Enter the website :\n")
ed = Website(website_name)
print(ed.title)
print(ed.text)

system_prompt = "You are an assistant that analyzes the contents of a website \
and provides a short summary, ignoring text that might be navigation related. \
Respond in markdown."

def user_prompt_for(website):
    user_prompt = f"You are looking at a website titled {website.title}"
    user_prompt += "\nThe contents of this website is as follows; \
please provide a short summary of this website in markdown. \
If it includes news or announcements, then summarize these too.\n\n"
    user_prompt += website.text
    return user_prompt


def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)}
    ]


def summarize(url):
    website = Website(url)
    response = openai.chat.completions.create(
        model = "gpt-4o-mini",
        messages = messages_for(website)
    )
    return response.choices[0].message.content
	

def display_summary(url):
    summary = summarize(url)
    display(Markdown(summary))
    
def summaryToSpeech(url):
    summary = summarize(url)
    return summary
    
weblink = input("Enter the website link : \n")
#weblink = "https://link.springer.com/article/10.1007/s10462-025-11352-1?_gl=1*q0ftrr*_up*MQ..*_gs*MQ..&gclid=Cj0KCQjw8p7GBhCjARIsAEhghZ2IqP0J3uQpGh-grkHXi2VPmsya2I7XEdMdwAiUHyLziO5fZbQVF2saAss6EALw_wcB&gbraid=0AAAAApIS33vt_gc51HIIRLGzgVu-4iDi4"
display_summary(weblink)

import base64
from io import BytesIO
from IPython.display import Audio, display

def talker(message):
    response = openai.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=message)

    audio_stream = BytesIO(response.content)
    output_filename = "output_audio.mp3"
    with open(output_filename, "wb") as f:
        f.write(audio_stream.read())

    # Play the generated audio
    display(Audio(output_filename, autoplay=True))
    
weblink = "https://link.springer.com/article/10.1007/s10462-025-11352-1?_gl=1*q0ftrr*_up*MQ..*_gs*MQ..&gclid=Cj0KCQjw8p7GBhCjARIsAEhghZ2IqP0J3uQpGh-grkHXi2VPmsya2I7XEdMdwAiUHyLziO5fZbQVF2saAss6EALw_wcB&gbraid=0AAAAApIS33vt_gc51HIIRLGzgVu-4iDi4"
tts = summaryToSpeech(weblink)
talker(tts)
