import feedparser
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup as bs
import re
import fire
import sqlite3
from datetime import datetime

SERVER = 'http://localhost:1200'
ROUTERS = [
    '/zaobao/znews/china',
    '/thepaper/featured',
    '/ftchinese/simplified/hotstoryby7day',
    '/nytimes',
    '/bbc/chinese',
    '/caixin/article',
    '/wsj/zh-cn/opinion',
    '/yicai/headline',
    '/caijing/roll',
    '/cls/hot']

def create_db_and_table():
    db_path = Path('news.db')
    if not db_path.exists():
        conn = sqlite3.connect('news.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE feeds
                     (
                  agent TEXT,
                  title TEXT,
                  disc TEXT,
                  pubdate TEXT,
                  PRIMARY KEY (agent, title)
                  )''')
        conn.commit()
        conn.close()

def fmt_date(date_str):
    date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
    return date_obj.strftime('%Y%m%d')

def get_a_news(feed, n=0):
    # recieve a feed obj and a number
    d = feed.entries
    if n == 0:
        items = len(d)
    elif n < len(d):
        items = n
    else: items=len(d)

    agent = feed['feed'].title
    title_list = [t.title for t in d[:items]]
    disc = [de_tag(t.description) for t in d[:items]]
    pubdate = [fmt_date(t.published) for t in d[:items]]

    db_list = list(zip([agent]*len(title_list), title_list, disc, pubdate))
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.executemany('INSERT OR IGNORE INTO feeds VALUES (?,?,?,?)', db_list)
    conn.commit()
    conn.close()

    brief = f'## {feed.feed.title}\n\n' +'\n\n'.join(title_list)
    text = '\n\n'.join(disc)
    text = re.sub(r'\n{3,}', '\n\n', text)
    content = {
        # 'agent': agent,
        'text': text,
        'brief': brief
    }
    print(f'{feed["feed"].title} is ok!')
    return content

def pub_all(n=0):
    create_db_and_table()
    # make dir
    today = pd.Timestamp.today().strftime('%Y%m%d')
    dir = Path(f'./docs/{today}')
    if not dir.exists():
        dir.mkdir(parents=True)

    # publish one news and get out the brief
    brief = []
    for r in ROUTERS:
        f = feedparser.parse(SERVER+r)
        if not 'title' in f.feed:
            print(r +' failed!')
            continue
        content = get_a_news(f, n)
        brief.append(content['brief'])
        news_fn = f'{dir}/{f["feed"].title}.md'
        with open(news_fn, 'w', encoding='utf-8') as f:
            f.write(content['text'])

    # write brief file
    brief_fn = f'{dir}/index.md'
    position = 20309999-int(today)
    front_str = f'---\nsidebar_position: {position}\n---\n\n'
    with open(brief_fn, 'w', encoding='utf-8') as f:
        f.write(front_str)
        f.write(f'# {today} \n\n')
        f.write('\n\n'.join(brief))

    return 'published!'

def de_tag(text):
    soup = bs(text, 'html.parser')
    for img in soup(['img', 'figure']):
        img.decompose()
    text_with_newlines = soup.get_text('\n\n')

    tidy = [
        # (r' {2,}',' '),
        # (r'　', ''),
        # (r' ', ''),
        (r'\n','pppp'), # 保护住换行
        (r'\s', ''), # 去除空格及各种不可见字符        
        (r'([^。”p.])p{4,}', r'\1'), # 如果不是句号后有换行，也去掉，小标题可能会被有误杀。
        (r'p{4,}([。“])', r'\1'), # 句号前的换行去掉。
        # 去除各种括号中内容        
        (r'\(.*?\)', ''),
        (r'（.*?）', ''),
        (r'【.*?】', ''),
        (r'[<>]', '”'),
        (r'此文章为付费文章，会员请访问网站阅读。', ''),
        (r'请订阅或登录，以继续阅读全文！', ''),
        (r'图：.*?\n', '\n'),
        (r'p{4,}', '\n\n'),
    ]
    for pattern, repl in tidy:
        text_with_newlines = re.sub(pattern, repl, text_with_newlines)

    return text_with_newlines

if __name__ == '__main__':
    fire.Fire()