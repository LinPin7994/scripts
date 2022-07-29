#!/usr/bin/env python3.8

### Namespace dev and test choose for examples, you can modify it

import psycopg2
import argparse
from kubernetes import client, config
import base64

parser = argparse.ArgumentParser(description="Drop postgres database")
parser.add_argument("-n", dest="ns", required=True, help="current namespace")
parser.add_argument("-db", dest="dat_name", required=True, help="database name")
parser.add_argument("-config", dest="kubeconfig", required=True, help="kubectl config")

args = parser.parse_args()

postgres_host = "You host"
postgres_user = "User with superuser access"
postgres_port_dev = "your port"
postgres_port_test = "yout port"

def open_db_connect(host, user, password, port, database):
    conn = psycopg2.connect(dbname=database, user=user, password=password, host=host, port=port)
    return conn

def get_postgres_root_password(ns, secret_name):
    v1 = client.CoreV1Api()
    secret = v1.read_namespaced_secret(secret_name, ns).data['you_key']
    secret = base64.b64decode(secret).decode('utf-8')
    return secret

def drop_database(open_pg_session, database_to_delete):
    open_pg_session.autocommit = True
    drop_session = f''' SELECT pg_terminate_backend (pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{database_to_delete}'; '''
    drop_database = f''' DROP database {database_to_delete}; '''
    cursor = open_pg_session.cursor()
    cursor.execute(drop_session)
    cursor.execute(drop_database)
    cursor.execute("select datname from pg_database;")
    list_database = cursor.fetchall()
    if (database_to_delete,) not in list_database:
        print(f"[+] Database {database_to_delete} deleted.")
    else:
        print(f"[ERROR] Database {database_to_delete} not deleted. Run script again!")
    cursor.close()
    open_pg_session.close()

def main():
    if args.ns == "dev":
        config.load_kube_config(config_file=args.kubeconfig)
        postgres_root_password = get_postgres_root_password(args.ns, "secret_name_for_postgres_password")
        open_pg_session = open_db_connect(postgres_host, postgres_user, postgres_root_password, postgres_port_dev, "postgres")
        drop_database(open_pg_session, args.dat_name)
    elif args.ns == "test":
        config.load_kube_config(config_file=args.kubeconfig)
        postgres_root_password = get_postgres_root_password(args.ns, "secret_name_for_postgres_password")
        open_pg_session = open_db_connect(postgres_host, postgres_user, postgres_root_password, postgres_port_test, "postgres")
        drop_database(open_pg_session, args.dat_name)
    else:
        print(f"[+] NS {args.ns} is not supported...")

if __name__ == "__main__":
    main()