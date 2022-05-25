import stanza
import json
import time
import argparse
import sys


def load(filename):
    with open(filename, 'r') as file:
        return json.JSONDecoder().decode(file.read())


def build_inverted_index(articles, proc_id):
    article_num = -1
    index = dict()
    print('starting build index by {:d}', proc_id, file=sys.stderr)
    for article in articles:
        article_num += 1
        sentence_num = -1
        for sentence in article['sentences']:
            sentence_num += 1
            for word in sentence['tokens']:
                v = word['normal_form']
                if v not in index:
                    index[v] = []
                index[v].append((article_num, sentence_num))
        print('indexed {:d} articles by {:d}'.format(article_num, proc_id), file=sys.stderr)
    return index


def process(articles, proc_id):
    ppln = stanza.Pipeline('ru', processors='tokenize,pos,lemma,depparse')
    iter = 0
    print('starting process articles by {:d}'.format(proc_id), file=sys.stderr)
    for article in articles:
        iter += 1
        doc = ppln(article['content'])
        sentences = []
        for i, dsentence in enumerate(doc.sentences):
            original_sentence = ''
            sentence = dict()
            sentence['tokens'] = []
            is_first = True
            for word in dsentence.words:
                token = dict()
                if not is_first:
                    original_sentence += ' '
                is_first = False
                original_sentence += word.text
                token['word'] = word.text
                token['normal_form'] = word.lemma
                token['speech_part'] = word.upos
                token['id'] = word.id
                token['head'] = word.head
                token['deprel'] = word.deprel
                token['feats'] = word.feats
                sentence['tokens'].append(token)
            sentence['original'] = original_sentence
            sentences.append(sentence)
        article['sentences'] = sentences
        del article['content']
        print('processed {:d} articles by {:d}'.format(iter, proc_id), file=sys.stderr)
    inverted_index = build_inverted_index(articles, proc_id)
    return (articles, inverted_index)


def __main__():
    parser = argparse.ArgumentParser(description='Build index.')
    parser.add_argument('--id', dest='ID', action='store')
    parser.add_argument('--shards-count', dest='shards_count', action='store')
    args = parser.parse_args()
    shards_cnt = int(args.shards_count)
    shard_num = int(args.ID)
    print('start by {:d}'.format(shard_num), file=sys.stderr)

    articles = load('articles_content.json')
    #articles_by_shard_count = (len(articles) + shards_cnt - 1) // shards_cnt
    articles_by_shard_count = 100
    left = shard_num * articles_by_shard_count
    right = min(left + articles_by_shard_count, len(articles))
    output_shard_filename = 'shard' + str(shard_num) + '.json'
    print(left, right, len(articles), output_shard_filename, file=sys.stderr)

    articles, index = process(articles[left:right], shard_num)
    result = dict()
    result['articles'] = articles
    result['inverted_index'] = index

    with open(output_shard_filename, 'w+') as file:
        json.dump(result, file)


__main__()
