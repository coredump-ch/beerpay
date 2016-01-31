from binascii import hexlify, unhexlify

import pytest
import ecdsa

import bitcoin


TEST_PEM = """
-----BEGIN EC PRIVATE KEY-----
MHQCAQEEIKXVveE0gp92tUV6m3Grc6vCkbZCPoB6ztN09e1zuxDwoAcGBSuBBAAK
oUQDQgAEhEDTyjA6wCSG+EHb53uwTc1M7yaaMFt08HLdUKxq0RJPR40Hs6S+falb
hkjwPMyb7BM3Ab1ljdhinri7R5eTZA==
-----END EC PRIVATE KEY-----
""".strip()
TEST_SIN = 'Tf8MXZi8Nf9VckDhYCoWU7rwh2E8mXTnyZi'


@pytest.fixture
def patched_bitcoin(monkeypatch):
    """
    Always use TEST_PEM when generating a public key.
    """
    sk = ecdsa.SigningKey.from_pem(TEST_PEM)
    vk = sk.get_verifying_key()
    monkeypatch.setattr(bitcoin, '_generate_public_key', lambda: vk.to_string())
    return bitcoin


def test_base58encode():
    assert bitcoin._base58encode('0123456789ABCDE') == 'h1iJWQwqX'
    assert bitcoin._base58encode('0123456789ABCDEF') == 'C3CPq7c8PY'


def test_checksum():
    """
    Test data generated using bitpay library.
    """
    hexdigest = '0F023fa98244c5d38c088048a440253335d745a9ed65'
    checksum = bitcoin._checksum(hexdigest)
    assert checksum == '4d6171ea'


def test_compress_key(patched_bitcoin):
    pk = patched_bitcoin._generate_public_key()
    compressed = patched_bitcoin._compress_key(pk)
    assert hexlify(compressed) == \
           b'028440d3ca303ac02486f841dbe77bb04dcd4cef269a305b74f072dd50ac6ad112'


def test_hash160():
    compressed_key = unhexlify(
        b'028440d3ca303ac02486f841dbe77bb04dcd4cef269a305b74f072dd50ac6ad112'
    )
    assert hexlify(bitcoin._hash160(compressed_key)) == \
            b'76997e34de47c3f6b9d6aaaaa42d2a21bfc14fc7'


def test_generate_sin(patched_bitcoin):
    assert patched_bitcoin.generate_sin() == TEST_SIN
