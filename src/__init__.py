from hashids import Hashids

_hashids = Hashids(salt="your-key", min_length=4)


def encode_user_id(user_id: int) -> str:
    return _hashids.encode(user_id)


def decode_user_id(encoded_value: str) -> int:
    return _hashids.decode(encoded_value)[0]

print(encode_user_id(123))

print(decode_user_id(encode_user_id(123)))