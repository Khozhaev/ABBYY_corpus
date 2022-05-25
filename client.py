import argparse
import json
import random

def load_shards(shards_count):
    res = []
    for i in range(shards_count):
        with open('shard{}.json'.format(i), 'r') as shard:
            s = json.JSONDecoder().decode(shard.read())
            res.append(s)
    return res


class EventLoop:
    def __init__(self, shards, need_lemmatize, need_depends, need_speech_parts, any_form):
        self.shards = shards
        self.shards_count = len(self.shards)
        self.max_ans = 15
        self.need_lemmatize = need_lemmatize
        self.need_depends = need_depends
        self.need_speech_parts = need_speech_parts
        self.any_form = any_form
        if self.need_speech_parts:
            self.need_lemmatize = True


    def process_shard(self, id, word):
        shard = self.shards[id]
        index = shard['inverted_index']
        articles = shard['articles']
        if not self.any_form:
            if word not in index:
                return []
            docs = index[word]
            result = []
            for doc in docs:
                res = dict()
                article_id, sentence_id = doc[0], doc[1]
                res['article_id'] = article_id
                res['sentence_id'] = sentence_id
                article = articles[article_id]
                sentence = article['sentences'][sentence_id]
                res['article'] = article
                res['sentence'] = sentence
                result.append(res)
            return result
        result = []

        for article in articles:
            for sentence in article['sentences']:
                for token in sentence['tokens']:
                    if token['word'] == word:
                        res = dict()
                        res['article'] = article
                        res['sentence'] = sentence
                        result.append(res)
        return result



    def process_responses(self, word, responses):
        answers = []
        for response in responses:
            ans = '==========================================================================\n'
            #print('debug, resp={}'.format(response))
            sentence = response['sentence']
            article = response['article']
            #print('debug, sentence={}'.format(sentence))
            ans += 'original sentence: {}'.format(sentence['original'])
            ans += '\n'
            ans += 'source:{}'.format(article['ref'])
            ans += '\n'
            ans += 'article title: {}'.format(article['title'])
            ans += '\n'
            flag = True
            if self.need_lemmatize and not self.need_speech_parts:
                lemms = []
                for token in sentence['tokens']:
                    lemms.append(token['normal_form'])
                ans += 'lemmatized:{}'.format(str(lemms))
                ans += '\n'
            if self.need_speech_parts:
                lemms = []
                for token in sentence['tokens']:
                    lemms.append((token['normal_form'], token['speech_part']))
                    if token['word'] != word and token['normal_form'] == word:
                        flag = False
                ans += 'lemmatized:{}'.format(str(lemms))
                ans += '\n'
            if self.need_depends:
                id_to_word = dict()
                for token in sentence['tokens']:
                    id_to_word[int(token['id'])] = token['word']
                id_to_word[0] = 'root'
                for token in sentence['tokens']:
                    ans += token['word']
                    ans += ' ->depends from-> '
                    ans += id_to_word[int(token['head'])]
                    ans += '\n'
            if True:  # for debug
             answers.append(ans)
        answers.append('========================================================================\n')
        return ''.join(answers)

    def process_request(self, command):
        if not command.isalpha():
            return 'invalid request'
        responses = []
        for i in range(self.shards_count):
            res = self.process_shard(i, command)
            for resp in res:
                responses.append(resp)
        random.shuffle(responses)
        responses = responses[0:min(200, len(responses), self.max_ans)]
        return self.process_responses(command, responses)

    def run_loop(self):
        while True:
            cmd = input('enter the word\n')
            if cmd == 'exit':
                return 0
            print('your word={}'.format(cmd))
            print(self.process_request(cmd))


def __main__():
    parser = argparse.ArgumentParser(description='Build index.')
    parser.add_argument('--lemmatize', action='store_true')
    parser.add_argument('--depends', dest='depends', action='store_true')
    parser.add_argument('--speech-parts', dest='speech_parts', action='store_true')
    parser.add_argument('--any-form', dest='any', action='store_true')
    #parser.add_argument('--shards-count', dest='shards_count', action='store')
    args = parser.parse_args()
    #shards_cnt = int(args.shards_count)
    #shard_num = int(args.ID)
    print('Processing shards...')
    shards = load_shards(5)
    print('Shards load success')
    event_loop = EventLoop(shards, args.lemmatize, args.depends, args.speech_parts, args.any)
    event_loop.run_loop()


if __name__ == '__main__':
    __main__()