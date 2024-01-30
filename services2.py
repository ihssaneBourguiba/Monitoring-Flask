from pysnmp.hlapi import *

def get_memory(target, community, storage_index):
    memory_storage_oid = f'.1.3.6.1.2.1.25.2.3.1.5.{storage_index}'
    memory_usage_oid = f'.1.3.6.1.2.1.25.2.3.1.6.{storage_index}'
    memory_free_oid = f'.1.3.6.1.2.1.25.2.3.1.7.{storage_index}'

    storage, usage, free = get(target, community, memory_storage_oid), get(target, community, memory_usage_oid), get(target, community, memory_free_oid)
    return storage, usage, free

def get_disk(target, community, disk_index):
    disk_storage_oid = f'.1.3.6.1.2.1.25.2.3.1.4.{disk_index}'
    disk_usage_oid = f'.1.3.6.1.2.1.25.2.3.1.6.{disk_index}'
    disk_free_oid = f'.1.3.6.1.2.1.25.2.3.1.7.{disk_index}'

    storage, usage, free = get(target, community, disk_storage_oid), get(target, community, disk_usage_oid), get(target, community, disk_free_oid)
    return storage, usage, free

def get(target, community, oid):
    error_indication, error_status, error_index, var_binds = next(
        getCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((target, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )
    )

    if error_indication:
        return f'Error: {error_indication}'
    if error_status:
        return f'Error: {error_status.prettyPrint()} at {error_index and var_binds[int(error_index)-1] or "?"}'

    return var_binds[0][1]

def bytes_to_gb(bytes_value):
    try:
        return float(bytes_value) / (1024 ** 3)  # Convert bytes to gigabytes
    except (TypeError, ValueError):
        return 'N/A'

if __name__ == "__main__":
    target_ip = '127.0.0.1'
    snmp_community = 'public'
    memory_index = 1  # Replace with the appropriate memory index
    disk_index = 36  # Replace with the appropriate disk index

    memory_storage, memory_usage, memory_free = get_memory(target_ip, snmp_community, memory_index)
    disk_storage, disk_usage, disk_free = get_disk(target_ip, snmp_community, disk_index)

    print(f'Memory Storage: {bytes_to_gb(memory_storage)} GB')
    print(f'Memory Usage: {bytes_to_gb(memory_usage)} GB')
    print(f'Memory Free: {bytes_to_gb(memory_free)} GB')

    print(f'Disk Storage: {bytes_to_gb(disk_storage)} GB')
    print(f'Disk Usage: {bytes_to_gb(disk_usage)} GB')
    print(f'Disk Free: {bytes_to_gb(disk_free)} GB')
