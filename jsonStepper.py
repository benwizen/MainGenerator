import json
from functools import reduce
import operator
import timeit


def json_navigator(path, my_json):
    data = json.loads(json.dumps(my_json))
    paths = path.split('/')
    paths.pop(0)
    for p in paths:
        if p.isdigit(): p = int(p)
        data = data[p]
    return data


def json_navigator_reduced(path, my_json):
    try:
        data = json.loads(my_json)
        # paths = list(map(lambda x: int(x) if x.isdigit() else x, (filter(None, path.split('/')))))
        paths = [int(p) if p.isdigit() else p for p in (filter(None, path.split('/')))]
        return reduce(operator.getitem, paths, data)
    except IndexError as e:
        print(f"Index - {str(e)} does'nt exist in the current path")
    except KeyError as e:
        print(f"Key - {str(e)} does'nt exist in the current path")


if __name__ == '__main__':
    path = '/menu/popup/menuitem/3/Bendod'
    my_json = """
    {
    "menu": {
      "id": "file",
      "value": "File",
      "popup": {
        "menuitem": [
          {"value": "New", "onclick": "CreateNewDoc()"},
          {"value": "Open", "onclick": "OpenDoc()"},
          {"value": "Close", "onclick": "CloseDoc()"},
          {"Bendod": "noob"}
        ]
      }
    }}"""

    print("Avarage time for reduced Walker: " + str(timeit.timeit('json_navigator_reduced(path, my_json)',
                                                                  setup='from __main__ import json_navigator_reduced',
                                                                  number=10000, globals=globals())))
    print("Avarage time for non-reduced Walker: " + str(timeit.timeit('json_navigator(path, my_json)',
                                                                      setup='from __main__ import json_navigator',
                                                                      number=10000, globals=globals())))
