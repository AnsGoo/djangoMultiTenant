import base64
from Crypto.Cipher import AES
from Crypto.Util import Padding
from django.conf import settings

SECRET_KEY = settings.SECRET_KEY[33:-1]

class Crypt:
    
    def encrypt(self,  clear_text:str) -> str:
        """
        加密
        """
        aes = AES.new(SECRET_KEY.encode(),AES.MODE_ECB)
        text_b = clear_text.encode()
        pad_text = Padding.pad(text_b,AES.block_size,style='pkcs7')
        encrypt_text = aes.encrypt(pad_text)
        encrypt_text = base64.b64encode(encrypt_text).decode()
        return encrypt_text


    def decrypt(self, cipher_text: str) -> str:
        """
        解密
        """
        aes = AES.new(SECRET_KEY.encode(),AES.MODE_ECB)
        text = base64.b64decode(cipher_text.encode())
        plain_text = aes.decrypt(text)
        # pad后的数据可能在末尾加了字符，避免影响json识别，需进行unpad。
        plain_text = Padding.unpad(plain_text, AES.block_size, style='pkcs7').decode()
        return plain_text


crypt = Crypt()


__all__ = ['crypt']