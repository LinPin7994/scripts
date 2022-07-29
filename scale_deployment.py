from kubernetes import client, config
import sys

config.load_kube_config()
v1 = client.AppsV1Api()

try:
    function = sys.argv[1]
    ns = sys.argv[2]
except IndexError:
    print(f"Usage: {sys.argv[0]} <stop|start|restart> <namespace> ")
    sys.exit(1)

deployment = v1.list_namespaced_deployment(ns)

def open_file(file_method):
    if file_method == 'r':
        file = open(f"{ns}-replicas.txt", 'r')
    elif file_method == 'w':
        file = open(f"{ns}-replicas.txt", 'w')
    else:
        print(f"{file_method} is not supported.")
    return file

def stop_deployment(ns):
    file_w = open_file("w")
    for i in deployment.items:
        deployment_info = i.metadata.name + ":" + str(i.status.replicas)
        file_w.write(deployment_info+'\n')
    file_w.close()
    file_r = open_file("r")
    for line in file_r:
        deployment_name = line.split(":")[0]
        scale_response = v1.patch_namespaced_deployment_scale(deployment_name, ns, {'spec': {'replicas': 0}})
        print(scale_response.spec)
    file_r.close()

def start_deployment(ns):
    file_r = open_file("r")
    for line in file_r:
        deployment_name = line.split(":")[0]
        deployment_replicas = int(line.split(":")[1])
        scale_response = v1.patch_namespaced_deployment_scale(deployment_name, ns, {'spec': {'replicas': (deployment_replicas)}})
        print(scale_response.spec)
    file_r.close()

if function == 'stop':
    stop_deployment(ns)
elif function == 'start':
    start_deployment(ns)
elif function == 'restart':
    stop_deployment(ns)
    start_deployment(ns)
else:
    print(f"Function {function} is not supported.")