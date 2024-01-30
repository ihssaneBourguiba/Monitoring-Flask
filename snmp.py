from pysnmp.hlapi import *

def octets_to_go(octets):
    return octets / (1024 ** 3)

def get_snmp_data(ip_address, community_string, oid_list):
    data = {}

    total_cpu_percentage = 0  # Variable pour stocker la somme des pourcentages CPU

    for oid in oid_list:
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(community_string),
                   UdpTransportTarget((ip_address, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid)))
        )

        if errorIndication:
            print(f"Erreur lors de la récupération de l'OID {oid}: {errorIndication}")
        elif errorStatus:
            print(f"Erreur lors de la récupération de l'OID {oid}: {errorStatus.prettyPrint()}")
        else:
            for varBind in varBinds:
                value = varBind[1]
                if oid == "1.3.6.1.2.1.25.2.2.0":
                    # Total RAM en octets
                    total_ram_bytes = int(value)* 4096
                    total_ram_gb = octets_to_go(total_ram_bytes)
                    data["Total Memory"] = f"{total_ram_gb:.2f} GB"
                elif oid == "1.3.6.1.2.1.25.2.3.1.6.1":
                    # Espace disque utilisé en blocs pour le disk 1 (ou "C:")
                    used_disk_blocks_1 = int(value)
                    # Convertir en octets (en supposant que chaque bloc a une taille de 4096 octets)
                    used_disk_bytes_1 = used_disk_blocks_1 * 4096
                    # Convertir en gigaoctets
                    used_disk_gb_1 = octets_to_go(used_disk_bytes_1)
                    data["Used Disk Space 1"] = f"{used_disk_gb_1:.2f} GB"
                elif oid == "1.3.6.1.2.1.25.2.3.1.6.2":
                    # Espace disque utilisé en blocs pour le disk 2 (ou autre disque si nécessaire)
                    used_disk_blocks_2 = int(value)
                    # Convertir en octets (en supposant que chaque bloc a une taille de 4096 octets)
                    used_disk_bytes_2 = used_disk_blocks_2 * 4096
                    # Convertir en gigaoctets
                    used_disk_gb_2 = octets_to_go(used_disk_bytes_2)
                    data["Used Disk Space 2"] = f"{used_disk_gb_2:.2f} GB"
                elif oid.startswith("1.3.6.1.2.1.25.3.3.1.2."):
                    # Charge processeur pour chaque CPU
                    cpu_index = int(oid.split(".")[-1])
                    cpu_percentage_str = value.prettyPrint()
                    # Extraire la partie numérique du pourcentage (éliminer le caractère '%')
                    cpu_percentage = int(cpu_percentage_str.replace("%", ""))
                    data[f"CPU {cpu_index} Usage"] = f"{cpu_percentage}%"
                    total_cpu_percentage += cpu_percentage

    # Normaliser les pourcentages CPU pour que la somme soit égale à 100%
    if total_cpu_percentage > 0:
        for cpu_index in range(6, 14):
            cpu_key = f"CPU {cpu_index} Usage"
            if cpu_key in data:
                normalized_percentage = int(data[cpu_key].replace("%", "")) / total_cpu_percentage * 100
                data[cpu_key] = f"{normalized_percentage:.2f}%"

    return data

