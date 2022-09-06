import json
import time
import requests
import os
import datetime


start = time.perf_counter()


def request_get_json(url,query, headers):
    ret_code = 0
    while ret_code != 200 and ret_code != 404:
        try:
            res = requests.post(url=url, json={"query": query}, headers=headers)
            ret_code = res.status_code
            # print(ret_code)

            while ret_code == 403:
                nowtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print('sleeping now. from '+ nowtime)
                datetime.time.sleep(1800) #sleap a half an hour
                res = requests.get(url=url, headers=headers)
                ret_code = res.status_code

            # if ret_code != 200:  # ret_code != 200表明http请求失败，可以考虑进行处理
                # print(ret_code)
                # pass
        except:
            pass
    return res.json()


def query_pr(token, name, owner, api):
    header = {'Authorization': f'token {token}'}
    after_cursor = ''
    hasnextpage = True
    json_data = {}
    while hasnextpage:
        if after_cursor == '':
            query = '{\n' + f'repository(owner:"{owner}",name:"{name}")' + """{
                pullRequests(first:100){
                    edges{
                        node{
                            number
                            author{
                                login
                                url
                            }
                            state
                            createdAt
                            updatedAt
                            closedAt
                            merged
                            mergedAt
                            comments(last:100,orderBy:{direction:DESC,field:UPDATED_AT}){
                                edges{
                                    node{
                                        author{
                                            login
                                            url
                                        }
                                        createdAt
                                        publishedAt}}}
                            reviewDecision
                            reviews(last:100){
                                edges{
                                    node{
                                        author{
                                            login
                                            url
                                        }
                                        createdAt
                                        submittedAt
                                    }
                                }
                            }
                        }
                    }
                    pageInfo{
                        endCursor
                        hasNextPage
                    }
                }
            }
        }"""
            response = request_get_json(api, query, headers=header)
            json_data['pullrequest'] = response['data']['repository']['pullRequests']['edges']
            after_cursor = response['data']['repository']['pullRequests']['pageInfo']['endCursor']
            hasnextpage = response['data']['repository']['pullRequests']['pageInfo']['hasNextPage']
        else:
            query = '{\n' + f'repository(owner:"{owner}",name:"{name}")' + '{\n' + \
                f'pullRequests(first:100,after:"{after_cursor}")' + """{
                    edges{
                        node{
                            number
                            author{
                                login
                                url
                            }
                            state
                            createdAt
                            updatedAt
                            closedAt
                            merged
                            mergedAt
                            comments(last:100,orderBy:{direction:DESC,field:UPDATED_AT}){
                                edges{
                                    node{
                                        author{
                                            login
                                            url
                                        }
                                        createdAt
                                        publishedAt}}}
                            reviewDecision
                            reviews(last:100){
                                edges{
                                    node{
                                        author{
                                            login
                                            url
                                        }
                                        createdAt
                                        submittedAt
                                    }
                                }
                            }
                        }
                    }
                    pageInfo{
                        endCursor
                        hasNextPage
                    }
                }
            }
        }"""
            response = request_get_json(api, query, headers=header)
            json_data['pullrequest'] = json_data['pullrequest'] + (response['data']['repository']['pullRequests']['edges'])
            after_cursor = response['data']['repository']['pullRequests']['pageInfo']['endCursor']
            hasnextpage = response['data']['repository']['pullRequests']['pageInfo']['hasNextPage']
            print(hasnextpage)
            print(len(json_data['pullrequest']))
    return json_data


def query_issue(token, name, owner, api):
    header = {'Authorization': f'token {token}'}
    after_cursor = ''
    hasnextpage = True
    json_data = {}
    while hasnextpage:
        if after_cursor == '':
            query = '{\n' + f'repository(owner:"{owner}",name:"{name}")' + """{
                issues(first:100){
                    edges{
                        node{
                            number
                            author{
                                login
                                url
                            }
                            state
                            createdAt
                            updatedAt
                            closedAt
                            comments(last:100,orderBy:{direction:DESC,field:UPDATED_AT}){
                                edges{
                                    node{
                                        author{
                                            login
                                            url
                                        }
                                        createdAt
                                        publishedAt}}}
                        }
                    }
                    pageInfo{
                        endCursor
                        hasNextPage
                    }
                }
            }
        }"""
            response = request_get_json(api, query, headers=header)
            json_data['issue'] = response['data']['repository']['issues']['edges']
            after_cursor = response['data']['repository']['issues']['pageInfo']['endCursor']
            hasnextpage = response['data']['repository']['issues']['pageInfo']['hasNextPage']
        else:
            query = '{\n' + f'repository(owner:"{owner}",name:"{name}")' + \
                    '{\n' + f'issues(first:100,after:"{after_cursor}")' + """{
                        edges{
                        node{
                            number
                            author{
                                login
                                url
                            }
                            state
                            createdAt
                            updatedAt
                            closedAt
                            comments(last:100,orderBy:{direction:DESC,field:UPDATED_AT}){
                                edges{
                                    node{
                                        author{
                                            login
                                            url
                                        }
                                        createdAt
                                        publishedAt}}}
                        }
                    }
                    pageInfo{
                        endCursor
                        hasNextPage
                    }
                }
            }
        }"""
            response = request_get_json(api, query, headers=header)
            json_data['issue'] = json_data['issue'] + (
            response['data']['repository']['issues']['edges'])
            after_cursor = response['data']['repository']['issues']['pageInfo']['endCursor']
            hasnextpage = response['data']['repository']['issues']['pageInfo']['hasNextPage']
            print(hasnextpage)
            print(len(json_data['issue']))
    return json_data


def analysisEachProject(token, repo_url, path_store):
    print(repo_url)
    user_repoName = repo_url.replace("https://github.com/", "")
    userName = user_repoName.split("/")[0]
    projectname = user_repoName.split("/")[1]
    print(userName)
    print(projectname)
    json_fn = path_store + userName + '&' + projectname + '&all_raw_data.json'
    pr_raw_data = query_pr(token, projectname, userName, api)
    issue_raw_data = query_issue(token, projectname, userName, api)
    all_raw_data = {**pr_raw_data, **issue_raw_data}
    with open(json_fn, 'w') as f:
        json.dump(all_raw_data, f, indent=4)
    print("Saved all raw data to " + json_fn)


def start_download(token,category):
    projectListFile = './project_category/' + category + '_repoList.txt'
    path_store = './raw_data/jsonFile_' + category + '_raw_data/'
    if not os.path.exists(path_store):
        os.makedirs(path_store)
    with open(projectListFile, 'r') as f:
        content_repo = f.read().splitlines()
        for repo_url in content_repo:
            start = time.perf_counter()
            analysisEachProject(token, repo_url, path_store)
            run_time = (time.perf_counter() - start)
            print("This repo used time:", run_time, ' seconds')
            print('Sleep 2 minutes')
            time.sleep(120)


if __name__ == "__main__":
    Github_token = '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'
    api = "https://api.github.com/graphql"
    language_list = ['JavaScript', 'Python', 'Java', 'TypeScript', 'C#', 'PHP', 'C++', 'Shell', 'C', 'Ruby']  # 'JavaScript', 'Python', 'Java', 'TypeScript', 'C#', 'PHP', 'C++', 'Shell', 'C', 'Ruby'
    for language in language_list:
        start_download(Github_token, language)
