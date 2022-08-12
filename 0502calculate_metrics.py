import json
import os
import time

from dateutil import relativedelta
from collections import Counter
from numpy import *
import datetime
import numpy as np


def calculate_metrics(json_data, commit_data):
    result = {}

    developer_list =[]
    create_list = []
    contributor_timeList = {}

    issue_create_list = []
    issue_update_list = []
    issue_closed_list = []
    open_issue_number = 0
    delay_time = 0
    closed_issue_create_list = []
    response_issue_create_list = []
    issue_responsed_list = []
    issue_resolution_time = []
    issue_comment_list = []
    long_time_issue_date = []
    open_issue_date = []
    long_time_issue_list = {}

    comment_create_list = []
    commenter_list = []

    pr_create_list = []
    pr_update_list = []
    pr_closed_list = []
    long_time_pr_date = []
    pr_resolution_time = []
    pr_comment_list = []
    pr_committer_list = []
    overload_committer = []
    overload_reviewer = []
    pr_submitted_list = []
    reviewer_list = []
    response_pr_create_list = []
    pr_responsed_list = []
    each_pr_response_time = {}
    reviewed_pr_create_list = []
    create2review_list = []
    each_pr_create2review_time = {}
    pr_review_list = []
    reviewed_pr_list = {}
    submitted2merge_list = []
    pr_merged_list = []
    unreviewed_merged_pr_number = {}
    unreviewed_merged_pr_list = {}
    discarded_pr_number = {}
    discarded_pr_list = {}
    discarded_pr_wasted_comment = {}
    discarded_pr_wasted_review = {}
    discarded_pr_closed_list = []
    open_pr_date = []

    long_time_threshold = 3  # 72 hours = 3 days
    commit_date_list = []
    merged_commits = []
    changed_file_number_per_month = {}
    changed_nloc_per_month = {}

    for issue in json_data['issue']:
        t = issue['node']
        if t['author']:
            developer = t['author']['login']
        else:
            developer = t['author']
        developer_list.append(developer)
        created_at = t['createdAt']
        create_year, create_month, create_date = created_at.split('-')
        create_year_month = create_year + create_month
        update_at = t['updatedAt']
        update_year, update_month, update_date = update_at.split('-')
        update_year_month = update_year + update_month
        if developer in contributor_timeList.keys():
            contributor_timeList[developer].append(create_year_month)
        else:
            contributor_timeList[developer] = [create_year_month]
        create_list.append(create_year_month)
        temp = created_at.split('T')
        time1 = temp[1].split('Z')
        dt1 = datetime.datetime.strptime(temp[0] + ' ' + time1[0], '%Y-%m-%d %H:%M:%S')
        # issue相关指标:需要用到created_at，closed_at，responsed_at,
        # if 'pull_request' not in t:
        issue_create_list.append(create_year_month)
        issue_update_list.append(update_year_month)
        not_long_time = dt1 + datetime.timedelta(days=long_time_threshold)  # 在该时间内关闭则不是长时间运行
        if t['closedAt'] != None:
            closed_issue_create_list.append(create_year_month)
            closed_at = t['closedAt']
            close_year, close_month, close_date = closed_at.split('-')
            close_year_month = close_year + close_month
            memp = closed_at.split('T')
            m = memp[1].split('Z')
            dt2 = datetime.datetime.strptime(memp[0] + ' ' + m[0], '%Y-%m-%d %H:%M:%S')
            timediff = (dt2 - dt1).total_seconds()
            issue_resolution_time.append(timediff)
            create_time = dt1
            while create_time <= dt2:
                open_year_month = str(dt1)[0:4] + str(dt1)[5:7]
                open_issue_date.append(open_year_month)
                create_time = create_time + relativedelta.relativedelta(months=1)
            while not_long_time <= dt2:
                long_time_year_month = str(not_long_time)[0:4] + str(not_long_time)[5:7]
                long_time_issue_date.append(long_time_year_month)
                not_long_time = not_long_time + relativedelta.relativedelta(months=1)
            issue_closed_list.append(close_year_month)
        if t['comments']['edges']:
            response_issue_create_list.append(create_year_month)
            response_at = None
            for node in t['comments']['edges']:
                i = node['node']
                created_at = i['createdAt']
                year, month, date = created_at.split('-')
                year_month = year + month
                comment_create_list.append(year_month)
                if i['author']:
                    commenter = i['author']['login']
                else:
                    commenter = i['author']
                commenter_list.append(commenter)
                if commenter in contributor_timeList.keys():
                    contributor_timeList[commenter].append(year_month)
                else:
                    contributor_timeList[commenter] = [year_month]
                issue_comment_list.append(year_month)
                if response_at  == None:
                    response_at = i['createdAt']
            memp = response_at.split('T')
            m = memp[1].split('Z')
            dt2 = datetime.datetime.strptime(memp[0] + ' ' + m[0], '%Y-%m-%d %H:%M:%S')
            response_timediff = (dt2 - dt1).total_seconds()
            issue_responsed_list.append(response_timediff)
        if t['state'] == 'OPEN':
            open_issue_number += 1
            closed_at = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            memp = closed_at.split('T')
            m = memp[1].split('Z')
            dt2 = datetime.datetime.strptime(memp[0] + ' ' + m[0], '%Y-%m-%d %H:%M:%S')
            create_time = dt1
            timediff = (dt2 - create_time).total_seconds()
            delay_time += timediff
            while create_time <= dt2:
                open_year_month = str(dt1)[0:4] + str(dt1)[5:7]
                open_issue_date.append(open_year_month)
                create_time = create_time + relativedelta.relativedelta(months=1)
            while not_long_time <= dt2:
                long_time_year_month = str(not_long_time)[0:4] + str(not_long_time)[5:7]
                long_time_issue_date.append(long_time_year_month)
                not_long_time = not_long_time + relativedelta.relativedelta(months=1)
        # pull request相关指标：需要用到created_at
    for pr in json_data['pullrequest']:
        t = pr['node']
        if t['author']:
            developer = t['author']['login']
        else:
            developer = t['author']
        developer_list.append(developer)
        created_at = t['createdAt']
        create_year, create_month, create_date = created_at.split('-')
        create_year_month = create_year + create_month
        update_at = t['updatedAt']
        update_year, update_month, update_date = update_at.split('-')
        update_year_month = update_year + update_month
        pr_update_list.append(update_year_month)
        if developer in contributor_timeList.keys():
            contributor_timeList[developer].append(create_year_month)
        else:
            contributor_timeList[developer] = [create_year_month]
        create_list.append(create_year_month)
        temp = created_at.split('T')
        time1 = temp[1].split('Z')
        dt1 = datetime.datetime.strptime(temp[0] + ' ' + time1[0], '%Y-%m-%d %H:%M:%S')
        merged_at = t['mergedAt']
        pr_create_list.append(create_year_month)
        pr_committer_list.append(developer)
        not_long_time = dt1 + datetime.timedelta(days=long_time_threshold)  # 在该时间内关闭则不是长时间运行
        if t['closedAt'] != None:
            closed_at = t['closedAt']
            close_year, close_month, close_date = closed_at.split('-')
            close_year_month = close_year + close_month
            pr_closed_list.append(close_year_month)
            memp = closed_at.split('T')
            m = memp[1].split('Z')
            dt2 = datetime.datetime.strptime(memp[0] + ' ' + m[0], '%Y-%m-%d %H:%M:%S')
            timediff = (dt2 - dt1).total_seconds()
            pr_resolution_time.append(timediff)
            # 运行的pr
            create_time = dt1
            while create_time <= dt2:
                open_year_month = str(dt1)[0:4] + str(dt1)[5:7]
                open_pr_date.append(open_year_month)
                create_time = create_time + relativedelta.relativedelta(months=1)
            # 长时间运行的pr
            while not_long_time <= dt2:
                long_time_year_month = str(not_long_time)[0:4] + str(not_long_time)[5:7]
                long_time_pr_date.append(long_time_year_month)
                not_long_time = not_long_time + relativedelta.relativedelta(months=1)
        submitted_at = []
        for node in t['reviews']['edges']:
            i = node['node']
            submitted_at = i['submittedAt']
            if submitted_at:
                year, month, date = submitted_at.split('-')
                year_month = year + month
                pr_submitted_list.append(year_month)
            if i['author']:
                reviewer = i['author']['login']
            else:
                reviewer = i['author']
            reviewer_list.append(reviewer)
            if reviewer in contributor_timeList.keys():
                contributor_timeList[reviewer].append(year_month)
            else:
                contributor_timeList[reviewer] = [year_month]
        if t['comments']['edges']:
            response_pr_create_list.append(create_year_month)
            response_at = None
            for node in t['comments']['edges']:
                i = node['node']
                created_at = i['createdAt']
                year, month, date = created_at.split('-')
                year_month = year + month
                comment_create_list.append(year_month)
                if i['author']:
                    commenter = i['author']['login']
                else:
                    commenter = i['author']
                commenter_list.append(commenter)
                if commenter in contributor_timeList.keys():
                    contributor_timeList[commenter].append(year_month)
                else:
                    contributor_timeList[commenter] = [year_month]
                pr_comment_list.append(year_month)
                if response_at == None:
                    response_at = i['createdAt']
            memp = response_at.split('T')
            m = memp[1].split('Z')
            dt2 = datetime.datetime.strptime(memp[0] + ' ' + m[0], '%Y-%m-%d %H:%M:%S')
            response_timediff = (dt2 - dt1).total_seconds()
            pr_responsed_list.append(response_timediff)
            each_pr_response_time[t['number']] = round(response_timediff / 3600, 2)
        if submitted_at:
            reviewed_pr_create_list.append(create_year_month)
            memp = submitted_at.split('T')
            m = temp[1].split('Z')
            dt2 = datetime.datetime.strptime(memp[0] + ' ' + m[0], '%Y-%m-%d %H:%M:%S')
            timediff = (dt2 - dt1).total_seconds()
            create2review_list.append(timediff)
            each_pr_create2review_time[t['number']] = round(timediff / 3600, 2)
        if submitted_at and merged_at:
            year, month, date = submitted_at.split('-')
            year_month = year + month
            temp = submitted_at.split('T')
            time2 = temp[1].split('Z')
            memp = merged_at.split('T')
            m = memp[1].split('Z')
            submitted = datetime.datetime.strptime(temp[0] + ' ' + time2[0], '%Y-%m-%d %H:%M:%S')
            dt2 = datetime.datetime.strptime(memp[0] + ' ' + m[0], '%Y-%m-%d %H:%M:%S')
            if dt2 > submitted:
                pr_review_list.append(year_month)
                timediff = (dt2 - submitted).total_seconds()
                submitted2merge_list.append(timediff)
        if t['state'] == 'OPEN':
            closed_at = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            memp = closed_at.split('T')
            m = memp[1].split('Z')
            dt2 = datetime.datetime.strptime(memp[0] + ' ' + m[0], '%Y-%m-%d %H:%M:%S')
            create_time = dt1
            while create_time <= dt2:
                open_year_month = str(dt1)[0:4] + str(dt1)[5:7]
                open_pr_date.append(open_year_month)
                create_time = create_time + relativedelta.relativedelta(months=1)
            while not_long_time <= dt2:
                long_time_year_month = str(not_long_time)[0:4] + str(not_long_time)[5:7]
                long_time_pr_date.append(long_time_year_month)
                not_long_time = not_long_time + relativedelta.relativedelta(months=1)
        merge_state = t['merged']
        if merge_state == True:
            year, month, date = merged_at.split('-')
            year_month = year + month
            pr_merged_list.append(year_month)
        if t['reviews']['edges'] == [] and merge_state == True:
            year, month, date = merged_at.split('-')
            year_month = year + month
            month_each = year_month
            if month_each in unreviewed_merged_pr_number.keys():
                unreviewed_merged_pr_number[month_each] += 1
            else:
                unreviewed_merged_pr_number[month_each] = 1
        if t['state'] == 'CLOSED':
            closed_at = t['closedAt']
            close_year, close_month, close_date = closed_at.split('-')
            close_year_month = close_year + close_month
            month_each = close_year_month
            if month_each in discarded_pr_number.keys():
                discarded_pr_number[month_each] += 1
            else:
                discarded_pr_number[month_each] = 1
            if month_each in discarded_pr_wasted_comment:
                discarded_pr_wasted_comment[month_each] += len(t['comments']['edges'])
            else:
                discarded_pr_wasted_comment[month_each] = len(t['comments']['edges'])
            if month_each in discarded_pr_wasted_review:
                discarded_pr_wasted_review[month_each] += len(t['reviews']['edges'])
            else:
                discarded_pr_wasted_review[month_each] = len(t['reviews']['edges'])
            discarded_pr_closed_list.append(close_year_month)

    for c in commit_data:
        commit_date = c['committer_date']
        commit_year, commit_month = commit_date.split('-')[0], commit_date.split('-')[1]
        commit_year_month = commit_year + commit_month
        if commit_year_month in changed_file_number_per_month.keys():
            changed_file_number_per_month[commit_year_month] += c['changes']['files']
        else:
            changed_file_number_per_month[commit_year_month] = c['changes']['files']
        if commit_year_month in changed_nloc_per_month.keys():
            changed_nloc_per_month[commit_year_month] += c['changes']['lines']
        else:
            changed_nloc_per_month[commit_year_month] = c['changes']['lines']
        # 计算每个月实际产生的commit个数，不包括自动Merged的(parent = 2)
        if c['parent'] == 1:
            commit_date_list.append(commit_year_month)
        elif c['parent'] >= 2:
            merged_commits.append(commit_year_month)

    print('json data analysis over!')

    # new_commits_per_month
    new_commits_per_month = dict(
        sorted(Counter(commit_date_list).most_common(len(Counter(commit_date_list))), key=(lambda x: [x[0]])))
    print('1')

    # new merged commits per month
    new_merged_commits_per_month = dict(
        sorted(Counter(merged_commits).most_common(len(Counter(merged_commits))), key=(lambda x: [x[0]])))
    print('2')

    # 新提交的issue
    issues_created_per_month = dict(
        sorted(Counter(issue_create_list).most_common(len(Counter(issue_create_list))), key=(lambda x: [x[0]])))
    print('3')

    # 新更新的issue
    issue_updated_per_month = dict(
        sorted(Counter(issue_update_list).most_common(len(Counter(issue_update_list))), key=(lambda x: [x[0]])))
    print('4')

    # 新关闭的issue
    issues_closed_per_month = dict(
        sorted(Counter(issue_closed_list).most_common(len(Counter(issue_closed_list))), key=(lambda x: [x[0]])))
    print('5')

    # 长时间运行的issue
    long_time_issue_number_per_month = dict(
        sorted(Counter(long_time_issue_date).most_common(len(Counter(long_time_issue_date))), key=(lambda x: [x[0]])))
    print('6')

    # 未解决issue花费的平均时间  (项目之间对比)
    issue_avg_delay_time = round(delay_time / open_issue_number / 3600, 2)

    # 每月创建的issue的平均响应时长
    average_issue_comment_second = {}
    for i in list(zip(response_issue_create_list, issue_responsed_list)):
        response_issue_num = int(dict(Counter(response_issue_create_list))[i[0]])
        if i[0] in average_issue_comment_second:
            issue_response_time += int(i[1])
        else:
            issue_response_time = int(i[1])
        average_issue_comment_second[i[0]] = round(issue_response_time / response_issue_num / 3600, 2)   # 小时
    print('7')

    # 每月已解决issue花费的平均时间
    average_issue_resolve_second = {}
    a = issues_closed_per_month
    r = list(zip(issue_closed_list, issue_resolution_time))
    for i in r:
        issue_close_num = int(a[i[0]])
        if i[0] in average_issue_resolve_second:
            issue_resolution_time += int(i[1])
        else:
            issue_resolution_time = int(i[1])
        average_issue_resolve_second[i[0]] = int(round(issue_resolution_time / issue_close_num / 3600, 2))
    print('8')

    # issue每月新增的评论数
    issues_comment_created_per_month = dict(
        sorted(Counter(issue_comment_list).most_common(len(Counter(issue_comment_list))), key=(lambda x: [x[0]])))
    print('9')

    # 新提交的pr
    pr_created_per_month = dict(
        sorted(Counter(pr_create_list).most_common(len(Counter(pr_create_list))), key=(lambda x: [x[0]])))
    print('10')

    # 新更新的pr
    pr_updated_per_month = dict(
        sorted(Counter(pr_update_list).most_common(len(Counter(pr_update_list))), key=(lambda x: [x[0]])))
    print('11')
    # 新关闭的pr
    pr_closed_per_month = dict(
        sorted(Counter(pr_closed_list).most_common(len(Counter(pr_closed_list))), key=(lambda x: [x[0]])))
    print('12')

    # 长时间运行的pr
    long_time_pr_number_per_month = dict(
        sorted(Counter(long_time_pr_date).most_common(len(Counter(long_time_pr_date))), key=(lambda x: [x[0]]),
               reverse=True))
    print('13')

    # 每月已关闭的pr花费的平均时间
    average_pr_resolve_second = {}
    a = pr_closed_per_month
    r = list(zip(pr_closed_list, pr_resolution_time))
    for i in r:
        pr_close_num = int(a[i[0]])
        if i[0] in average_pr_resolve_second:
            pr_resolution_time += int(i[1])
        else:
            pr_resolution_time = int(i[1])
        average_pr_resolve_second[i[0]] = int(round(pr_resolution_time / pr_close_num / 3600, 2))
    print('14')

    # pr每月新增的评论数
    pr_comment_created_per_month = dict(
        sorted(Counter(pr_comment_list).most_common(len(Counter(pr_comment_list))), key=(lambda x: [x[0]])))
    print('15')

    # 每月创建的pr的平均响应时长
    average_pr_comment_second = {}
    for i in list(zip(response_pr_create_list, pr_responsed_list)):
        pr_num = int(dict(Counter(response_pr_create_list))[i[0]])
        if i[0] in average_pr_comment_second:
            pr_response_time += int(i[1])
        else:
            pr_response_time = int(i[1])
        average_pr_comment_second[i[0]] = round(pr_response_time / pr_num / 3600, 2)
    print('16')

    # 每月提交审查的pr的平均审查周期
    average_review_second = {}
    for i in sorted(list(zip(pr_review_list, submitted2merge_list)), key=(lambda x: [x[0]])):
        pr_num = int(dict(Counter(pr_review_list))[i[0]])
        if i[0] in average_review_second:
            review_time_diff += int(i[1])
        else:
            review_time_diff = int(i[1])
        average_review_second[i[0]] = round(review_time_diff / pr_num / 3600, 2)
    print('17')

    # 每月pr的平均审查次数，当月总审查次数/当月被审查pr数
    pr_avg_review_times_per_month = {}
    reviewed_pr_list = dict(Counter(reviewed_pr_create_list))
    for key,value in reviewed_pr_list.items():
        review_times = dict(Counter(pr_submitted_list)).get(key)
        if review_times == None:
            review_times = 0
        pr_avg_review_times_per_month[key] = round(review_times / value, 0)
    pr_avg_review_times_per_month = dict(sorted(pr_avg_review_times_per_month.items(), key=(lambda x: [x[0]])))
    print('18')

    # 每月丢弃的pr
    # 每月丢弃的pr浪费的平均评论数:评论数/丢弃的pr数
    # 每月丢弃的pr浪费的平均审查次数:审查次数/丢弃的pr数
    discarded_pr_wasted_avg_comment_per_month = {}
    discarded_pr_wasted_avg_review_per_month = {}
    for key,value in discarded_pr_number.items():
        discarded_pr_wasted_avg_comment_per_month[key] = round(discarded_pr_wasted_comment.get(key) / value, 1)
        discarded_pr_wasted_avg_review_per_month[key] = round(discarded_pr_wasted_review.get(key) / value, 1)
    discarded_pr_wasted_avg_comment_per_month = dict(
        sorted(discarded_pr_wasted_avg_comment_per_month.items(), key=(lambda x: [x[0]])))
    discarded_pr_wasted_avg_review_per_month = dict(
        sorted(discarded_pr_wasted_avg_review_per_month.items(), key=(lambda x: [x[0]])))
    print('19')

    # 每月未经审查而合并的pr数

    # 活跃的提交者
    list1 = list(set(zip(create_list, developer_list)))
    if list1 == []:
        active_developer = {}
    else:
        active_developer = dict(
            sorted(Counter(np.array(list1)[:, 0]).most_common(
                len(Counter(np.array(list1)[:, 0]))),
                key=(lambda x: [x[0]]), reverse=True))
    print('20')

    # 活跃的评论者人数(只要有提交，有贡献，就是活跃的)
    list2 = list(set(zip(comment_create_list, commenter_list)))
    if list2 == []:
        active_commenter = {}
    else:
        active_commenter = dict(sorted(
            Counter(np.array(list2)[:, 0]).most_common(
                len(Counter(np.array(list2)[:, 0]))),
            key=(lambda x: [x[0]]), reverse=True))
    print('21')

    # 活跃的审查者人数
    list3 = list(set(zip(pr_submitted_list, reviewer_list)))
    if list3 == []:
        active_reviewer = {}
    else:
        active_reviewer = dict(
            sorted(Counter(np.array(list3)[:, 0]).most_common(
                len(Counter(np.array(list3)[:, 0]))),
                key=(lambda x: [x[0]]), reverse=True))
    print('22')

    # 超负荷的提交者
    overload_committer_list = {}
    for i in set(list(zip(create_list, developer_list))):
        if list(zip(create_list, developer_list)).count(i) >= 20:  # 定义是每周5个以下为健康，每月按4周计算，则应低于20
            month_each = i[0]
            if month_each in overload_committer_list.keys():
                overload_committer_list[month_each].append(i[1])
            else:
                overload_committer_list[month_each] = [i[1]]
            overload_committer.append(i)
    if overload_committer:
        overload_committer = dict(
            sorted(Counter(np.array(overload_committer)[:, 0]).most_common(
                len(Counter(np.array(overload_committer)[:, 0]))),
                key=(lambda x: [x[0]]), reverse=True))
    else:
        overload_committer = {}
    print('23')

    # 超负荷的评论者
    overload_commenter = []
    overload_commenter_list = {}
    for i in set(list(zip(comment_create_list, commenter_list))):
        if list(zip(comment_create_list, commenter_list)).count(i) >= 20:  # 定义是每周5个以下为健康，每月按4周计算，则应低于20
            month_each = i[0]
            if month_each in overload_commenter_list.keys():
                overload_commenter_list[month_each].append(i[1])
            else:
                overload_commenter_list[month_each] = [i[1]]
            overload_commenter.append(i)
    if overload_commenter:
        overload_commenter = dict(
            sorted(Counter(np.array(overload_commenter)[:, 0]).most_common(
                len(Counter(np.array(overload_commenter)[:, 0]))),
                key=(lambda x: [x[0]]), reverse=True))
    else:
        overload_commenter = {}
    print('24')

    # 超负荷的审查者
    overload_reviewer_list = {}
    for i in set(list(zip(pr_submitted_list, reviewer_list))):
        if list(zip(pr_submitted_list, reviewer_list)).count(i) >= 20:  # 定义是每周5个以下为健康，每月按4周计算，则应低于20
            month_each = i[0]
            if month_each in overload_reviewer_list.keys():
                overload_reviewer_list[month_each].append(i[1])
            else:
                overload_reviewer_list[month_each] = [i[1]]
            overload_reviewer.append(i)
    if overload_reviewer:
        overload_reviewer = dict(
            sorted(
                Counter(np.array(overload_reviewer)[:, 0]).most_common(len(Counter(np.array(overload_reviewer)[:, 0]))),
                key=(lambda x: [x[0]]), reverse=True))
    else:
        overload_reviewer = {}
    print('25')

    # 每月新增的贡献者数
    new_contributor_number_permonth = {}
    contributor_list_permonth = {}
    for key, value in contributor_timeList.items():
        sorted_value_ct = sorted(list(value))
        month_each = str(sorted_value_ct[0])
        if month_each in contributor_list_permonth.keys():
            contributor_list_permonth[month_each].append(key)
        else:
            contributor_list_permonth[month_each] = [key]
        # 统计每个月新增的贡献者的数量
        # 按key排序，并统计各个键对应的值的数目
    for eachTime in sorted(contributor_list_permonth, reverse=True):
        new_contributor_number_permonth[eachTime] = len(contributor_list_permonth[eachTime])
    print('26')

    # 团队健康
    result['active_committer_number_per_month'] = active_developer
    result['active_commenter_number_per_month'] = active_commenter
    result['active_reviewer_number_per_month'] = active_reviewer
    result['new_contributor_per_month'] = new_contributor_number_permonth
    result['overloaded_committer_number_per_month'] = overload_committer
    result['overloaded_commenter_number_per_month'] = overload_commenter
    result['overloaded_reviewer_number_per_month'] = overload_reviewer

    # 开发活跃度
    result['issues_created_per_month'] = issues_created_per_month
    result['issues_updated_per_month'] = issue_updated_per_month
    result['issues_closed_per_month'] = issues_closed_per_month
    result['issues_avg_comment_time(hour)'] = average_issue_comment_second
    result['issues_avg_resolution_time(hour)'] = average_issue_resolve_second
    result['issues_num_of_comment_per_month'] = issues_comment_created_per_month
    result['pr_created_per_month'] = pr_created_per_month
    result['pr_updated_per_month'] = pr_updated_per_month
    result['pr_closed_per_month'] = pr_closed_per_month
    result['pr_avg_comment_time(hour)'] = average_pr_comment_second
    result['pr_avg_resolution_time(hour)'] = average_pr_resolve_second
    result['pr_num_of_comment_per_month'] = pr_comment_created_per_month
    result['new_commits_per_month'] = new_commits_per_month
    result['new_merged_commits_per_month'] = new_merged_commits_per_month
    result['changed_file_number_per_month'] = changed_file_number_per_month
    result['changed_nloc_per_month'] = changed_nloc_per_month

    # 开发风险
    result['long_time_issue_number_per_month'] = long_time_issue_number_per_month
    result['long_time_pr_number_per_month'] = long_time_pr_number_per_month
    result['pr_avg_review_cycle_per_month(hour)'] = average_review_second
    result['pr_avg_review_times_per_month'] = pr_avg_review_times_per_month
    result['discarded_pr_number_per_month'] = discarded_pr_number
    result['discarded_pr_wasted_avg_comment_per_month'] = discarded_pr_wasted_avg_comment_per_month
    result['discarded_pr_wasted_avg_review_per_month'] = discarded_pr_wasted_avg_review_per_month
    result['unreviewed_merged_pr_number_per_month'] = unreviewed_merged_pr_number

    return result


def get_json_path(root_path, result_file):
    for root,dirs,files in os.walk(root_path, 'r'):
        for file in files:
            start = time.perf_counter()
            file_path = os.path.join(root,file)
            f = open(file_path, 'r')
            json_data = json.load(f)
            a = file_path.split('\\')[1]
            username = a.split('&')[0]
            projectname = a.split('&')[1]
            commit_data_path = './clone_commit/commit_data/' + projectname + '.json'
            commit_data = json.load(open(commit_data_path, 'r', encoding='utf-8'))
            if not os.path.exists(result_file):
                os.makedirs(result_file)
            result_path = result_file + username + '&' + projectname + '.json'
            if not os.path.exists(result_path):
                result = calculate_metrics(json_data, commit_data)
                with open(result_path, 'w') as f:
                    json.dump(result, f, indent=4)
                print('Save successfully!')
            run_time = (time.perf_counter() - start)
            print("This repo used time:", run_time, ' seconds')


if __name__ == "__main__":
    language_list = ['JavaScript', 'Python', 'Java']
    for language in language_list:
        pr_issue_root = './raw_data/jsonFile_' + language + '_raw_data'
        result_file = './result/' + language + '_calculate_result/'
        get_json_path(pr_issue_root, result_file)
