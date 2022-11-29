#!/usr/bin/env python3.8

from jira import JIRA, Project, JIRAError
import argparse
import urllib3
import yaml
import re
import requests
import time
from time import sleep
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings()

parser = argparse.ArgumentParser(description="Automation JIRA release. Script set fix version = 1.1-<release_number>")
parser.add_argument("-j", "--jira", dest="ticket", required=True, help="Enter JIRA ticker. CARMA-XXXX. Getting from CI/CD")
parser.add_argument("-t", "--tag", dest="tag", required=True, help="Tag number. Getting from CI/CD.")
parser.add_argument("-n", "--name", dest="app_name", required=True, help="App name. Get from CI/CD")

args = parser.parse_args()

config_file = "/opt/auto_jira_update.yaml"
sprint_custom_field = "customfield_10100"

argocd_dev_url = "https://argocd.domain.ru"
argocd_session_url = "/api/v1/session"
argocd_application_url = "/api/v1/applications/"

timeout = 800
timeout_start = time.time()

def get_credentials(config):
    with open (config, 'r', encoding="utf-8") as file:
        config_yaml = yaml.safe_load(file)
        jira_login = config_yaml["jira"]["login"]
        jira_password = config_yaml["jira"]["password"]
        argocd_login = config_yaml["argocd"]["login"]
        argocd_password = config_yaml["argocd"]["password"]
    return jira_login, jira_password, argocd_login, argocd_password

def send_request(**kwargs):
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    if kwargs['method'] == "TOKEN":
        r = requests.post(url = kwargs['url'] + kwargs['session_url'], json={"username":f"{kwargs['login']}","password":f"{kwargs['password']}"}, verify=False)
        data = r.json()
        data = data['token']
    elif kwargs['method'] == "GET":
        r = requests.get(url = kwargs['url'] + kwargs['app_url'] + kwargs['app'], headers={'Authorization': 'Bearer ' + kwargs['token']}, verify=False)
        data = r.json()
    return data

def switch_jira_task_to_ready_to_install(jira_issue, jira, ticket, app_tag, app_name):
    issue_type = str(jira_issue.fields.issuetype)
    if  issue_type == "Подзадача на разработку":
        try:
            jira.transition_issue(jira_issue, transition="Deployment")
            print(f"[CI_INFO] Jira issue {args.ticket} move to \"Deployment\" status")
            jira.add_comment(ticket, f"Установлено на DEV: {app_name}:{app_tag}")
        except JIRAError as e:
            print(f"[CI_INFO] Jira issue {args.ticket} already in \"Deployment\" status")
    elif issue_type == "Bug ST" or issue_type == "Задача":
        issue_status = str(jira_issue.fields.status)
        if issue_status == "Готово к тестированию":
            jira.transition_issue(jira_issue, transition="Back to Work")
            jira.add_comment(ticket, f"Установлено на DEV: {app_name}:{app_tag}")
            print(f"[CI_INFO] Jira issue {args.ticket} move to \"In progress\" status")
        else:
            try:
                jira.transition_issue(jira_issue, transition="Start Work")
                jira.add_comment(ticket, f"Установлено на DEV: {app_name}:{app_tag}")
                print(f"[CI_INFO] Jira issue {args.ticket} move to \"In progress\" status")
            except JIRAError as e:
                print(f"[CI_INFO] Jira issue {args.ticket} already in \"In progress\" status")
    elif issue_type == "История":
        issue_status = str(jira_issue.fields.status)
        if issue_status == "В работе":
            try:
                jira.transition_issue(jira_issue, transition="Finish Work")
                jira.transition_issue(jira_issue, transition="Approve")
                jira.add_comment(ticket, f"Установлено на DEV: {app_name}:{app_tag}")
            except JIRAError as e:
                print(f"[CI_INFO] Jira issue {args.ticket} already in \"Ready to install\" status")
        else:
            print(f"[CI_ERROR] Unknow status {issue_status}")
    else:
        if str(jira_issue.fields.status) != "К выполнению":
            issue_status = str(jira_issue.fields.status)
            if issue_status == "В работе":
                jira.transition_issue(jira_issue, transition="To review")
                jira.transition_issue(jira_issue, transition="Ready for test")
                jira.transition_issue(jira_issue, transition="Start Testing")
                jira.transition_issue(jira_issue, transition="Ready to Install")
                jira.add_comment(ticket, f"Установлено на DEV: {app_name}:{app_tag}")
            elif issue_status == "Review":
                jira.transition_issue(jira_issue, transition="Ready for test")
                jira.transition_issue(jira_issue, transition="Start Testing")
                jira.transition_issue(jira_issue, transition="Ready to Install")
                jira.add_comment(ticket, f"Установлено на DEV: {app_name}:{app_tag}")
            elif issue_status == "Готово к тестированию":
                jira.transition_issue(jira_issue, transition="Start Testing")
                jira.transition_issue(jira_issue, transition="Ready to Install")
                jira.add_comment(ticket, f"Установлено на DEV: {app_name}:{app_tag}")
            elif issue_status == "Тестирование":
                jira.transition_issue(jira_issue, transition="Ready to Install")
                jira.add_comment(ticket, f"Установлено на DEV: {app_name}:{app_tag}")
            print(f"[CI_INFO] Jira issue {args.ticket} move to \"Ready to Install\" status")
        else:
            print(f"[CI_ERROR] Unknow status {issue_status}")

def get_jira_sprint(jira_issue):
    sprint_name = jira_issue.fields.customfield_10100.pop()
    sprint_name = re.findall(r"name=[^,]*", str(sprint_name))
    sprint_number = ''.join(map(str, sprint_name)).replace("name=", "").replace("Carma.Sprint", "").strip()
    sprint_name = "1.1." + sprint_number
    return sprint_name

def get_current_tag_from_argocd(argocd_user, app_name_in_argocd, argocd_token):
    data = send_request(url=argocd_dev_url, login=argocd_user, app_url=argocd_application_url, app=app_name_in_argocd, method="GET", token=argocd_token)
    app_status = data["status"]["health"]["status"]
    if len(data["status"]["summary"]["images"]) == 1:
        current_app_tag = data["status"]["summary"]["images"][0].replace(f"<you_harbor_url>/<you_rep>/{args.app_name}:", "")
    else:
        current_app_tag = data["status"]["summary"]["images"][1].replace(f"<you_harbor_url>/<you_rep>/{args.app_name}:", "")
        if "<you_harbor_url>/<you_rep>/init-postgres-db" in current_app_tag:
            current_app_tag = data["status"]["summary"]["images"][0].replace(f"sregistry.mts.ru/<you_rep>/{args.app_name}:", "")
    return current_app_tag, app_status

def main():
    app_name_in_argocd = args.app_name.replace("-", "") + "-dev"
    jira_user = get_credentials(config_file)[0]
    jira_password = get_credentials(config_file)[1]
    argocd_login = get_credentials(config_file)[2]
    argocd_password = get_credentials(config_file)[3]
    argocd_token = send_request(url=argocd_dev_url, login=argocd_login, password=argocd_password, method="TOKEN", session_url=argocd_session_url)
    while time.time() < timeout_start + timeout:
        print(f"[CI_INFO] Wait for argocd to do sync...")
        sleep(10)
        current_app_tag = get_current_tag_from_argocd(argocd_login, app_name_in_argocd, argocd_token)[0]
        app_status = get_current_tag_from_argocd(argocd_login, app_name_in_argocd, argocd_token)[1]
        if current_app_tag == args.tag and app_status == "Healthy":
            print(f"[CI_INFO] App {args.app_name} synced")
            break
    current_app_tag = get_current_tag_from_argocd(argocd_login, app_name_in_argocd, argocd_token)[0]
    if current_app_tag == args.tag:
        jira = JIRA(options={'server': 'https://jira.domain.ru', 'verify': False}, auth=(jira_user, jira_password))
        issue = jira.issue(args.ticket)
        switch_jira_task_to_ready_to_install(issue, jira, args.ticket, args.tag, args.app_name)
        sprint_name = get_jira_sprint(issue)
        try:
            jira.create_version(name=sprint_name, project="<you_jira_project>")
            print(f"[CI_INFO] Version of sprint {sprint_name} created.")
        except JIRAError as e:
            print(f"[CI_INFO] Version of sprint {sprint_name} is exist.")
        try:
            issue.update(fields={"fixVersions": [{'name': f'{sprint_name}'}]})
            print(f"[CI_INFO] Set fixVersion {sprint_name} on task {args.ticket}")
        except JIRAError as e:
            print(f"[CI_INFO] FixVersion {sprint_name} already is set.")


if __name__ == "__main__":
    main()`
