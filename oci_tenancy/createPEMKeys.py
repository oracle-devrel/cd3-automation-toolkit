from Crypto.PublicKey import RSA
key = RSA.generate(2048)
f = open("oci_demo_api_private.pem", "wb")
f.write(key.exportKey('PEM'))
f.close()

pubkey = key.publickey()
f = open("oci_demo_api_public.pem", "wb")
f.write(pubkey.exportKey('PEM'))
f.close()
