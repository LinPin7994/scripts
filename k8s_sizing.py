from kubernetes import client, config
import re
import argparse

regex = re.compile(r'resources.*')
config.load_kube_config()
v1 = client.AppsV1Api()

parser = argparse.ArgumentParser(description="Get k8s sizing info")
subparser = parser.add_subparsers(title='subcommands', description='vaid subcommands', help='Enter get subcommand')
create_parser_get = subparser.add_parser('get', help='get some info from k8s')
create_parser_get.add_argument('command', choices=['replicas', 'sizing'])
create_parser_get.add_argument('-n', '--namespace', help='k8s namespace', dest='ns', required=True)
create_parser_get.set_defaults(func='get')

args = parser.parse_args()


def init_deployment(ns):
    deployment = v1.list_namespaced_deployment(ns)
    return deployment

def get_replicas(ns):
    deployment = init_deployment(ns)
    for item in deployment.items:
        app_name = item.metadata.name
        app_replicas = item.status.replicas
        print(f"{app_name}:{app_replicas}")

def get_sizing(ns):
    deployment = init_deployment(ns)
    for i in deployment.items:
        resources = i.spec.template.spec.containers
        resources =''.join(map(str, resources))
        resources = regex.findall(resources)
        print("%s\t%s" %  (i.metadata.name, resources))

def main():
    if args.command == 'replicas':
        get_replicas(args.ns)
    elif args.command == 'sizing':
        get_sizing(args.ns)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()