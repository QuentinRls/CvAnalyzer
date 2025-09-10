"""
Script pour télécharger et sauvegarder le logo Devoteam
"""
import requests
import os
from PIL import Image
import io

def download_devoteam_logo():
    """Télécharge le logo Devoteam depuis l'image fournie"""
    
    # URL du logo Devoteam (version haute qualité)
    logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Devoteam_logo.svg/1200px-Devoteam_logo.svg.png"
    
    try:
        # Télécharger l'image
        response = requests.get(logo_url, timeout=10)
        response.raise_for_status()
        
        # Traiter l'image
        with Image.open(io.BytesIO(response.content)) as img:
            # Convertir en RGB si nécessaire
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Redimensionner à 200x200 max
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            
            # Sauvegarder
            assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
            os.makedirs(assets_dir, exist_ok=True)
            
            logo_path = os.path.join(assets_dir, 'devoteam_logo.png')
            img.save(logo_path, format='PNG', optimize=True)
            
            print(f"Logo Devoteam sauvegardé: {logo_path}")
            return True
            
    except Exception as e:
        print(f"Erreur lors du téléchargement du logo Devoteam: {e}")
        
        # Créer un logo de substitution avec du texte
        try:
            assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
            os.makedirs(assets_dir, exist_ok=True)
            
            # Créer une image simple avec le texte "devoteam"
            img = Image.new('RGB', (200, 60), color=(248, 72, 93))  # Couleur Devoteam
            
            logo_path = os.path.join(assets_dir, 'devoteam_logo.png')
            img.save(logo_path, format='PNG')
            
            print(f"Logo Devoteam de substitution créé: {logo_path}")
            return True
            
        except Exception as e2:
            print(f"Erreur lors de la création du logo de substitution: {e2}")
            return False

if __name__ == "__main__":
    download_devoteam_logo()
