import ahocorasick
import logging
import json


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

def remove_contain(ners):
    ners = sorted(ners, key=lambda x: x['start'])
    contain_ner = []
    contain = []
    for ner in ners:
        if not contain_ner:
            contain_ner.append(ner)
            continue
        last_ner = contain_ner.pop()
        if not is_complex(ner, last_ner):
            if len(ner['name']) >= len(last_ner['name']):
                contain_ner.append(ner)
                contain.append(last_ner)
            else:
                contain_ner.append(last_ner)
                contain.append(ner)
        else:
            contain_ner.append(last_ner)
            contain_ner.append(ner)

    for i in contain:
        flag = 1
        for j in contain_ner:
            if is_fix_complex(i, j):
                flag = 0
                break
        if flag:
            contain_ner.append(i)
    return sorted(contain_ner, key=lambda x: x['start'])

def is_complex(now, old):
    # print(now, old)
    if now['start'] < old['end']:
        # print('FALSE')
        return False
    return True


def is_fix_complex(new, old):
    if old['start'] <= new['start'] < old['end'] \
            or old['start'] < new['end'] <= old['end']:
        return True
    return False


class ACTree:

    def __init__(self):
        self.acTree = ahocorasick.Automaton()


    def build_Tree(self, datas):
        """
            构建字典树

            Parameters
            ----------

            data: 格式为['id', 'origin word', 'alias'] 其中 'alias'使用'|'进行分割

            Returns
            -------
            string
              a value in a string
        """
        for data, tag in datas:
            self.acTree.add_word(data, (data, tag))

        self.acTree.make_automaton()

    def add_entity(self, datas):
        for data, tag in datas:
            self.acTree.add_word(data, (data, tag))
        self.acTree.make_automaton()

    def search_ner(self, sentence):
        entitys = []
        for end_index, (original_value, tag) in self.acTree.iter(sentence):
            start_index = end_index - len(original_value) + 1
            entitys.append({"name": original_value,
                            "start": start_index,
                            "end": start_index + len(original_value),
                            "tag": tag})

        return entitys