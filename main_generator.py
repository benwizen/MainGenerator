import re
import json
import string
from jsonStepper import json_navigator
from random_name import rand_name
from collections import Counter
from random import *


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

        word_l = f.read().split('\n')
        for s in word_l:
            # Class name
            if re.match('class\s(\w+)', s):
                class_name = s.split(' ')[1]
            # Members
            extract(members, '\\t(?P<type>\w+)\s+(?P<name>\w+);', s, False)
            # Ctors
            extract(ctors, '\\t(?P<ctor>\w+)(\((?P<args_str>.*)\));', s, True)
            # Methods and setters
            extract(methods, '\\t(?P<ret_type>\w+) (?P<name>\w+)(\((?P<args_str>.*)\));', s, True)

    return class_name, class_json


def extract(out, regex_pattern, string, has_args):
    if re.match(regex_pattern, string):
        m = re.search(regex_pattern, string)
        dict = m.groupdict()
        if has_args:
            args_comma_sep = list(filter(None, [x.strip() for x in dict['args_str'].split(',')]))
            dict['args_required'] = len(args_comma_sep)
            args = []
            for a in args_comma_sep:
                arg = {}
                arg_split = a.split()
                if arg_split[0] == 'const':
                    arg_split.pop(0)
                arg['type'] = arg_split[0].replace('&', '')
                arg['name'] = arg_split[1]
                args.append(arg)
            dict['args'] = args
        out.append(dict)


def random_value_gen(type):
    try:
        if type == 'int':
            return randint(1, 100)
        elif type == 'float' or type == 'double':
            return round(uniform(1, 10), 2)
        elif type == 'char':
            return random.choice(string.ascii_letters)
        elif type == 'char*':
            return rand_name()
        else:
            raise Exception("Unknown type in random_value_gen")
    except Exception as e:
        print(e)


def generate_objects(class_name, cjson, pre_objs, count=5):
    bi_types = ['int', 'bool', 'char', 'char*', 'double', 'float']
    str_objs = ""
    objs = []
    rel_ctor = None

    for ctor in cjson['ctors']:
        if ctor['args_required'] > 0:
            rel_ctor = ctor
            break

    for obj_id in range(count):
        args_required = int(json_navigator('/args_required', rel_ctor))
        obj_id = f'{class_name.lower()}{obj_id + 1}'
        objs.append({'class': class_name, 'obj_id': obj_id})
        obj_str = f"{class_name} {obj_id}("
        for arg_id in range(args_required):
            m_type = json_navigator(f'/args/{arg_id}/type', rel_ctor)
            if m_type not in bi_types:
                for idx, po in enumerate(pre_objs):
                    if m_type == po['class']:
                        obj_str += po['obj_id']
                        if arg_id != args_required - 1:
                            obj_str += ", "
                        pre_objs.pop(idx)
                        break
            else:
                rnd = random_value_gen(m_type)
                obj_str += str(rnd)
                if arg_id != args_required - 1:
                    obj_str += ", "
        obj_str += ");"
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
    prereq_dict = {}
    for cls in cls_json:
        req_amount = json_navigator(f'/{cls}/req_amount', cls_json)
        if req_amount < 1: req_amount = 1
        for k, v in prerequisite_objs(cls_json[cls]).items():
            if k in prereq_dict.keys():
                prereq_dict[k] += v * req_amount
            else:
                prereq_dict[k] = v * req_amount
    return prereq_dict


def check_cls_depth(cls_json, class_name):
    bi_types = ['int', 'bool', 'char', 'char*', 'double', 'float']
    cls = cls_json[class_name]
    for ctor in cls['ctors']:
        if ctor['args_required'] > 0:
            break

    ctor_args = ctor['args']
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
    depths = {}
    for cls_name in cls_json.keys():
        depth = check_cls_depth(cls_json, cls_name)
        if depth in depths.keys():
            depths[depth] += [cls_name]
        else:
            depths[depth] = [cls_name]
    return depths


def main_generator(paths):
    final_str = ""
    pre_objs = []
    total_cls_json = classes_json_gen(paths)
    depths = check_depths(total_cls_json)
    prereq = prereq_for_classes(total_cls_json)
    for depth in range(1, max(depths.keys()) + 1):
        for cls in depths[depth]:
            if cls not in prereq: prereq[cls] = 1
            objs_str, objs = generate_objects(cls,
                                              total_cls_json[cls],
                                              pre_objs,
                                              max(prereq[cls],
                                                  json_navigator(f'/{cls}/req_amount', total_cls_json)))
        pre_objs += objs
        final_str += objs_str
    return final_str


if __name__ == '__main__':
    paths = {r'C:\Users\User\Desktop\CPP\Ex2\T2\T2\Point.h': 10,
             r'C:\Users\User\Desktop\CPP\Ex2\T2\T2\Line.h': 3,
             r'C:\Users\User\Desktop\CPP\Ex2\T2\T2\Triangle.h': 3}

    print(main_generator(paths))
