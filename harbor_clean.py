#!/usr/bin/env python3.8

### This script requires a repository with a list of component versions. ( Use get_component_version.py for create repo with component versions)

### Example dev.txt
#   a:1
#   b:2
#   prod.txt
#   a:3
#   b:3
#####################


import shutil
import requests
import json
import re
from git import Repo
import os
from hurry.filesize import size

class INIT_REPO():
    registry = "harbor.com"
    project = "my-project"
    repo_url = f"https://{registry}/api/v2.0/projects/{project}/repositories"
    sizing_url = f"https://{registry}/api/v2.0/projects/{project}/summary"
    user = "user_name"
    password = "password"
    git_repo = f"you_repo_url"
    clone_dir = "/srv/clone"

repos = ['you_rep1', 'you_rep2']
harborMap = {}
gitlabMap = {}
gitlabMapDev = {}
gitlabMapTest = {}
gitlabMapProd = {}
finalMap = {}
file_name = ['dev', 'test', 'prod']
init_repo = INIT_REPO()

def send_request(url, user, password, method):
    if method == 'GET':
        r = requests.get(url = url, auth=(user, password))
        data = r.json()
        return data
    elif method == 'DELETE':
        print(f"[+] Send delete to {url}")
        requests.delete(url = url, auth=(user, password))
    else:
        print(f"{method} is not supported.")

def clone_repo(repo, dir):
    shutil.rmtree(dir)
    Repo.clone_from(repo, dir)

def create_map(map, key, value):
    map[key] = value
    return map

def create_map_from_file(file, map):
    f = open(file, 'r')
    for line in f:
        component = line.strip().split(':')[0]
        version = line.strip().split(':')[1]
        if component not in map:
            map[component] = [version]
        elif type(map[component]) == list:
            map[component].append(version)
        else:
            map[component] = [map[component], version]
    f.close()
    return map

def compare_map(gitlab_map):
    for app, f_value in finalMap.items():
        if app in gitlab_map.keys():
            for f_version in f_value:
                if f_version.split() == gitlab_map[app]:
                    finalMap[app].remove(f_version)

def get_current_space():
    response = send_request(init_repo.sizing_url, init_repo.user, init_repo.password, "GET")
    data = response
    quota = str(data['quota'])
    quota_parser = str(re.findall(r'\d+', quota))
    removed_char = ",[]'"
    for char in removed_char:
        quota_parser = quota_parser.replace(char, "")
    used_quota = int(quota_parser.split()[1])
    return used_quota

def harbor_space_diff(space_before, space_after):
    result = space_before - space_after
    print("Cleaned: " + size(result))
                    
for repo in repos:
    tags_url = f"https://{init_repo.registry}/api/v2.0/projects/{init_repo.project}/repositories/{repo}/artifacts"
    full_tags = send_request(tags_url, init_repo.user, init_repo.password, "GET")
    convert_tags_type =''.join(map(str,full_tags))
    tags = re.findall(r'\d{1}\.\d{1}-\d+', convert_tags_type)
    harborMap = create_map(harborMap, repo, tags)

clone_repo(init_repo.git_repo, init_repo.clone_dir)

for file in file_name:
    create_map_from_file(f"/srv/clone/{file}.txt", gitlabMap)
    if file == 'dev':
        create_map_from_file(f"/srv/clone/{file}.txt", gitlabMapDev)
    elif file == 'test':
        create_map_from_file(f"/srv/clone/{file}.txt", gitlabMapTest)
    elif file == 'prod':
        create_map_from_file(f"/srv/clone/{file}.txt", gitlabMapProd)

finalMap = gitlabMap.copy()
finalMap.update(harborMap)
compare_map(gitlabMapDev)
compare_map(gitlabMapTest)
compare_map(gitlabMapProd)

for k, v in list(finalMap.items()):
    if len(v) == 0:
        del finalMap[k]
    elif k == '':
        del finalMap[k]
    elif k in ('rep1', 'rep2'):
        del finalMap[k]
print("Next version will be deleted")
print("#" * 30)
for k, v in finalMap.items():
    print(k,v)
print("#" * 30)
print("Do you want proceed?(y/n): ")
answer = input()
if answer == 'y' or answer == 'Y':
    space_before = get_current_space()
    for key, value in finalMap.items():
        for version in value:
            delete_url = f"https://{init_repo.registry}/api/v2.0/projects/{init_repo.project}/repositories/{key}/artifacts/{version}"
            send_request(delete_url, init_repo.user, init_repo.password, "DELETE")
            print(f"[+] Delete artifact {key}:{version}")
    space_after = get_current_space()
    harbor_space_diff(space_before, space_after)
else:
    print("Exit script")