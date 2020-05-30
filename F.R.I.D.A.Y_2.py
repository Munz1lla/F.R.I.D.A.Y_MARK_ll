from google import google
import boto3
import speech_recognition as sr
import os
from playsound import playsound
import webbrowser
import random

speech = sr.Recognizer()

greeting_dict = {'hello ': 'hello', 'hi': 'hi'}
open_launch_dict = {'open': 'open', 'launch': 'launch'}
google_searches_dict = {'what': 'what', 'why': 'why', 'who': 'who', 'where': 'where', 'which': 'which', 'when': 'when'}
social_media_dict = {'facebook': 'https://www.facebook.com', 'youtube': 'https://www.youtube.com'}
thank_you_dict = {'thank you': 'thank you', 'thanks': 'thanks'}

mp3_thankyou_list = ['mp3/friday/thankyou_1.mp3', 'mp3/friday/thankyou_2.mp3']
mp3_listening_problem_list = ['mp3/friday/Listening_problem_1.mp3', 'mp3/friday/Listening_problem_2.mp3']
mp3_struggling_list = ['mp3/friday/struggling_1.mp3']
mp3_google_search = ['mp3/friday/google_search_1.mp3', 'mp3/friday/google_search_3.mp3']
mp3_greeting_list = ['mp3/friday/greeting_2.mp3', 'mp3/friday/greeting_3.mp3']
mp3_open_launch_list = ['mp3/friday/open_1.mp3', 'mp3/friday/open_2.mp3', 'mp3/friday/open_3.mp3']

error_occurrence = 0
counter = 0

polly = boto3.client('polly')

def play_sound_from_polly(result):
    global counter
    mp3_name = 'output.mp3'.format(counter)
    obj = polly.synthesize_speech(Text=result, OutputFormat='mp3', VoiceId='Emma')
    with open(mp3_name, 'wb') as file:
        file.write(obj['AudioStream'].read())
        file.close()
    playsound(mp3_name)
    os.remove(mp3_name)
    counter+=1


def google_search_result(query):
    search_result = google.search(query)
    print(search_result)
    for result in search_result:
        print(result.description.replace('...', '').rsplit('.', 3)[0])
        play_sound_from_polly(result.description.replace('...', '').rsplit('.', 3)[0])
        break


def is_valid_google_search(phrase):
    if google_searches_dict.get(phrase.split(' ')[0]) == phrase.split(' ')[0]:
        return True

def play_sound(mp3_list):
    mp3 = random.choice(mp3_list)
    playsound(mp3)

def read_voice_cmd():
    voice_text = ''
    print('Listening...')

    global error_occurrence

    try:
        with sr.Microphone() as source:
            audio = speech.listen(source=source, timeout=10, phrase_time_limit=5)
        voice_text = speech.recognize_google(audio)
    except sr.UnknownValueError:
        if error_occurrence == 0:
            play_sound(mp3_listening_problem_list)
            error_occurrence += 1
        elif error_occurrence == 1:
            play_sound(mp3_struggling_list)
            error_occurrence += 1


    except sr.RequestError as e:
        print('Network Error.')
    except sr.WaitTimeoutError:
        if error_occurrence == 0:
            play_sound(mp3_listening_problem_list)
            error_occurrence += 1
        elif error_occurrence == 1:
            play_sound(mp3_struggling_list)
            error_occurrence += 1

    return voice_text

def is_valid_note(greeting_dict, voice_note):
    for key, value in greeting_dict.iteritems():
        # 'Hello Friday'
        try:
            if value == voice_note.split(' ')[0]:
                return True
                break
            elif key == voice_note.split(' ')[1]:
                return True
                break
        except IndexError:
            pass

    return False




if __name__ == '__main__':

    playsound('mp3/friday/beginning_greeting.mp3')

    while True:

        voice_note = read_voice_cmd().lower()
        print('cmd : {}'.format(voice_note))

        if is_valid_note(greeting_dict, voice_note):
            print('In greeting...')
            play_sound(mp3_greeting_list)
            continue
        elif is_valid_note(open_launch_dict, voice_note):
            print('In open...')
            play_sound(mp3_open_launch_list)
            if(is_valid_note(social_media_dict, voice_note)):
                # Launch Facebook
                key = voice_note.split(' ')[1]
                webbrowser.open(social_media_dict.get(key))
            else:
                os.system('explorer C:\\"{}"'.format(voice_note.replace('Open ', '').replace('Launch ', '')))
            continue
        elif is_valid_google_search(voice_note):
            print('In google search...')
            play_sound(mp3_google_search)
            webbrowser.open('https://www.google.com/search?q={}'.format(voice_note))
            google_search_result(voice_note)
            continue
        elif 'thank you' in voice_note:
            play_sound(mp3_thankyou_list)
            continue
        elif 'goodbye' in voice_note:
            playsound('mp3/friday/bye.mp3')
            exit()
