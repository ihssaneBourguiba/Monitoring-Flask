from pysnmp.hlapi import *

def getMemory():

    target = '127.0.0.1'
    community = 'public'
    memory_storage_oid = '.1.3.6.1.2.1.25.2.3.1.5.1'
    memory_usage_oid = '.1.3.6.1.2.1.25.2.3.1.6.1'

    return(get(target,community,memory_storage_oid),get(target,community,memory_usage_oid))

def get(target,community,oid):
    ErrorIndaction, ErrorStatus, ErrorIndex, varBind=next(
        getCmd(SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((target,161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )
    )
    if ErrorIndaction or ErrorStatus or ErrorIndex :
        return f'error {ErrorIndaction,ErrorStatus,ErrorIndex}'
    return varBind[0][1]

if __name__=='__main__':
    pass