from django.shortcuts import render, redirect
from mainapp.forms import CityForm
import tweepy,json
import requests
from tweepy.streaming import StreamListener
from dotenv import load_dotenv
import os, json

load_dotenv()

access_token = os.getenv('access_token')
access_token_secret = os.getenv('access_token_secret')
consumer_key = os.getenv('consumer_key')
consumer_secret = os.getenv('consumer_secret')

# class TwitterStreamer():
#     def __init__(self):
#         pass

#     def stream_tweets(self, hash_tag_list):
#         listener = StdOutListener()
#         auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
#         auth.set_access_token(access_token,access_token_secret)
#         stream = tweepy.Stream(auth, listener)
#         stream.filter(track=['oxygen', 'remdesivir'])#hash_tag_list)

# class StdOutListener(StreamListener):
#     def on_data(self, data):
#         try:
#             data = json.loads(data)
#             print(data['text'])
#             return True
#         except BaseException as e:
#             print("Error on_data %s" % str(e))
#         return True
          

#     def on_error(self, status):
#         print(status)

def home_page(request):
    return render(request, 'mainapp/home.html', {'title': 'CovidAid - A helping hand to the help needers and providers'})

def need_help(request):
    return render(request, 'mainapp/need_help.html', {'title': 'Need help'})

# ========================================================================================================================
# tweet fetching starts here

bearer_token = 'AAAAAAAAAAAAAAAAAAAAAC6qPAEAAAAA1w9XBNXo9w5aQIvuevm7UXoSNPk%3DcASFZE4tZ3Ek4KrDYZQepIITB5qiDqEgkWDLhHjchBPTVAL4WJ'

def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def get_rules(headers, bearer_token):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", headers=headers
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(headers, bearer_token, rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))


def set_rules(headers, delete, bearer_token):
    # You can adjust the rules if needed
    sample_rules = [
        {"value": "covid has:images", "tag": "dog pictures"},
        {"value": "remdesivir has:images -grumpy", "tag": "cat pictures"},
    ]
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))


def get_stream(headers, set, bearer_token):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream", headers=headers, stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            print(json.dumps(json_response, indent=4, sort_keys=True))

def do_help(request):
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            req = form.cleaned_data.get('required_help')
            cityName = form.cleaned_data.get('city_name')
            return redirect('results', cityName, req)
    else:
        form = CityForm()
    context = {
        'form' : form,
        'title' : 'Do help'
    }
    return render(request, 'mainapp/do_help.html', context)

def need_help(request):
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            req = form.cleaned_data.get('required_help')
            cityName = form.cleaned_data.get('city_name')
            return redirect('results', cityName, req)
    else:
        form = CityForm()
    context = {
        'form' : form,
        'title' : 'Do help'
    }
    return render(request, 'mainapp/need_help.html', context)

def results(request, cityName, req):
    # req.append(cityName)
    # print(req)
    # req = req.strip('][').split(', ')
    # print(req)
    # twitter_streamer = TwitterStreamer()
    # twitter_streamer.stream_tweets(req)
    headers = create_headers(bearer_token)
    rules = get_rules(headers, bearer_token)
    delete = delete_all_rules(headers, bearer_token, rules)
    set = set_rules(headers, delete, bearer_token)
    get_stream(headers, set, bearer_token)
    return render(request, 'mainapp/results.html', {'city' : cityName, 'req' : req})