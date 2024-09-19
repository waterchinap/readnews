import os
import random
import subprocess
import select
import sys
import time

import azure.cognitiveservices.speech as speechsdk
import akshare as ak
import feedparser
from gtts import gTTS
# import fire
# import numpy as np
import pandas as pd

def rss_news(n=50, voice=20):
    """
    use https://rss-source.com/ feeds
    以下三个网站的rss源比较规整，可以选择。
    """
    urls = {
        'BBC新闻' : 'http://www.bbc.co.uk/zhongwen/simp/index.xml',
        '纽约时报新闻' : 'https://cn.nytimes.com/rss.html',
        '界面新闻' : 'https://a.jiemian.com/index.php?m=article&a=rss'
    }
   
    for k, v in urls.items():
        d = feedparser.parse(v).entries
        if n > len(d):
            sel = d
        else:
            sel = d[:n] 
        item_list = ['第'+str(i+1)+'条、'+sel[i].title for i in range(len(sel))]

        text = k + '：'+'。'.join(item_list)

        # edge(text, voice) 
        play(text)

def tidy(df):
    sel = df.sort_index(ascending=False)
    sel = sel.loc[sel != ''].drop_duplicates()
    sel = ['第'+str(i+1)+'条、' for i in range(len(sel))] + sel
    text = '。'.join(sel)
    return text

def news(agent='em', n=100, voice=20):
    """
    播放最新的n条新闻
    em: 东方财富网
    cls: 财联社
    sina: 新浪财经
    ths: 同花顺
    """
    dfs = {
        'em' : ak.stock_info_global_em().iloc[:n,0],
        'cls' : ak.stock_info_global_cls(symbol="全部").iloc[:n,0],
        'sina' : ak.stock_info_global_sina().iloc[:,1],
        'ths' : ak.stock_info_global_ths().iloc[:,0]
    }
    text = tidy(dfs[agent])
    edge(text, voice)

def ak_news(voice=20, n=100):
    """
    play all aknews
    """
    dfs = {
        '东方财富：' : ak.stock_info_global_em().iloc[:n,0],
        '财联社：' : ak.stock_info_global_cls(symbol="全部").iloc[:n,1],
        '新浪财经：' : ak.stock_info_global_sina().iloc[:,1],
        '同花顺：' : ak.stock_info_global_ths().iloc[:,0]
    }
    for k, v in dfs.items():
        text = k + tidy(v)
        edge(text, voice)

def play(text):

    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    # The neural multilingual voice can speak different languages based on the input text.
    speech_config.SpeechSynthesisVoiceName = "zh-CN-XiaoxiaoMultilingualNeural"

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    # Get text from the console and synthesize to the default speaker.
    # print("Enter some text that you want to speak >")
    # text = input()

    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

def edge(text, voice=20):
    # text = tidy(df)
    V = [
        'zh-CN-XiaoxiaoNeural',
        'zh-CN-XiaoyiNeural',
        'zh-CN-YunjianNeural',
        'zh-CN-YunxiNeural',
        'zh-CN-YunxiaNeural',
        'zh-CN-YunyangNeural',
        'zh-CN-liaoning-XiaobeiNeural',
        'zh-TW-HsiaoChenNeural',
        'zh-TW-YunJheNeural',
    ]
    if voice > len(V):
        voice = random.randint(0, len(V)-1)
    subprocess.run(['edge-playback', '--voice', V[voice], '--text', text])

def test1():
    time.sleep(2)
    print('test1')

def test2():
    time.sleep(2)
    print('test2')

def main():
    while True:
        print('Enter a number in 10 sec:')
        print('1: ak_news')
        print('2: rss_news')
        choice = None
        ready, _, _ = select.select([sys.stdin], [], [], 10)
        if ready:
            choice = sys.stdin.readline().strip()

            try:
                if choice == '1':
                    ak_news()
                elif choice == '2':
                    rss_news()
                else:
                    print('invalid input')
            except KeyboardInterrupt:
                print('stop, exit.')
                exit()
        else:
            print(f'no input, exit.\n')
            sys.exit()

if __name__ == '__main__':
    main()