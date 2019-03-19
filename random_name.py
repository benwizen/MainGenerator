import random


def rand_name():
    return ' '.join([name for name in map(lambda s: s[:-1], random.sample(name_words, 1))])


with open('./rand_words') as words:
    upper_words = [word for word in words if word[0].isupper()]
    name_words = [word for word in upper_words if not word.isupper()]
