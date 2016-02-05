import shortuuid
suid = shortuuid.ShortUUID()

def get_short_uuid():
    return suid.uuid()[:7]

