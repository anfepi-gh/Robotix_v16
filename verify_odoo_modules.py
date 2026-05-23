import os
import subprocess
import sys

def install_dependencies():
    """Instala automáticamente las librerías necesarias si no están presentes."""
    try:
        import paramiko
    except ImportError:
        print("-> Instalando librería 'paramiko' necesaria para SSH...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko"])
        import paramiko
    return paramiko

paramiko = install_dependencies()

# Configuración basada en SSH.TXT
SSH_HOST = "143.198.65.235"
SSH_USER = "usuario97775"
SSH_PASS = "AX0qU9za9mZ6Td"

# Configuración de Odoo (Ajusta el nombre de tu base de datos)
DB_NAME = "soyrobotix" 
LOCAL_ADDONS_PATHS = [
    r"c:\Desarrollos Locales\Robotix_v16\addons",
    r"/odoo/custom/addons"
]

def get_local_modules(paths):
    modules = set()
    for path in paths:
        if not os.path.exists(path):
            print(f"Advertencia: La ruta {path} no existe.")
            continue
        for folder in os.listdir(path):
            full_path = os.path.join(path, folder)
            if os.path.isdir(full_path):
                # Un módulo de Odoo se identifica por tener un __manifest__.py o __openerp__.py
                if "__manifest__.py" in os.listdir(full_path) or "__openerp__.py" in os.listdir(full_path):
                    modules.add(folder)
    return modules

def get_installed_modules_ssh():
    installed_modules = []
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS, timeout=10)

        # Comando para consultar módulos instalados en PostgreSQL
        # Usamos -A y -t para obtener solo los nombres sin formato de tabla
        query = f"psql -d {DB_NAME} -A -t -c \"SELECT name FROM ir_module_module WHERE state = 'installed'\""
        
        stdin, stdout, stderr = ssh.exec_command(query)
        output = stdout.read().decode().splitlines()
        error = stderr.read().decode()

        if "error" in error.lower() or "fatal" in error.lower():
            print(f"Error de base de datos en el servidor: {error.strip()}")
            return []
        
        installed_modules = [line.strip() for line in output if line.strip() and not line.startswith('row')]
        ssh.close()
    except Exception as e:
        print(f"Error de conexión: {e}")
    
    return installed_modules

def verify():
    if DB_NAME == "nombre_de_tu_base_de_datos":
        print("Error: Por favor, edita el script y cambia 'nombre_de_tu_base_de_datos' por el nombre real.")
        return

    print("-" * 50)
    print("--- Iniciando verificación de módulos Odoo ---")
    
    local_modules = get_local_modules(LOCAL_ADDONS_PATHS)
    print(f"Módulos detectados localmente: {len(local_modules)}")

    installed_on_server = get_installed_modules_ssh()
    if not installed_on_server:
        print("No se pudo obtener la lista de módulos del servidor.")
        return

    print(f"Módulos instalados en el servidor: {len(installed_on_server)}")
    print("-" * 50)

    not_installed = [m for m in local_modules if m not in installed_on_server]

    if not_installed:
        print("ATENCIÓN: Los siguientes módulos están en tus carpetas pero NO están instalados en el servidor:")
        for m in not_installed:
            print(f"  [ ] {m}")
    else:
        print("¡Todo en orden! Todos los módulos locales están instalados en el servidor.")

if __name__ == "__main__":
    verify()