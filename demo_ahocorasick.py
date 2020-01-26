import re
import pandas as pd

from tire import ACTree
from tire import remove_contain

# 词典文件 key 为类别，value为文件地址
dict_files = {'district':'./data/district_dict',
              'category': './data/category_dict',
              'crowd': './data/crowd_dict',
              'count': './data/count_dict'}

# 分句子模版
split_pattern = re.compile('[。|；|;|,|，|、|（|）|\(|\)]')

# 抽取人数模版
people_pattern = re.compile('[0-9]+[例|人]')

# 初始化词典树，返回ACtree
def get_type_tire(dict_files):
    '''
    初始化字典树
    :param dict_files: dict
    :return: ACTree
    '''
    entity = []
    for key, value in dict_files.items():
        with open(value) as data:
            for i in data:
                i = i.strip()
                entity.append([i, key])

    ac = ACTree()
    ac.build_Tree(entity)
    return ac


def get_people_pattern(content):
    '''
    抽取人数信息
    :param content: str
    :return: list
    '''
    people_size = people_pattern.findall(content)
    return people_size


def get_struct_data(ac, title, content):
    title = title.strip()
    content = content.replace('\n', '')
    title_res, title_district = get_sentence(ac, title, istitle=True)
    content_res, title_district = get_sentence(ac, content, istitle=False, title_district=title_district)

    return title_res + content_res


def init_category(entitys, sentence_len):
    for e in entitys:
        if e['tag'] == 'category':
            return ':'.join([e['name'], str(e['start'] + sentence_len), str(e['end'] + sentence_len)])
    return '确诊'

def get_sentence(ac, sentence, istitle=False, title_district=None):
    res = []
    category = None
    district = None
    count = '累计'

    # 将长句分为短句
    span = split_pattern.split(sentence)

    sentence_len = 0

    for index, j in enumerate(span):

        crowd = None

        # 获取每一个短句中存在的人数信息，并将人数信息加入到字典树中。
        s = set(get_people_pattern(j.strip()))
        people_size_entity = [[t, 'size'] for t in s]
        ac.add_entity(people_size_entity)

        # 最长匹配所有实体，无重叠
        entity = remove_contain(ac.search_ner(j))
        if not category or ':' not in category:
            category = init_category(entity, sentence_len)

        for e in entity:
            # 更新地点数据
            if e['tag'] == 'district':
                district = ':'.join([e['name'], str(e['start'] + sentence_len), str(e['end'] + sentence_len)])
                if istitle and not title_district:
                    title_district = e['name']
            if e['tag'] == 'count':
                count = ':'.join([e['name'], str(e['start'] + sentence_len), str(e['end'] + sentence_len)])
            if e['tag'] == 'crowd':
                crowd = ':'.join([e['name'], str(e['start'] + sentence_len), str(e['end'] + sentence_len)])
            # 更新类别数据
            if e['tag'] == 'category':
                category = ':'.join([e['name'], str(e['start'] + sentence_len), str(e['end'] + sentence_len)])
            # 对每一个抽取到的人口信息，给定地点和类别信息，并判断是增量还是累计值
            if e['tag'] == 'size' and district and category:
                res.append([sentence, j, count, crowd, istitle, title_district, district, category, e['name']])
        sentence_len += len(j)
    return res, title_district


if __name__ == '__main__':

    # 初始化字典树
    ac = get_type_tire(dict_files)

    res = []
    titles = open('./data/raw_title.txt').read().split('\n')
    contents = open('./data/raw_content.txt').read().split('\n')

    for title, content in zip(titles, contents):
        res.extend(get_struct_data(ac, title, content))


    data = pd.DataFrame(res, columns=['content', 'span', 'count', '特殊人群', 'istitle', '标题地点', '地点', '类别', '人数'])

    data.to_csv('./data/res.csv', index=False)