#!/usr/bin/env python3
"""Assemble ai-community/v1/index.html from xz+base64 chunks and verify byte-exactness.

Verification gate: decompressed payload size + md5, and the resulting git blob
SHA-1 (git hash-object) must equal the expected published values.
"""
import base64
import hashlib
import lzma
import os
import subprocess
import sys

D = 'ai-community/v1'
PACK = os.path.join(D, '.pack')
N_PARTS = 4
EXPECT_SIZE = 189785
EXPECT_MD5 = 'c0d7ae2fc7d259492a095cc524acc9ba'
EXPECT_BLOB = '49e13f91430aa3031f6f02530d8ff074acc54f0e'

b64 = []
missing = False
for i in range(N_PARTS):
    p = os.path.join(PACK, 'part%d.b64' % i)
    if not os.path.exists(p):
        print('MISSING %s' % p)
        missing = True
        continue
    raw = open(p, 'r', encoding='ascii').read().replace('\n', '').replace('\r', '')
    print('part%d chars=%d md5=%s' % (i, len(raw), hashlib.md5(raw.encode('ascii')).hexdigest()))
    b64.append(raw)

if missing:
    sys.exit('missing chunks; nothing assembled')

payload = lzma.decompress(base64.b64decode(''.join(b64)))
size = len(payload)
md5 = hashlib.md5(payload).hexdigest()
print('payload size=%d md5=%s' % (size, md5))
assert size == EXPECT_SIZE, 'size mismatch: %d != %d' % (size, EXPECT_SIZE)
assert md5 == EXPECT_MD5, 'md5 mismatch: %s != %s' % (md5, EXPECT_MD5)

out = os.path.join(D, 'index.html')
with open(out, 'wb') as f:
    f.write(payload)

blob = subprocess.check_output(['git', 'hash-object', out]).decode().strip()
print('blob sha1=%s expected=%s' % (blob, EXPECT_BLOB))
assert blob == EXPECT_BLOB, 'blob sha1 mismatch'
print('VERIFIED: %s is byte-exact' % out)
