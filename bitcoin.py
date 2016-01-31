"""
Bitcoin related functions.

Some code inspired by
https://github.com/bitpay/bitpay-python/blob/master/bitpay/key_utils.py

"""
import binascii
import hashlib

import ecdsa


def _generate_public_key():
    """
    Generate a master public key.
    """
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    return vk.to_string()


def _compress_key(key):
    """
    Return a compressed representation of the key.
    """
    hexkey = binascii.hexlify(key)
    intval = int(hexkey, 16)
    prefix = b'02' if intval % 2 == 0 else b'03'
    return binascii.unhexlify(prefix + hexkey[:64])


def _hash160(data):
    """
    The Hash160 function is defined as `ripemd160(sha256(data))`.
    """
    sha256 = hashlib.new('sha256')
    ripemd160 = hashlib.new('ripemd160')

    sha256.update(data)
    step1 = sha256.digest()

    ripemd160.update(step1)
    step2 = ripemd160.digest()

    return step2


def _checksum(hexdigest):
    """
    Calculate the checksum: `sha256(sha256(digest))[:8]`
    """
    step1 = hashlib.sha256(binascii.unhexlify(hexdigest)).digest()
    step2 = hashlib.sha256(step1).hexdigest()
    return step2[:8]


def _encode58(string, int_val, chars):
    """
    Recursive encoding function. Used by `_base58encode`.
    """
    if int_val == 0:
        return string
    else:
        new_val, rem = divmod(int_val, 58)
        new_string = (chars[rem]) + string
        return _encode58(new_string, new_val, chars)


def _base58encode(hexdata):
    """
    Do Base58 encoding of hex data.
    """
    chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    int_val = int(hexdata, 16)
    encoded = _encode58("", int_val, chars)
    return encoded


def generate_sin():
    """
    Generate a bitcion SIN (Secure Identity Number).

    See https://en.bitcoin.it/wiki/Identity_protocol_v1#Creating_a_SIN for more
    details.

    """
    prefix = '0F'  # Always 0x0f
    sin_type = '02'  # Ephemeral type
    pubkey = _generate_public_key()
    compressed_key = _compress_key(pubkey)
    digest = _hash160(compressed_key)
    full_hexdigest = prefix + sin_type + binascii.hexlify(digest).decode()
    checksum = _checksum(full_hexdigest)
    return _base58encode(full_hexdigest + checksum)
