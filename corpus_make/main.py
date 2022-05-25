import requests
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import json
import os


def get_article_by_ref(ref):
    response = requests.get(ref)
    soup = BeautifulSoup(response.content, 'lxml')
    res = dict()
    if response.status_code != 200:
        print('alarm', response.status_code)
        print(response)
        print(response.headers)
        print(response.content)
        print(ref)
        os.system('sleep 1')
        return None
    res['title'] = soup.find(class_="tm-article-snippet__title").get_text()
    res['content'] = soup.find(id='post-content-body').get_text()
    return res


def get_all_articles(url_prefix, pages_count=4):
    result = []
    iteration = 0
    for id_page in range(1, pages_count + 1):
        iteration += 1
        url = url_prefix + '/page' + str(id_page) + '/'
        response = requests.get(url)
        if response.status_code != 200:
            print("ALARM, ", response.status_code)
            print(response.content)
            print(response.headers)
            print(response.status_code)
            continue
        soup = BeautifulSoup(response.content, 'lxml')
        articles = soup.find_all(class_='tm-articles-list__item')
        for article in articles:
            snippets = article.find_all('a', class_='tm-article-snippet__title-link')
            if len(snippets) != 1:
                print(len(snippets), article)
                continue
            assert len(snippets) == 1
            snippet = snippets[0]
            id_state = article['id']
            res = dict()
            res['id'] = id_state
            res['page'] = url
            res['ref'] = 'https://habr.com' + snippet['href']
            result.append(res)
        if iteration % 5 == 0:
            os.system('sleep 1')
        if iteration % 10 == 0:
            print("processed=", iteration)

    return result


def get_articles_refs(filename):
    if not os.path.exists(filename):
        articles = get_all_articles('https://habr.com/ru/flows/popsci', 1000)
        print(len(articles))
        with open(filename, 'w+') as file:
            json.dump(articles, file)
        return articles
    with open(filename) as file:
        res = json.JSONDecoder().decode(file.read())
        return res


def load():
    filename = 'articles_content.json'
    articles = get_articles_refs('articles_refs_list.json')
    res = []
    iteration = 0
    for article in articles:
        iteration += 1
        tmp = get_article_by_ref(article['ref'])
        if tmp is None:
            continue
        article['title'] = tmp['title']
        article['content'] = tmp['content']
        res.append(article)
        if iteration % 30 == 0:
            print("iteration={}".format(iteration))
            os.system('sleep 1')
    with open(filename, 'w+') as file:
        json.dump(res, file)


def __main__():
    articles = []
    with open('articles_content.json', 'r') as file:
        articles = json.JSONDecoder().decode(file.read())
    sum = 0
    iter = 0
    for article in articles:
        iter += 1
        sum += len(article['content'])
        if iter % 100 == 0:
            print('iter={}, sum={}, avg={}'.format(iter, sum, (sum / iter)))



if __name__ == '__main__':
    __main__()

