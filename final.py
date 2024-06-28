import requests
from helpers import disk_params
import json
import time
from datetime import datetime, timedelta
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()


# Replace these variables with your Zabbix server details and credentials
ZABBIX_URL = os.getenv("ZABBIX_URL", 'http://10.100.116.112/api_jsonrpc.php')
ZABBIX_USER = os.getenv("ZABBIX_USER",'Admin')
ZABBIX_PASSWORD = os.getenv("ZABBIX_PASSWORD",'Bcs@12345$#$')

# Function to make API calls
def zabbix_api(method, params):
    headers = {'Content-Type': 'application/json-rpc'}
    data = {
        'jsonrpc': '2.0',
        'method': method,
        'params': params,
        'auth': auth_token,
        'id': 1
    }
    response = requests.post(ZABBIX_URL, headers=headers, data=json.dumps(data))
    return response.json()

# Step 1: Authenticate and get the auth token
auth_params = {
    'username': ZABBIX_USER,
    'password': ZABBIX_PASSWORD
}
auth_data = {
    'jsonrpc': '2.0',
    'method': 'user.login',
    'params': auth_params,
    'id': 1
}
auth_response = requests.post(ZABBIX_URL, headers={'Content-Type': 'application/json-rpc'}, data=json.dumps(auth_data))
# print(auth_response.json())
auth_token = auth_response.json().get('result')
print("auth check")
# auth_token


HOST_GROUP_NAME = os.getenv("HOST_GROUP_NAME", "Linux servers")
TIME_PERIOD = int(os.getenv("TIME_PERIOD", 2)) * 3600 #seconds

print(f"HOST_GROUP_NAME: {HOST_GROUP_NAME}")
print(f"TIME_PERIOD: {TIME_PERIOD}")
# Step 2: Get the host group ID
host_group_params = {
    'filter': {'name': [HOST_GROUP_NAME]},
    'output': ['groupid']
}
host_group_response = zabbix_api('hostgroup.get', host_group_params)
host_group_id = host_group_response['result'][0]['groupid']

# Step 3: Get hosts in the specified host group
host_params = {
    'groupids': host_group_id,
    'output': ['hostid', 'host'],
    'selectInterfaces': ['interfaceid', 'ip']
}
host_response = zabbix_api('host.get', host_params)
print("host check")
# host_response


hostsAndIPs = {}
for host in host_response['result']:
    hostsAndIPs[host['hostid']] = host['interfaces'][0]['ip']
host_df = pd.DataFrame(list(hostsAndIPs.items()), columns=['hostid', 'ip_address'])
host_df["host_name"] = host_df["hostid"].apply(lambda x: [host['host'] for host in host_response['result'] if host['hostid'] == x][0])
# host_df


cpu_params = {
    "output": "extend",
        "hostids": list(hostsAndIPs.keys()),
        "with_triggers": True,
        "search": {
            "key_": "system.cpu"
        },
        "sortfield": "name"
}
mem_params = {
    "output": "extend",
        "hostids": list(hostsAndIPs.keys()),
        "with_triggers": True,
        "search": {
            "key_": "vm.memory.util"
        },
        "sortfield": "name"
}
print("cpu and mem check")

# disk_response_c = zabbix_api("item.get", disk_params("C", hostsAndIPs))
# disk_response_d= zabbix_api("item.get", disk_params("D", hostsAndIPs))
cpu_response = zabbix_api('item.get', cpu_params)
mem_response = zabbix_api('item.get', mem_params)


# disk_df_c = pd.DataFrame(disk_response_c['result'], columns=['itemid', 'name', 'key_', 'hostid'])
# disk_df_d = pd.DataFrame(disk_response_d['result'], columns=['itemid', 'name', 'key_', 'hostid'])
cpu_df = pd.DataFrame(cpu_response['result'], columns=['itemid', 'name', 'key_', 'hostid'])
mem_df = pd.DataFrame(mem_response['result'], columns=['itemid', 'name', 'key_', 'hostid'])


# disk_df_c['ip'] = disk_df_c['hostid'].apply(lambda x: hostsAndIPs[x])
# disk_df_d['ip'] = disk_df_d['hostid'].apply(lambda x: hostsAndIPs[x])
cpu_df['ip'] = cpu_df['hostid'].apply(lambda x: hostsAndIPs[x])
mem_df['ip'] = mem_df['hostid'].apply(lambda x: hostsAndIPs[x])
# mem_df
print("disk check")

cpu_history_params = {
    'output': 'extend',
    'history': 0,
    'itemids': [item['itemid'] for item in cpu_response['result']],
    'sortfield': 'clock',
    'sortorder': 'DESC',
    "time_from": int(datetime.now().timestamp()) - TIME_PERIOD,
    'time_till': int(datetime.now().timestamp())
}
cpu_history_response = zabbix_api('history.get', cpu_history_params)
cpu_hist_df = pd.DataFrame(cpu_history_response["result"])
# cpu_hist_df
print("cpu history check")

mem_history_params = {
    'output': 'extend',
    'history': 0,
    'itemids': [item['itemid'] for item in mem_response['result']],
    'sortfield': 'clock',
    'sortorder': 'DESC',
    "time_from": int(datetime.now().timestamp()) - TIME_PERIOD,
    'time_till': int(datetime.now().timestamp())
}
mem_history_response = zabbix_api('history.get', mem_history_params)
mem_hist_df = pd.DataFrame(mem_history_response["result"])
print("mem history check")

# diskC_history_params = {
#     'output': 'extend',
#     'history': 0,
#     'itemids': [item['itemid'] for item in disk_response_c['result']],
#     'sortfield': 'clock',
#     'sortorder': 'DESC',
#     "time_from": int(datetime.now().timestamp()) - TIME_PERIOD,
#     'time_till': int(datetime.now().timestamp())
# }

# diskC_history_response = zabbix_api('history.get', diskC_history_params)
# diskC_hist_df = pd.DataFrame(diskC_history_response["result"])
# print("diskC history check")

# diskD_history_params = {
#     'output': 'extend',
#     'history': 0,
#     'itemids': [item['itemid'] for item in disk_response_d['result']],
#     'sortfield': 'clock',
#     'sortorder': 'DESC',
#     "time_from": int(datetime.now().timestamp()) - TIME_PERIOD,
#     'time_till': int(datetime.now().timestamp())
# }

# diskD_history_response = zabbix_api('history.get', diskD_history_params)
# diskD_hist_df = pd.DataFrame(diskD_history_response["result"])
# print("diskD history check")

cpu_hist_df['value'] = pd.to_numeric(cpu_hist_df['value'], errors='coerce')
cpu_mean_df = cpu_hist_df.groupby('itemid')['value'].mean()
cpu_max_df = cpu_hist_df.groupby('itemid')['value'].max()
# cpu_max_df
# Convert Series to DataFrame
cpu_mean_df = cpu_mean_df.to_frame('cpu_mean')
cpu_max_df = cpu_max_df.to_frame('cpu_max')
print("cpu mean and max check")

# Reset index to make 'itemid' a column
cpu_mean_df.reset_index(level=0, inplace=True)
cpu_max_df.reset_index(level=0, inplace=True)

# Merge DataFrames
cpu_merged_df = pd.merge(cpu_mean_df, cpu_max_df, on='itemid')
cpu_merged_df = pd.merge(cpu_merged_df, cpu_df, on='itemid')
print("cpu merged check")
# cpu_merged_df


mem_hist_df['value'] = pd.to_numeric(mem_hist_df['value'], errors='coerce')
mem_mean_df = mem_hist_df.groupby('itemid')['value'].mean()
mem_max_df = mem_hist_df.groupby('itemid')['value'].max()
# Convert Series to DataFrame
mem_mean_df = mem_mean_df.to_frame('mem_mean')
mem_max_df = mem_max_df.to_frame('mem_max')
print("mem mean and max check")

# Reset index to make 'itemid' a column
mem_mean_df.reset_index(level=0, inplace=True)
mem_max_df.reset_index(level=0, inplace=True)

# Merge DataFrames
mem_merged_df = pd.merge(mem_mean_df, mem_max_df, on='itemid')
mem_merged_df = pd.merge(mem_merged_df, mem_df, on='itemid')
print("mem merged check")

# diskC_hist_df['value'] = pd.to_numeric(diskC_hist_df['value'], errors='coerce')
# diskC_mean_df = diskC_hist_df.groupby('itemid')['value'].mean()
# diskC_max_df = diskC_hist_df.groupby('itemid')['value'].max()
# # Convert Series to DataFrame
# diskC_mean_df = diskC_mean_df.to_frame('diskC_avg')
# diskC_max_df = diskC_max_df.to_frame('diskC_max')
# diskC_mean_df.reset_index(level=0, inplace=True)
# diskC_max_df.reset_index(level=0, inplace=True)
# diskC_merged_df = pd.merge(diskC_mean_df, diskC_max_df, on='itemid')
# diskC_merged_df = pd.merge(diskC_merged_df, disk_df_c, on='itemid')
# print("diskC merged check")

# diskD_hist_df['value'] = pd.to_numeric(diskD_hist_df['value'], errors='coerce')
# diskD_mean_df = diskD_hist_df.groupby('itemid')['value'].mean()
# diskD_max_df = diskD_hist_df.groupby('itemid')['value'].max()
# # Convert Series to DataFrame
# diskD_mean_df = diskD_mean_df.to_frame('diskD_avg')
# diskD_max_df = diskD_max_df.to_frame('diskD_max')
# diskD_mean_df.reset_index(level=0, inplace=True)
# diskD_max_df.reset_index(level=0, inplace=True)
# diskD_merged_df = pd.merge(diskD_mean_df, diskD_max_df, on='itemid')
# diskD_merged_df = pd.merge(diskD_merged_df, disk_df_d, on='itemid')
# print("diskD merged check")


# mem_merged_df

# Merge cpu and memory DataFrames
merged_df = pd.merge(cpu_merged_df, mem_merged_df, on='hostid', suffixes=('_cpu', '_mem'))
# merged_df = pd.merge(merged_df, diskC_merged_df, on='hostid')
# merged_df = pd.merge(merged_df, diskD_merged_df, on='hostid')
print("merged check")

# Merge with host DataFrame
# host_df = pd.merge(host_df, merged_df, left_on='itemid', right_on='itemid')

# host_df
merged_df = merged_df[['hostid','ip_cpu', 'cpu_mean', 'cpu_max', 'mem_mean', 'mem_max']]
merged_df = merged_df.rename(columns={'ip_cpu': 'server', 'cpu_mean': 'cpu_avg', 'mem_mean' : 'memory_avg', 'mem_max' : 'memory_max'})
# merged_df

merged_df['cpu_avg'] = merged_df['cpu_avg'].round(0).astype(int)
merged_df['cpu_max'] = merged_df['cpu_max'].round(0).astype(int)
merged_df['memory_avg'] = merged_df['memory_avg'].round(0).astype(int)
merged_df['memory_max'] = merged_df['memory_max'].round(0).astype(int)
# merged_df['diskC_avg'] = merged_df['diskC_avg'].round(1)
# merged_df['diskC_max'] = merged_df['diskC_max'].round(1)
# merged_df['diskD_avg'] = merged_df['diskD_avg'].round(1)
# merged_df['diskD_max'] = merged_df['diskD_max'].round(1)
merged_df["date"] = datetime.now().date()
merged_df["date"] = merged_df["date"].apply(lambda x: x.strftime('%d-%m-%Y'))
two_hours_ago = datetime.now() - timedelta(hours=TIME_PERIOD/3600)
merged_df["time"] = f"{two_hours_ago.strftime('%H:%M')} - {datetime.now().strftime('%H:%M')}"

merged_df = pd.merge(merged_df, host_df[['hostid', 'host_name']], on='hostid', how='left')
merged_df = merged_df[['date', 'time', 'server',"host_name", 'cpu_avg', 'cpu_max', 'memory_avg', 'memory_max']]

if (merged_df.empty):
    print("No data found")
    exit(-1)
merged_df.to_csv(f'{HOST_GROUP_NAME}.csv', index=False)

print("Data saved to CSV file")




