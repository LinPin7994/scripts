from kubernetes import client, config
import sys
import re
from git import Repo
from git import Git
import shutil
import os

try:
    ns = sys.argv[1]
except IndexError:
    print(f"Usage: {sys.argv[0]} <namespace>")
    sys.exit(1)

result_file = f"{ns}.txt"
repo_url = "url_for_repository_with_components_version"
git_clone_dir = "dir_for_clone"

if ns != 'prod_current_namespace':
    config.load_kube_config(config_file='./you_kubeconfig_dev_file')
else:
    config.load_kube_config(config_file='./you_kubeconfig_prod_file')

v1 = client.AppsV1Api()
deployment = v1.list_namespaced_deployment(ns)


def get_component_and_version():
    print(f"[+] Get component version from namespace {ns}...")
    file = open(result_file, 'w')
    char_for_delete = "[']"
    for item in deployment.items:
        image = str(re.findall(r'<address_you_registry.For_example harbor.com/my-project>.*\w', str(item.spec)))
        for char in char_for_delete:
            image = image.replace(char, "")
        if image == "":
            continue
        elif (",") in image:
            full_app = image.split(",")[0]
            full_app = full_app.split("/")[2]
            file.write(full_app + '\n')
        else:
            full_app = image.split("/")[2]
            file.write(full_app + '\n')
    file.close()


def clone_repository(repo, dir):
    print(f"[+] Cloning repository {repo} to {dir}...")
    git_dir_is_exist = os.path.exists(dir)
    if not git_dir_is_exist:
        os.makedirs(dir)
    shutil.rmtree(dir)
    Repo.clone_from(repo, dir, env=dict(GIT_SSH_COMMAND="ssh -i <path_to_ssh_key> -o StrictHostKeyChecking=no"))


get_component_and_version()
clone_repository(repo_url, git_clone_dir)
shutil.copy(result_file, git_clone_dir)
print(f"[+] Push changes to {repo_url}...")
repo = Repo(git_clone_dir)
with repo.git.custom_environment(GIT_SSH_COMMAND="ssh -i <path_to_ssh_key>"):
    repo.git.add(update=True)
    repo.index.commit("Update devops-component-version")
    repo.git.push('origin', 'master')
print("[+] Successfully...")
