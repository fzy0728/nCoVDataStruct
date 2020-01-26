import re
import pandas as pd

from tire import ACTree
from tire import remove_contain

# 词典文件 key 为类别，value为文件地址
dict_files = {'district':'./data/district_dict', 'category': './data/category_dict'}

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

if __name__ == '__main__':

    # 初始化字典树
    ac = get_type_tire(dict_files)

    res = []

    with open('./data/content_data') as data:

        for i in data:

            # 初始化信息，严格控制地点数据。
            category = '确诊'
            district = None
            i_type = '累计'

            # 将长句分为短句
            small_sentences = split_pattern.split(i)

            for j in small_sentences:
                if '新增' in j:
                    i_type = '新增'
                if '累计' in j or '增至' in j:
                    i_type = '累计'
                print(j)

                # 获取每一个短句中存在的人数信息，并将人数信息加入到字典树中。
                s = set(get_people_pattern(j.strip()))
                people_size_entity = [[t, 'size'] for t in s]
                ac.add_entity(people_size_entity)

                # 最长匹配所有实体，无重叠
                entity = remove_contain(ac.search_ner(j))
                for e in entity:
                    # 更新地点数据
                    if e['tag'] == 'district':
                        district = e['name']
                    # 更新类别数据
                    if e['tag'] == 'category':
                        category = e['name']
                    # 对每一个抽取到的人口信息，给定地点和类别信息，并判断是增量还是累计值
                    if e['tag'] == 'size' and district and category:
                        res.append([i, j, district, category, e['name'], i_type])

                    # print(e)


    data = pd.DataFrame(res, columns=['content', 'small_content', '地点', '类别', '人数', '+？'])

    data.to_csv('./data/res.csv', index=False)