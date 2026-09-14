import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

def encrypt_data(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    # Aplicar padding PKCS7 requerido para bloques AES
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(plaintext) + padder.finalize()
    
    # Configurar el cifrador AES en modo CBC
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return ciphertext

def decrypt_data(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Remover el padding PKCS7
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded_data) + unpadder.finalize()
    return plaintext

# Ejemplo de prueba rápida para validar el funcionamiento
if __name__ == "__main__":
    # La llave debe ser de 16, 24 o 32 bytes (128, 192 o 256 bits)
    key = os.urandom(32)
    # El IV (Vector de Inicialización) debe ser de 16 bytes para AES
    iv = os.urandom(16)
    
    mensaje_original = b"Prueba de cifrado con AES y criptografia en Python para el laboratorio."
    
    print(f"Mensaje original: {mensaje_original.decode('utf-8')}")
    
    cifrado = encrypt_data(mensaje_original, key, iv)
    print(f"Texto cifrado (bytes): {cifrado}")
    
    descifrado = decrypt_data(cifrado, key, iv)
    print(f"Mensaje descifrado: {descifrado.decode('utf-8')}")