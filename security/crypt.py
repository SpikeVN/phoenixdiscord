import base64
import os

from Crypto.Cipher import AES


def get_cipher():
    return AES.new(
        bytes(os.environ["credentials_encrypt_key"], "utf8"),
        AES.MODE_EAX,
        nonce=base64.b64decode(os.environ["credentials_encrypt_nonce"]),
    )
