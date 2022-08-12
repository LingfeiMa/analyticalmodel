from git import Repo
from git.objects.commit import Commit
from git import Diff
import re
import json
import os
import requests

def get_commit_history(repo: Repo,filename:str=None):
    git_ = repo.git
    initial_log = git_.log("--pretty=oneline",filename)
    #查看本地某个 tag 的详细信息：git show <tagName>
    #查看本地所有 tag：git tag 或者 git tag -l
    allTag = git_.tag(filename)
    tagList = allTag.split("\n")
    tagCounts = len(tagList)
    hash_version = {}
    for t in tagList:
        tagDetailList = git_.show(t).split("\n")
        h = tagDetailList[0].split(" ")[1]
        if(h in hash_version):
            hash_version[h].append(t)
        else:
            hash_version[h] = []
            hash_version[h].append(t)
    hash=[]
    for line in initial_log.split("\n"):
        hash.append(line.split(" ")[0])
    return hash,tagCounts,hash_version

#def get_changed_lines(res):
    #rule1 = re.compile('^\+',re.M)
    #rule2 = re.compile('^\-',re.M)
    #rule3 = re.compile('^\+\+\+')
    #count1 = re.findall(rule1,res)
    #count2 = re.findall(rule2,res)
    #return len(count1),len(count2)

def write_jsonFile(projectName,response_metrics_ordered,path):
    f = open(f"./{path}/{projectName}.json", 'w', encoding='utf-8')
    json.dump(response_metrics_ordered, f, indent=4, ensure_ascii=False)

def get_commits(base):
    repo = Repo(base)
    # 传入仓库，得到hash列表
    hash_list, tagCounts, hash_version = get_commit_history(repo)
    commits = []
    for hash in hash_list:
        c = repo.commit(hash)
        print(c)
        commit = {'hash': c.hexsha,
                  'message': c.message,
                  'authors': c.author.name,
                  'author_email': c.author.email,
                  'author_date': str(c.authored_datetime),
                  'committer': c.committer.name,      # + " <" + c.committer.email + ">",
                  'committer_email': c.committer.email,
                  'committer_date': str(c.committed_datetime),
                  "parent": len(c.parents),
                  "changed_files_detail": dict(c.stats.files),
                  'changes': dict(c.stats.total),
                  'total_versions': tagCounts
                  }
        if(hash in hash_version):
            commit['version'] = hash_version[hash]
            print(hash_version[hash])
        else:
            commit['version'] = []
        commits.append(commit)
        print(commit)
        #write_jsonFile(file, commits, 'origin_data')
    return commits


if __name__ =="__main__":
    Base = "./items"
    #Base2 = 'https://api.github.com/repos/'
    # fileName = os.listdir(Base)
    #遍历所有的文件
    #https://api.github.com/repos/mybatis/spring/commits/966fd6563bcb9a641025b160d8c12512ac4c3ea7
    # for file in fileName:
    file = 'MaLiang'
    base = Base + '/' + file
        #commits, row_data = get_commit_detail(base1,base2)
    origin_data = get_commits(base)
        #write_jsonFile(file, commits, 'out_put_json')
    write_jsonFile(file, origin_data, 'commit_data')