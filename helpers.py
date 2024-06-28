

def disk_params(disk_drive, hostsAndIPs):
    return {
        "output": "extend",
        "hostids": list(hostsAndIPs.keys()),
        "with_triggers": True,
        "search": {
            "key_": f'vfs.fs.size[{disk_drive}:,pused]'
        },
        "sortfield": "name"
    }
