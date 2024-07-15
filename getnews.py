import feedparser
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup as bs
import re

def readnews():
    routers = [
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
    for i in range(len(routers)):
        print(f'{i}: {routers[i]}')
    n = int(input('请输入一个数字: '))
    if n > len(routers)-1:
        print('数字超出列表长度')
        exit()
    else:
        df = get_content('http://localhost:1200'+routers[n])

        return df    

def get_content(url, n=10):
    f = feedparser.parse(url)
    d = f.entries
    if len(d) < n:
        n = len(d)
    text = '\n\n'.join(
        [f'## {t.title}\n\n{de_tag(t.description)}' for t in d[:n]]
    )
    text = re.sub(r'\n{3,}', '\n\n', text)
    content = {
        'agent': f['feed'].title,
        'text': text
    }
    return content

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
    # replace 2 and more space with 1 space 
    # replace 1 space end with enter with enter

    
    return text_with_newlines

def md_file(df):
    # for each item text_list, i want to create a file and put it in a folder in the name of today's date
    # and the file name is the title of the item
    # and the file content is the description of the item
    # get today date string
    today = pd.Timestamp.today().strftime('%Y%m%d')
    dir = Path(f'./docs/{today}')
    if not dir.exists():
        dir.mkdir(parents=True)
    # write index.md
    position = 20309999-int(today)
    front_str = f'---\nsidebar_position: {position}\n---\n\n'
    index_fn = f'{dir}/index.md'
    with open(index_fn, 'w', encoding='utf-8') as f:
        f.write(front_str)
        f.write(f'# {today}')

    # write content file
    agent = df['agent']
    file_name = f'{dir}/{agent}.md'
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(df['text'])

if __name__ == '__main__':
    df = readnews()
    md_file(df)