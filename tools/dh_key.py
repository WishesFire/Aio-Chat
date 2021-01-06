from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from cryptography.fernet import Fernet
import base64


async def get_base_ct(data):
    from_js_bin = base64.b64decode(data)
    nonce = from_js_bin[:8]
    ciphertext = from_js_bin[8:]
    return nonce, ciphertext


async def encrypt_message_cbc(key, data):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_byte = cipher.encrypt(pad(data, AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_byte).decode('utf-8')
    return ct, iv


async def decrypt_message_cbc(ciphertext, key, iv):
    ct = base64.b64decode(ciphertext)
    iv = base64.b64decode(iv)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt


async def decrypt_base(token, key):
    f = Fernet(key)
    try:
        token = token.encode()
    except AttributeError:
        pass

    return f.decrypt(token)