class Crypt:
    

    def __init__(self, **kwargs) -> None:
        pass

    def encrypt(self,  clear_text:str) -> str:
        """
        加密
        """
        cipher_text = clear_text
        return cipher_text


    def decrypt(self, cipher_text: str) -> str:
        """
        解密
        """
        clear_text = cipher_text
        return clear_text


crypt = Crypt()


__all__ = ['crypt']