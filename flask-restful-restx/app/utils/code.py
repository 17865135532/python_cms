import uuid


def gen_api_key(num):
    return str(uuid.uuid3(uuid.NAMESPACE_OID, str(num))).replace('-', '')


def gen_secret_key():
    return str(uuid.uuid4()).replace('-', '')


if __name__ == '__main__':
    ak = (gen_api_key(1))
    print(ak, len(ak))
    print(gen_secret_key())
