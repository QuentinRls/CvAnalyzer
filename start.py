#!/usr/bin/env python3
"""
Script de démarrage intelligent qui trouve la bonne commande Python
"""
import subprocess
import sys
import os

def find_python():
    """Trouve la commande Python disponible"""
    commands = ['python3', 'python', 'python3.9', 'python3.8']
    
    for cmd in commands:
        try:
            result = subprocess.run([cmd, '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Trouvé Python: {cmd}")
                print(f"Version: {result.stdout.strip()}")
                return cmd
        except FileNotFoundError:
            continue
    
    print("❌ Aucune commande Python trouvée")
    sys.exit(1)

if __name__ == "__main__":
    python_cmd = find_python()
    
    # Exécuter main.py avec la bonne commande Python
    print(f"🚀 Démarrage avec: {python_cmd} main.py")
    
    try:
        subprocess.run([python_cmd, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        sys.exit(1)
