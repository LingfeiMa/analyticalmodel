import json
import os
import pandas as pd


def paint(json_fn: str, csv_name: str):
    json_file = open(json_fn, "r")  # 输入需要转换的json文件
    item_list = json.load(json_file)
    # TW1:2019.01-2022.04
    # TW2:2019.01-2019.11
    # TW3:2019.12-2020.03
    # TW4:2020.04-2020.12
    # TW5:2021.01-2021.10
    # TW6:2021.11-2022.04
    y = ['201901', '201902', '201903', '201904', '201905', '201906', '201907', '201908', '201909', '201910',
         '201911', '201912', '202001', '202002', '202003', '202004', '202005', '202006', '202007', '202008',
         '202009', '202010', '202011', '202012', '202101', '202102', '202103', '202104', '202105', '202106',
         '202107', '202108', '202109', '202110', '202111', '202112', '202201', '202202', '202203', '202204']
    # csv_path = './csv/TWx/language_csv/xxx&xxx'
    for metrics in item_list:
        if metrics in['contributor_detail','contributor_number','repo_language','repo_create_date']:
            continue
        csv_path = './csv/' + metrics + '/TW1/'
        if not os.path.exists(csv_path):
            os.makedirs(csv_path)
        csv_fn = csv_path + csv_name + '.csv'
        a = os.path.splitext(json_fn)
        project = a[0].split('/')[3]
        if metrics == 'issues_avg_delay_time(hour)':
            result = pd.DataFrame(data=item_list[metrics], index=[project], columns=['issues_avg_delay_time(hour)'])
        else:
            result = pd.DataFrame(data=item_list[metrics], index=[project], columns=y)
        if os.path.exists(csv_fn):
            result.to_csv(csv_fn, mode='a', header=False, sep=',')
        else:
            result.to_csv(csv_fn)
    json_file.close()


def get_json_path(root_path, i):
    for root, dirs, files in os.walk(root_path, 'r'):
        for file in files:
            i += 1
            a = file.split('.')[0]
            username = a.split('&')[0]
            projectname = a.split('&')[1]
            result_path = root_path + '/' + username + '&' + projectname + '.json'
            csv_name = username + '&' + projectname
            paint(result_path, csv_name)
            print('Save ' + str(i) + ' projects csv files successfully! ')


if __name__ == "__main__":
    language_list = ['JavaScript', 'Python', 'Java', 'TypeScript', 'C#', 'PHP', 'C++', 'Shell', 'C', 'Ruby']  # 'JavaScript', 'Python', 'Java', 'TypeScript', 'C#', 'PHP', 'C++', 'Shell', 'C', 'Ruby'
    for language in language_list:
        i = 0
        result_root = './result/' + language + '_calculate_result'
        get_json_path(result_root, i)
