import base64, struct, binascii, sys
try:
  from StringIO import StringIO
except ImportError:
  from io import StringIO, BytesIO

def get_binio(bytes):
  try:
    return StringIO(bytes)
  except TypeError:
    return BytesIO(bytes)

def ppkraw_to_openssh(ppkraw, passphrase = ''):
  lines = [l.strip() for l in ppkraw.strip().split('\n')]
  if lines[0].startswith('PuTTY-User-Key-File-2:'):
    privbin = ''
    pubbin = ''
    comment = ''
    hexmac = False
    for i in range(0,len(lines)):
      if lines[i].startswith('Public-Lines: '):
        pubbin = base64.b64decode(''.join(lines[i+1:int(lines[i][14:])+i+1]))
      elif lines[i].startswith('Private-Lines: '):
        privbin = base64.b64decode(''.join(lines[i+1:int(lines[i][15:])+i+1]))
      elif lines[i].startswith('Private-MAC: '):
        hexmac = lines[i][13:]
      elif lines[i].startswith('Comment: '):
        comment = lines[i][9:].encode()
    if pubbin == '' or privbin == '':
      raise SyntaxError('PPK missing either Public-Lines or Private-Lines')
    #pub decode
    pubio = get_binio(pubbin)
    keytype = pubio.read(struct.unpack('>I', pubio.read(4))[0])
    #hmac check
    if hexmac:
      import hashlib, hmac
      mackey = b"putty-private-key-file-mac-key" + passphrase.encode()
      if len(passphrase) > 0:
        cipherstr = b'aes256-cbc'
        # decrypt privbin
        aes256key = hashlib.sha1(b"\x00\x00\x00\x00"+passphrase.encode()).digest() + hashlib.sha1(b"\x00\x00\x00\x01"+passphrase.encode()).digest()
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        cipher = Cipher(algorithms.AES(aes256key[0:32]), modes.CBC(b"\x00"*16), backend=default_backend())
        decryptor = cipher.decryptor()
        privbin = decryptor.update(privbin) + decryptor.finalize()
      else:
        cipherstr = b'none'
      macbody = b''.join(struct.pack('>I', len(s)) + s for s in [keytype, cipherstr, comment, pubbin, privbin])
      if hmac.HMAC(hashlib.sha1(mackey).digest(),macbody,hashlib.sha1).hexdigest() != hexmac:
        raise ValueError('HMAC mismatch (bad passphrase?)')
    privio = get_binio(privbin)
    if keytype == b'ssh-rsa':
      pubexp = pubio.read(struct.unpack('>I', pubio.read(4))[0])
      modulus = pubio.read(struct.unpack('>I', pubio.read(4))[0])
      #priv decode
      privexp = privio.read(struct.unpack('>I', privio.read(4))[0])
      p = privio.read(struct.unpack('>I', privio.read(4))[0])
      q = privio.read(struct.unpack('>I', privio.read(4))[0])
      iqmp = privio.read(struct.unpack('>I', privio.read(4))[0])
      # we need exponent1 and exponent2, we have everything else
      d = int(binascii.hexlify(privexp), 16)
      e1x = '%X' % (d % int(binascii.hexlify(p), 16))
      e2x = '%X' % (d % int(binascii.hexlify(q), 16))
      #pad and binize
      e1b = binascii.unhexlify((len(e1x) % 2) * '0' + e1x)
      e2b = binascii.unhexlify((len(e1x) % 2) * '0' + e1x)
      #ASN.1! see it's not so bad. lol.
      sequence = b"\x02\x01\x00" + b''.join(b"\x02\x82" + struct.pack('>H', len(s)) + s for s in [modulus, pubexp, privexp, p, q, e1b, e2b, iqmp])
      complete = b"\x30\x82" + struct.pack('>H', len(sequence)) + sequence
      completeb64 = base64.b64encode(complete).decode()
      return "-----BEGIN RSA PRIVATE KEY-----\n" + "\n".join(completeb64[0+i:64+i] for i in range(0, len(completeb64), 64)) + "\n-----END RSA PRIVATE KEY-----\n"
    elif keytype == b'ssh-ed25519':
      pubval = pubio.read(struct.unpack('>I', pubio.read(4))[0])
      prival = privio.read(struct.unpack('>I', privio.read(4))[0])
      pubopenssh = struct.pack('>I', len(keytype)) + keytype + struct.pack('>I', len(pubval)) + pubval
      lastpart = struct.pack('>II', 1, 1) + pubopenssh + struct.pack('>I', len(prival) + len(pubval)) + prival + pubval + struct.pack('>I', len(comment)) + comment
      lastpart = lastpart + b"\x01\x02\x03\x04\x05\x06\x07"[0:8-(len(lastpart) % 8)]
      complete = b"openssh-key-v1\x00\x00\x00\x00\x04none\x00\x00\x00\x04none" + struct.pack('>III', 0, 1, len(pubopenssh)) + pubopenssh + struct.pack('>I', len(lastpart)) + lastpart
      completeb64 = base64.b64encode(complete).decode()
      return "-----BEGIN OPENSSH PRIVATE KEY-----\n" + "\n".join(completeb64[0+i:70+i] for i in range(0, len(completeb64), 70)) + "\n-----END OPENSSH PRIVATE KEY-----\n"

def main():
  """Command line conversion of a PPK file to an OpenSSH file
  python -m puttykeys myprivatekey.ppk [password] > id_rsa"""
  if len(sys.argv) > 1:
    f=open(sys.argv[1],'r')
    ppkraw = f.read()
    f.close()
    if len(sys.argv) > 2:
      sys.stdout.write(ppkraw_to_openssh(ppkraw, sys.argv[2]))
    else:
      sys.stdout.write(ppkraw_to_openssh(ppkraw))
