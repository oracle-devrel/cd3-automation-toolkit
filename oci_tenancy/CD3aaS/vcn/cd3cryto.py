from cryptography.fernet import Fernet
from django.conf import settings
import os


def generate_key():
    key = Fernet.generate_key()
    if not os.path.exists("secret.key"):
        with open("secret.key", "wb") as key_file:
            key_file.write(key)


def load_key():
    return open(os.path.join(os.getcwd(), "vcn", "secret.key"), "rb").read()


class Cd3Crypto:
    def __init__(self, key):
        self.key = key

    def encrypt_private_key(self):
        f = Fernet(load_key())
        encoded_message = self.key.Key_File.encode('utf-8')
        crypt_message = f.encrypt(encoded_message)
        user = self.key.Username.replace(' ', '_')
        file_path = self.key.Tenancy_Name + '-' + self.key.Stack_Name + '-' + 'private_key.bin'
        try:
            with open(os.path.join(settings.MEDIA_ROOT, user, "confidential", file_path), 'wb') as file_object:
                file_object.write(crypt_message)
                file_location = os.path.join(settings.MEDIA_ROOT, user, "confidential", file_path)
                return file_location
        except FileNotFoundError:
            print("File not created")

    def decrypt_private_key(self):
        f = Fernet(load_key())
        try:
            with open(self.key.Key_File, 'rb') as file_object:
                for line in file_object:
                    encrypted = line
            decoded_message = f.decrypt(encrypted)
            return decoded_message.decode('utf-8')
        except FileNotFoundError:
            print("File not created")


if __name__ == "__main__":
    generate_key()
