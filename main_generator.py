import re
import string
import json
from jsonStepper import json_navigator
from random_name import rand_name
from collections import Counter, defaultdict
from random import *
from functools import reduce


def parse_header(header_path, req_amount):
    with open(header_path) as f:
        methods = []
        members = []
        ctors = []
        class_json = {}
        class_name = ''
        class_json['ctors'] = ctors
        class_json['members'] = members
        class_json['methods'] = methods
        class_json['req_amount'] = req_amount

        lines = f.read().split('\n')
        for line in lines:
            # Class name
            if re.match(r'class\s+(\w+)', line):
                class_name = line.split(' ')[1]
            # Members
            members += extract(r'\s+(?P<type>\w+)\s+(?P<name>\w+)(?P<arr_size>(\[\d+\])*);', line, False)
            # Ctors
            ctors += extract(rf'\s+{class_name}(\((?P<args_str>([^\)]*)))\)', line, True)
            # Methods and setters
            methods += extract(r'\s+(?P<ret_type>\w+) (?P<name>\w+)(\((?P<args_str>.*)\));', line, True)

    return class_name, class_json


def extract(regex_pattern, in_str, is_func):
    if re.match(regex_pattern, in_str):
        m = re.search(regex_pattern, in_str)
        matches = m.groupdict()
        if is_func:
            args_comma_sep = list(filter(None, [x.strip() for x in matches['args_str'].split(',')]))
            matches['args_required'] = len(args_comma_sep)
            args = []
            for a in args_comma_sep:
                arg = {}
                arg_split = a.split()
                if arg_split[0] == 'const':
                    arg_split.pop(0)
                arg['type'] = arg_split[0].replace('&', '')
                arg['name'] = arg_split[1]
                if arg_split[1].find('[') > -1 or arg_split[1].find('*') > -1:
                    arg['is_arr'] = True
                else:
                    arg['is_arr'] = False
                args.append(arg)
            matches['args'] = args
        return [matches]
    return []


def array_generator(arr_type, arr_len):
    arr_str = '{'
    for _ in range(arr_len):
        arr_str += f'{random_value_gen(arr_type)}, '
    arr_str = arr_str.rstrip(', ')
    arr_str += '}'
    return arr_str


class UnregisteredType(Exception):
    """ Exception class for unregistered type.
        Type needs to be added to bi_types in functions """
    def __init__(self, message):
        super().__init__(message)


def random_value_gen(cpp_type):
    try:
        if cpp_type == 'int':
            return randint(1, 100)
        elif cpp_type == 'float' or cpp_type == 'double':
            return round(uniform(1, 10), 2)
        elif cpp_type == 'char':
            return random.choice(string.ascii_letters)
        elif cpp_type == 'char*' or cpp_type == 'string':
            return rand_name()
        else:
            raise UnregisteredType("Unknown type in random_value_gen")
    except UnregisteredType as e:
        print(e)


def arg_gen(arg, obj_id, obj_number, pre_objs):
    arg_str = ""
    bi_types = ['int', 'int*', 'bool', 'char', 'char*', 'double', 'float']
    m_type = arg['type']
    is_arr = arg['is_arr']
    if m_type not in bi_types:
        for idx, po in enumerate(pre_objs):
            if m_type == po['class']:
                arg_str += po['obj_id']
                arg_str += ", "
                pre_objs.pop(idx)
                break
    elif is_arr:
        m = re.search(r'(\[\d+\])+', arg['name'])
        if m:
            arr_size = m.group()
        else:
            arr_size = 5
        arr_len = reduce(lambda a, b: int(a) * int(b), re.findall(r'\d', arr_size))
        arg_name = re.sub(r'\[\d+\]', '', arg['name'])
        arg_name += f"_{obj_id[0]}_{obj_number}"
        arr = f"{arg['type']} {arg_name}{arr_size} = {array_generator('int', int(arr_len))};\n"
        arg_str = arr + arg_str + f"{arg_name}, "
    else:
        rnd = random_value_gen(m_type)
        arg_str += str(rnd)
        arg_str += ", "
    return arg_str


def generate_objects(class_name, cjson, pre_objs, count=5):
    str_objs = ""
    objs = []
    rel_ctor = None

    for ctor in cjson['ctors']:
        if ctor['args_required'] > 0:
            rel_ctor = ctor
            break

    for obj_number in range(1, count+1):
        args_required = int(json_navigator('/args_required', rel_ctor))
        obj_id = f'{class_name.lower()}{obj_number}'
        objs.append({'class': class_name, 'obj_id': obj_id})
        obj_str = f"{class_name} {obj_id}("
        for arg_id in range(args_required):
            arg = json_navigator(f'/args/{arg_id}', rel_ctor)
            obj_str += arg_gen(arg, obj_id, obj_number, pre_objs)
        obj_str = obj_str.rstrip(', ') + ");"
        str_objs += obj_str + "\n"
    return str_objs, objs


def classes_json_gen(headers_list):
    classes = {}
    for class_header, amount in headers_list.items():
        class_name, cjson = parse_header(class_header, amount)
        classes[class_name] = cjson
    return classes


def prerequisite_objs(cjson):
    bi_types = ['int', 'bool', 'char', 'char*', 'double', 'float']
    for ctor in cjson['ctors']:
        if ctor['args_required'] > 0:
            break
    return Counter(t['type'] for t in ctor['args'] if t['type'] not in bi_types)


def prereq_for_classes(cls_json):
    final_cnt = Counter()
    for cls in cls_json:
        req_amount = json_navigator(f'/{cls}/req_amount', cls_json)
        if req_amount < 1:
            req_amount = 1
        final_cnt.update(prerequisite_objs(cls_json[cls]))
    prereq_dict = {k: v * req_amount for k, v in final_cnt.items()}
    return prereq_dict


def check_cls_depth(cls_json, class_name):
    bi_types = ['int', 'int*', 'bool', 'char', 'char*', 'double', 'float']
    cls = cls_json[class_name]
    for ctor in cls['ctors']:
        if ctor['args_required'] > 0:
            rel_ctor = ctor
            break

    ctor_args = rel_ctor['args']
    types = set(t['type'] for t in ctor_args)
    comp_types = []
    max_depth = 0
    for t in types:
        if t not in bi_types:
            comp_types.append(t)
    for t in comp_types:
        max_depth = max(max_depth, check_cls_depth(cls_json, t))
    return max_depth + 1


def check_depths(cls_json):
    depths = defaultdict(list)
    for cls_name in cls_json.keys():
        depth = check_cls_depth(cls_json, cls_name)
        depths[depth] += [cls_name]
    return depths


def main_generator(paths):
    final_str = ""
    pre_objs = []
    total_cls_json = classes_json_gen(paths)
    # print(json.dumps(total_cls_json, indent=3))
    depths = check_depths(total_cls_json)
    prereq = prereq_for_classes(total_cls_json)
    for depth in range(1, max(depths.keys()) + 1):
        for cls in depths[depth]:
            if cls not in prereq:
                prereq[cls] = 1
            objs_str, objs = generate_objects(cls,
                                              total_cls_json[cls],
                                              pre_objs,
                                              max(prereq[cls],
                                                  json_navigator(f'/{cls}/req_amount', total_cls_json)))
            pre_objs += objs
            final_str += objs_str
    return final_str


if __name__ == '__main__':

    headers = {r'.\cpp_headers\Point.h': 2,
               r'.\cpp_headers\Line.h': 2,
               r'.\cpp_headers\Triangle.h': 2}

    # main_generator(headers)
    print(main_generator(headers))
