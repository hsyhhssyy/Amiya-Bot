import os
import re
import sys
import copy
import json
import time
import jieba
import jionlp
import shutil
import string
import random
import difflib
import pypinyin

from typing import List
from string import punctuation
from zhon.hanzi import punctuation as punctuation_cn
from amiyabot import PluginInstance


def all_match(text: str, items: list):
    for item in items:
        if item not in text:
            return False
    return True


def any_match(text: str, items: list):
    for item in items:
        if item in text:
            return item


def argv(name, formatter=str):
    key = f'--{name}'
    if key in sys.argv:
        index = sys.argv.index(key) + 1

        if index >= len(sys.argv):
            return True

        if sys.argv[index].startswith('--'):
            return True
        else:
            return formatter(sys.argv[index])


def char_seat(char):
    return 0.58 if 32 <= ord(char) <= 126 else 1


def check_file_content(text: str):
    if text and os.path.isfile(text):
        with open(text, mode='r', encoding='utf-8') as file:
            content = file.read()
        return content
    return text


def check_sentence_by_re(sentence: str, words: list, names: list):
    for item in words:
        for n in names:
            if re.search(re.compile(item % n if '%s' in item else item), sentence):
                return True
    return False


def chinese_to_digits(text: str):
    character_relation = {
        '零': 0,
        '一': 1,
        '二': 2,
        '两': 2,
        '三': 3,
        '四': 4,
        '五': 5,
        '六': 6,
        '七': 7,
        '八': 8,
        '九': 9,
        '十': 10,
        '百': 100,
        '千': 1000,
        '万': 10000,
        '亿': 100000000,
    }
    start_symbol = ['一', '二', '两', '三', '四', '五', '六', '七', '八', '九', '十']
    more_symbol = list(character_relation.keys())

    symbol_str = ''
    found = False

    def _digits(chinese: str):
        total = 0
        r = 1
        for i in range(len(chinese) - 1, -1, -1):
            val = character_relation[chinese[i]]
            if val >= 10 and i == 0:
                if val > r:
                    r = val
                    total = total + val
                else:
                    r = r * val
            elif val >= 10:
                if val > r:
                    r = val
                else:
                    r = r * val
            else:
                total = total + r * val
        return total

    for item in text:
        if item in start_symbol:
            if not found:
                found = True
            symbol_str += item
        else:
            if found:
                if item in more_symbol:
                    symbol_str += item
                    continue
                else:
                    digits = str(_digits(symbol_str))
                    text = text.replace(symbol_str, digits, 1)
                    symbol_str = ''
                    found = False

    if symbol_str:
        digits = str(_digits(symbol_str))
        text = text.replace(symbol_str, digits, 1)

    return text


def combine_dict(origin: dict, default: dict):
    for key in default.keys():
        if key not in origin:
            origin[key] = default[key]
        else:
            if type(default[key]) is dict:
                combine_dict(origin[key], default[key])
            elif default[key] is not None and not isinstance(origin[key], type(default[key])):
                origin[key] = default[key]

    return origin


def create_dir(path: str, is_file: bool = False):
    if is_file:
        path = os.path.dirname(path)

    if path and not os.path.exists(path):
        os.makedirs(path)

    return path


def create_test_data(data, path):
    with open(path, mode='w+', encoding='utf-8') as file:
        file.write('const testData = ' + json.dumps(data, ensure_ascii=False))


def cut_by_jieba(text):
    return jieba.lcut(text.lower().replace(' ', ''))


def cut_code(code, length):
    code_list = re.findall('.{' + str(length) + '}', code)
    code_list.append(code[(len(code_list) * length) :])
    res_list = []
    for n in code_list:
        if n != '':
            res_list.append(n)
    return res_list


def extract_time(text: str, to_time_point: bool = True):
    result = jionlp.ner.extract_time(text)
    if result:
        try:
            detail = result[0]['detail']

            if detail['type'] in ['time_span', 'time_point']:
                return [time.strptime(n, '%Y-%m-%d %H:%M:%S') for n in detail['time'] if n != 'inf']

            elif detail['type'] == 'time_delta':
                time_length = {
                    'year': 31536000,
                    'month': 2628000,
                    'day': 86400,
                    'hour': 3600,
                    'minute': 60,
                    'second': 1,
                }
                time_result = 0
                for k, v in time_length.items():
                    if k in detail['time']:
                        if to_time_point:
                            return [time.localtime(time.time() + detail['time'][k] * v)]
                        time_result += detail['time'][k] * v
                return time_result

            elif detail['type'] == 'time_period':
                pass

        except OSError:
            pass
    return []


def find_most_similar(text: str, text_list: list):
    res = find_similar_list(text, text_list)
    if res:
        return res[0]


def find_similar_list(text: str, text_list: list):
    result = {}
    for item in text_list:
        rate = float(difflib.SequenceMatcher(None, text, item).quick_ratio() * len([n for n in text if n in set(item)]))
        if rate > 0:
            if rate not in result:
                result[rate] = []
            result[rate].append(item)

    if result:
        return result[sorted(result.keys())[-1]]
    return []


def get_doc(func: PluginInstance):
    content = check_file_content(func.document)
    return f'# {func.name}\n\n{content}'


def get_index_from_text(text: str, array: list):
    r = re.search(r'(\d+)', text)
    if r:
        index = abs(int(r.group(1))) - 1
        if index >= len(array):
            index = len(array) - 1

        return index


def insert_empty(text, max_num, half=False):
    return '%s%s' % (text, ('　' if half else ' ') * (max_num - len(str(text))))


def integer(value):
    if type(value) is float and int(value) == value:
        value = int(value)
    return value


def is_all_chinese(text: List[str]):
    for word in text:
        for char in word:
            if not '\u4e00' <= char <= '\u9fff':
                return False
    return True


def is_contain_digit(text: str):
    return any(n.isdigit() for n in text)


def merge_dict(target: dict, source: dict):
    diff_dict = {}
    for key, value in source.items():
        if key not in target:
            diff_dict[key] = copy.deepcopy(value)
            continue

        if not isinstance(value, type(target[key])):
            target[key] = value

        if isinstance(value, dict):
            merge_dict(target[key], value)

    target.update(diff_dict)

    return target


def number_with_sign(number: int):
    if number >= 0:
        return '+' + str(number)
    return str(number)


def pascal_case_to_snake_case(camel_case: str):
    snake_case = re.sub(r'(?P<key>[A-Z])', r'_\g<key>', camel_case)
    return snake_case.lower().strip('_')


def random_code(length):
    pool = string.digits + string.ascii_letters
    code = ''
    for i in range(length):
        code += random.choice(pool)
    return code


def random_pop(items: list):
    return items.pop(random.randrange(0, len(items)))


def read_tail(path: str, lines: int = 1, _buffer: int = 4098):
    f = open(path, mode='r', encoding='utf-8')

    lines_found: List[str] = []
    block_counter = -1

    while len(lines_found) <= lines:
        try:
            f.seek(block_counter * _buffer, os.SEEK_END)
        except IOError:
            f.seek(0)
            lines_found = f.readlines()
            break

        lines_found = f.readlines()
        block_counter -= 1

    return lines_found[-lines:]


def remove_dir(path: str):
    if os.path.exists(path):
        shutil.rmtree(path)
    return path


def remove_punctuation(text: str, ignore: list = None):
    punc = punctuation + punctuation_cn
    if ignore:
        for i in ignore:
            punc = punc.replace(i, '')
    for i in punc:
        text = text.replace(i, '')
    return text


def remove_xml_tag(text: str):
    return re.compile(r'<[^>]+>', re.S).sub('', text)


def snake_case_to_pascal_case(snake_case: str):
    words = snake_case.split('_')
    return ''.join(word.title() if i > 0 else word.lower() for i, word in enumerate(words))


def sorted_dict(data: dict, *args, **kwargs):
    return {n: data[n] for n in sorted(data, *args, **kwargs)}


def text_to_pinyin(text: str):
    return ''.join([item[0] for item in pypinyin.pinyin(text, style=pypinyin.NORMAL)]).lower()


def get_resource_dir():
    absolute_path = os.path.abspath('./resource')
    return absolute_path


def get_plugin_dir():
    absolute_path = os.path.abspath('./plugins')
    return absolute_path
