"""
Service de recherche et téléchargement de logos d'entreprises
"""
import requests
import io
import logging
from typing import Optional, Tuple
from PIL import Image
import re
import time
from urllib.parse import urlencode, urlparse, quote_plus
import os

logger = logging.getLogger(__name__)

class LogoSearchService:
    """Service pour rechercher et télécharger des logos d'entreprises"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Cache des logos téléchargés
        self.logo_cache = {}
        
        # Dossier de cache local
        self.cache_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logos')
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def clear_cache(self):
        """Vide le cache des logos"""
        try:
            self.logo_cache.clear()
            # Supprimer les fichiers du cache
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.png'):
                    os.remove(os.path.join(self.cache_dir, filename))
            logger.info("Cache des logos vidé")
        except Exception as e:
            logger.warning(f"Erreur lors du vidage du cache: {e}")
    
    def search_company_logo(self, company_name: str) -> Optional[bytes]:
        """
        Recherche et télécharge le logo d'une entreprise
        
        Args:
            company_name: Nom de l'entreprise
            
        Returns:
            Bytes de l'image du logo ou None si non trouvé
        """
        try:
            # Nettoyer le nom de l'entreprise pour la recherche
            clean_name = self._clean_company_name(company_name)
            
            # Créer une clé de cache basée sur le nom original (plus spécifique)
            cache_key = company_name.lower().strip()
            cache_key = re.sub(r'[^\w\s-]', '', cache_key)  # Supprimer caractères spéciaux
            cache_key = re.sub(r'\s+', '_', cache_key)  # Remplacer espaces par underscore
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.png")
            
            if os.path.exists(cache_file):
                logger.info(f"Logo trouvé dans le cache pour {company_name}")
                with open(cache_file, 'rb') as f:
                    return f.read()
            
            if cache_key in self.logo_cache:
                return self.logo_cache[cache_key]
            
            # Recherche du logo dans l'ordre de fiabilité :
            # 1. Clearbit (très fiable et rapide)
            logo_url = self._search_logo_clearbit(company_name)
            
            # 2. Si pas trouvé, essayer DuckDuckGo
            if not logo_url:
                logo_url = self._search_logo_duckduckgo(clean_name)
                
            # 3. Si toujours pas trouvé, méthodes alternatives  
            if not logo_url:
                logo_url = self._search_logo_alternative(clean_name)
            
            if logo_url:
                logo_bytes = self._download_and_process_image(logo_url)
                if logo_bytes:
                    # Sauvegarder dans le cache
                    self.logo_cache[cache_key] = logo_bytes
                    
                    # Sauvegarder sur disque
                    try:
                        with open(cache_file, 'wb') as f:
                            f.write(logo_bytes)
                        logger.info(f"Logo sauvegardé en cache pour {company_name}")
                    except Exception as e:
                        logger.warning(f"Impossible de sauvegarder le logo en cache: {e}")
                    
                    return logo_bytes
            
            logger.warning(f"Aucun logo trouvé pour {company_name}")
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de logo pour {company_name}: {e}")
            return None
    
    def _clean_company_name(self, company_name: str) -> str:
        """Nettoie le nom de l'entreprise pour la recherche (moins agressif)"""
        # Supprimer les caractères spéciaux mais garder plus d'informations
        clean = re.sub(r'[^\w\s-]', '', company_name)
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        # Ne supprimer que les mots vraiment génériques à la fin
        # et seulement s'il y a d'autres mots
        stop_words_end = ['ltd', 'inc', 'corp', 'company', 'co']
        words = clean.split()
        
        if len(words) > 1:  # Seulement si plus d'un mot
            last_word = words[-1].lower()
            if last_word in stop_words_end:
                words = words[:-1]
        
        return ' '.join(words) if words else clean
    
    def _search_logo_duckduckgo(self, company_name: str) -> Optional[str]:
        """
        Recherche via DuckDuckGo Images avec scraping
        """
        try:
            # Construire la requête de recherche
            query = f"{company_name} logo official"
            
            # URL de recherche DuckDuckGo Images  
            search_url = f"https://duckduckgo.com/?q={quote_plus(query)}&t=h_&ia=images&iax=images"
            
            # Headers pour simuler un navigateur
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Première requête pour obtenir le token
            response = self.session.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Extraire le token vqd nécessaire pour l'API images
            vqd_pattern = r'vqd="([^"]+)"'
            vqd_match = re.search(vqd_pattern, response.text)
            
            if not vqd_match:
                logger.warning(f"Token vqd non trouvé pour {company_name}")
                return self._search_logo_alternative(company_name)
            
            vqd = vqd_match.group(1)
            
            # Requête à l'API images de DuckDuckGo
            images_url = "https://duckduckgo.com/i.js"
            params = {
                'l': 'us-en',
                'o': 'json',
                'q': query,
                'vqd': vqd,
                'f': ',,,',
                'p': '1',
                's': '0'
            }
            
            images_response = self.session.get(images_url, headers=headers, params=params, timeout=10)
            images_response.raise_for_status()
            
            images_data = images_response.json()
            
            # Analyser les résultats
            if 'results' in images_data and images_data['results']:
                # Chercher la meilleure image (priorité aux images avec 'logo' dans le nom/URL)
                best_candidates = []
                
                for img in images_data['results'][:20]:  # Limiter à 20 résultats
                    if 'image' in img:
                        image_url = img['image']
                        
                        # Priorité aux URLs contenant 'logo'
                        priority = 0
                        if 'logo' in image_url.lower():
                            priority += 3
                        if any(domain in image_url for domain in ['wikipedia.org', 'wikimedia.org']):
                            priority += 2
                        if any(domain in image_url for domain in ['.com', '.org', '.net']):
                            priority += 1
                            
                        # Éviter les images trop petites ou avec des extensions suspectes
                        if self._is_valid_image_url(image_url):
                            best_candidates.append((priority, image_url))
                
                # Trier par priorité et retourner la meilleure
                if best_candidates:
                    best_candidates.sort(key=lambda x: x[0], reverse=True)
                    best_url = best_candidates[0][1]
                    logger.info(f"Logo trouvé via DuckDuckGo pour {company_name}: {best_url}")
                    return best_url
            
            # Si aucune image trouvée, utiliser la méthode alternative
            logger.info(f"Aucune image DuckDuckGo pour {company_name}, essai méthode alternative")
            return self._search_logo_alternative(company_name)
            
        except Exception as e:
            logger.warning(f"Erreur DuckDuckGo pour {company_name}: {e}")
            return self._search_logo_alternative(company_name)
    
    def _score_logo_candidate(self, url: str, company_name: str) -> int:
        """
        Score un candidat de logo basé sur l'URL et le nom de l'entreprise
        """
        score = 0
        url_lower = url.lower()
        company_lower = company_name.lower()
        
        # Points pour mots-clés dans l'URL
        if 'logo' in url_lower:
            score += 5
        if 'brand' in url_lower:
            score += 3
        if 'icon' in url_lower:
            score += 2
            
        # Points pour nom de l'entreprise dans l'URL
        company_words = company_lower.split()
        for word in company_words:
            if len(word) > 2 and word in url_lower:
                score += 3
                
        # Points pour domaines fiables
        if any(domain in url_lower for domain in ['wikipedia.org', 'wikimedia.org']):
            score += 4
        elif any(domain in url_lower for domain in ['linkedin.com', 'crunchbase.com']):
            score += 3
        elif any(domain in url_lower for domain in ['clearbit.com', 'logo.clearbit.com']):
            score += 5
        elif url_lower.startswith('https://'):
            score += 1
            
        # Pénalités
        if any(bad in url_lower for bad in ['thumbnail', 'thumb', 'small', 'tiny']):
            score -= 2
        if any(bad in url_lower for bad in ['generic', 'placeholder', 'default']):
            score -= 3
            
        return max(0, score)
    
    def _search_logo_clearbit(self, company_name: str) -> Optional[str]:
        """
        Recherche via l'API Clearbit (service de logos d'entreprises)
        """
        try:
            # Clearbit Logo API - gratuit et fiable
            clean_name = self._clean_company_name(company_name)
            
            # Essayer différents formats de domaine
            possible_domains = [
                f"{clean_name.replace(' ', '').lower()}.com",
                f"{clean_name.replace(' ', '-').lower()}.com",
                f"{clean_name.split()[0].lower()}.com" if ' ' in clean_name else f"{clean_name.lower()}.com"
            ]
            
            for domain in possible_domains:
                try:
                    clearbit_url = f"https://logo.clearbit.com/{domain}"
                    
                    # Vérifier si l'image existe
                    response = self.session.head(clearbit_url, timeout=5)
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '').lower()
                        if 'image' in content_type:
                            logger.info(f"Logo Clearbit trouvé pour {company_name}: {clearbit_url}")
                            return clearbit_url
                            
                except Exception as e:
                    logger.debug(f"Clearbit échec pour {domain}: {e}")
                    continue
                    
            return None
            
        except Exception as e:
            logger.warning(f"Erreur Clearbit pour {company_name}: {e}")
            return None
            
        except Exception as e:
            logger.warning(f"Erreur DuckDuckGo pour {company_name}: {e}")
            return self._search_logo_alternative(company_name)
    
    def _search_logo_alternative(self, company_name: str) -> Optional[str]:
        """
        Méthode alternative de recherche de logo (fallback)
        Utilise des sources connues fiables et Wikipedia
        """
        try:
            # Nettoyer le nom de l'entreprise
            clean_name = self._clean_company_name(company_name).lower()
            
            # 1. Essayer avec des URLs directes pour les entreprises les plus courantes
            direct_logos = self._get_direct_logo_urls()
            for company, logo_url in direct_logos.items():
                if company in clean_name or clean_name in company:
                    logger.info(f"Logo direct trouvé pour {company_name}: {logo_url}")
                    return logo_url
            
            # 2. Essayer avec Wikipedia/Wikimedia (source très fiable)
            wikipedia_url = self._search_wikipedia_logo(clean_name)
            if wikipedia_url:
                return wikipedia_url
            
            # 3. Essayer avec des domaines d'entreprise connus
            company_domain_url = self._search_company_domain_logo(clean_name)
            if company_domain_url:
                return company_domain_url
            
            # 4. Logos génériques basés sur les initiales ou le nom
            generic_url = self._generate_generic_logo(company_name)
            if generic_url:
                return generic_url
            
            return None
            
        except Exception as e:
            logger.warning(f"Erreur recherche alternative pour {company_name}: {e}")
            return None
    
    def _get_direct_logo_urls(self) -> dict:
        """Retourne un dictionnaire des URLs de logos directs pour les entreprises courantes"""
        return {
            # Tech giants
            'google': 'https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_160x56dp.png',
            'microsoft': 'https://img-prod-cms-rt-microsoft-com.akamaized.net/cms/api/am/imageFileData/RE1Mu3b?ver=5c31',
            'apple': 'https://www.apple.com/ac/structured-data/images/knowledge_graph_logo.png',
            'amazon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Amazon_logo.svg/200px-Amazon_logo.svg.png',
            'meta': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Meta_Platforms_Inc._logo.svg/200px-Meta_Platforms_Inc._logo.svg.png',
            'facebook': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Meta_Platforms_Inc._logo.svg/200px-Meta_Platforms_Inc._logo.svg.png',
            
            # Entreprises françaises courantes
            'société générale': 'https://upload.wikimedia.org/wikipedia/fr/thumb/5/56/Logo_Soci%C3%A9t%C3%A9_G%C3%A9n%C3%A9rale_2020.svg/200px-Logo_Soci%C3%A9t%C3%A9_G%C3%A9n%C3%A9rale_2020.svg.png',
            'societe generale': 'https://upload.wikimedia.org/wikipedia/fr/thumb/5/56/Logo_Soci%C3%A9t%C3%A9_G%C3%A9n%C3%A9rale_2020.svg/200px-Logo_Soci%C3%A9t%C3%A9_G%C3%A9n%C3%A9rale_2020.svg.png',
            'bnp paribas': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/BNP_Paribas.svg/200px-BNP_Paribas.svg.png',
            'orange': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Orange_logo.svg/200px-Orange_logo.svg.png',
            'total': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/TotalEnergies_Logo.svg/200px-TotalEnergies_Logo.svg.png',
            'carrefour': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Carrefour_Logo.svg/200px-Carrefour_Logo.svg.png',
            'renault': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Renault_2022.svg/200px-Renault_2022.svg.png',
            'peugeot': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Peugeot_logo.svg/200px-Peugeot_logo.svg.png',
            'devoteam': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Devoteam_logo.png/200px-Devoteam_logo.png',
            
            # Entreprises tech courantes
            'linkedin': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/LinkedIn_logo_initials.png/200px-LinkedIn_logo_initials.png',
            'spotify': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Spotify_logo_without_text.svg/200px-Spotify_logo_without_text.svg.png',
            'uber': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Uber_logo_2018.png/200px-Uber_logo_2018.png',
            'netflix': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Netflix_2015_logo.svg/200px-Netflix_2015_logo.svg.png',
            'tesla': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Tesla_T_symbol.svg/200px-Tesla_T_symbol.svg.png',
            'airbnb': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Airbnb_Logo_B%C3%A9lo.svg/200px-Airbnb_Logo_B%C3%A9lo.svg.png',
            
            # Consulting/IT français
            'extia': 'https://www.extia.fr/images/logo.png',
            'infopro': 'https://www.infopro-digital.com/sites/default/files/logo-infopro-digital.png',
            'eventmaker': 'https://cdn.eventmaker.com/assets/logo-eventmaker.png'
        }
    
    def _generate_generic_logo(self, company_name: str) -> Optional[str]:
        """Génère un logo générique via un service comme Logo.dev ou UI Avatars"""
        try:
            # Utiliser UI Avatars pour créer un logo simple avec les initiales
            clean_name = self._clean_company_name(company_name)
            
            # Prendre les premières lettres de chaque mot
            words = clean_name.split()
            initials = ''.join([word[0].upper() for word in words if word])[:3]  # Max 3 lettres
            
            if initials:
                # UI Avatars service (gratuit)
                avatar_url = f"https://ui-avatars.com/api/?name={initials}&size=200&background=0D47A1&color=fff&bold=true&format=png"
                logger.info(f"Logo générique généré pour {company_name}: {avatar_url}")
                return avatar_url
            
            return None
            
        except Exception as e:
            logger.warning(f"Erreur génération logo générique pour {company_name}: {e}")
            return None
    
    def _search_wikipedia_logo(self, company_name: str) -> Optional[str]:
        """Recherche de logo sur Wikipedia"""
        try:
            # API Wikipedia pour rechercher la page de l'entreprise
            wiki_search_url = "https://en.wikipedia.org/w/api.php"
            search_params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': f"{company_name} company",
                'srlimit': 3
            }
            
            response = self.session.get(wiki_search_url, params=search_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'query' in data and 'search' in data['query'] and data['query']['search']:
                # Prendre la première page trouvée
                page_title = data['query']['search'][0]['title']
                
                # Récupérer les images de la page
                images_params = {
                    'action': 'query',
                    'format': 'json',
                    'titles': page_title,
                    'prop': 'images',
                    'imlimit': 10
                }
                
                response = self.session.get(wiki_search_url, params=images_params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if 'query' in data and 'pages' in data['query']:
                    pages = data['query']['pages']
                    for page_id in pages:
                        if 'images' in pages[page_id]:
                            for image in pages[page_id]['images']:
                                image_title = image['title']
                                if 'logo' in image_title.lower() or 'brand' in image_title.lower():
                                    # Récupérer l'URL de l'image
                                    image_info_params = {
                                        'action': 'query',
                                        'format': 'json',
                                        'titles': image_title,
                                        'prop': 'imageinfo',
                                        'iiprop': 'url',
                                        'iiurlwidth': 200
                                    }
                                    
                                    response = self.session.get(wiki_search_url, params=image_info_params, timeout=10)
                                    response.raise_for_status()
                                    data = response.json()
                                    
                                    if 'query' in data and 'pages' in data['query']:
                                        for img_page_id in data['query']['pages']:
                                            img_page = data['query']['pages'][img_page_id]
                                            if 'imageinfo' in img_page and img_page['imageinfo']:
                                                img_url = img_page['imageinfo'][0].get('thumburl') or img_page['imageinfo'][0].get('url')
                                                if img_url and self._is_valid_image_url(img_url):
                                                    logger.info(f"Logo trouvé sur Wikipedia pour {company_name}: {img_url}")
                                                    return img_url
            
            return None
            
        except Exception as e:
            logger.warning(f"Erreur recherche Wikipedia pour {company_name}: {e}")
            return None
    
    def _search_company_domain_logo(self, company_name: str) -> Optional[str]:
        """Recherche de logo via le domaine de l'entreprise"""
        try:
            # Essayer de deviner le domaine de l'entreprise
            possible_domains = [
                f"https://www.{company_name.replace(' ', '')}.com/favicon.ico",
                f"https://www.{company_name.replace(' ', '')}.com/logo.png",
                f"https://www.{company_name.replace(' ', '')}.fr/favicon.ico",
                f"https://logo.clearbit.com/{company_name.replace(' ', '')}.com"  # Service Clearbit
            ]
            
            for domain_url in possible_domains:
                try:
                    response = self.session.head(domain_url, timeout=5)
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '').lower()
                        if any(img_type in content_type for img_type in ['image/png', 'image/jpeg', 'image/jpg', 'image/gif']):
                            logger.info(f"Logo trouvé via domaine pour {company_name}: {domain_url}")
                            return domain_url
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.warning(f"Erreur recherche domaine pour {company_name}: {e}")
            return None
    
    def _is_valid_image_url(self, url: str) -> bool:
        """Vérifie si l'URL pointe vers une image valide"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Vérifier l'extension
            path_lower = parsed.path.lower()
            valid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']
            
            return any(path_lower.endswith(ext) for ext in valid_extensions)
            
        except Exception:
            return False
    
    def _download_and_process_image(self, image_url: str) -> Optional[bytes]:
        """
        Télécharge et traite une image (gère SVG et formats bitmap)
        """
        try:
            response = self.session.get(image_url, timeout=15, stream=True)
            response.raise_for_status()
            
            # Vérifier la taille
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > 5 * 1024 * 1024:  # 5MB max
                logger.warning(f"Image trop grande: {content_length} bytes")
                return None
            
            # Télécharger l'image
            image_data = response.content
            
            # Vérifier si c'est un SVG
            if self._is_svg_data(image_data):
                return self._convert_svg_to_png(image_data)
            
            # Traiter l'image bitmap avec Pillow
            try:
                with Image.open(io.BytesIO(image_data)) as img:
                    # Convertir en RGB si nécessaire
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Créer un fond blanc pour la transparence
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Redimensionner en préservant les proportions avec une taille cohérente
                    target_size = 120  # Taille standard pour cohérence
                    img = self._resize_with_aspect_ratio(img, target_size)
                    
                    # Sauvegarder en PNG
                    output = io.BytesIO()
                    img.save(output, format='PNG', optimize=True)
                    return output.getvalue()
                    
            except Exception as e:
                logger.warning(f"Erreur traitement image: {e}")
                return None
            
        except Exception as e:
            logger.warning(f"Erreur téléchargement image {image_url}: {e}")
            return None
    
    def _resize_with_aspect_ratio(self, img: Image.Image, target_size: int) -> Image.Image:
        """
        Redimensionne une image en préservant les proportions et en créant une image carrée
        avec l'image centrée sur un fond blanc
        """
        # Calculer les nouvelles dimensions en préservant les proportions
        original_width, original_height = img.size
        
        # Calculer le ratio pour que la plus grande dimension soit target_size
        if original_width > original_height:
            new_width = target_size
            new_height = int((original_height * target_size) / original_width)
        else:
            new_height = target_size
            new_width = int((original_width * target_size) / original_height)
        
        # Redimensionner l'image
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Créer une image carrée avec fond blanc
        square_img = Image.new('RGB', (target_size, target_size), (255, 255, 255))
        
        # Centrer l'image redimensionnée
        x_offset = (target_size - new_width) // 2
        y_offset = (target_size - new_height) // 2
        
        square_img.paste(img_resized, (x_offset, y_offset))
        
        return square_img

    def _is_svg_data(self, data: bytes) -> bool:
        """Vérifie si les données sont un fichier SVG"""
        try:
            # Vérifier les premiers bytes pour identifier un SVG
            data_str = data[:500].decode('utf-8', errors='ignore').lower()
            return '<svg' in data_str or '<?xml' in data_str and 'svg' in data_str
        except:
            return False
    
    def _convert_svg_to_png(self, svg_data: bytes) -> Optional[bytes]:
        """Convertit un SVG en PNG en utilisant un fallback simple"""
        try:
            # Pour l'instant, utiliser directement le fallback
            # La conversion SVG complexe sera ajoutée plus tard si nécessaire
            logger.info("Conversion SVG désactivée temporairement, utilisation du fallback")
            return self._simple_svg_fallback(svg_data)
                
        except Exception as e:
            logger.warning(f"Erreur conversion SVG vers PNG: {e}")
            return self._simple_svg_fallback(svg_data)
    
    def _simple_svg_fallback(self, svg_data: bytes) -> Optional[bytes]:
        """Fallback simple pour les SVG non convertibles"""
        try:
            # Créer une image de substitution simple
            from PIL import Image, ImageDraw, ImageFont
            
            target_size = 120  # Même taille que les autres logos
            
            # Créer une image blanche carrée
            img = Image.new('RGB', (target_size, target_size), color='white')
            draw = ImageDraw.Draw(img)
            
            # Ajouter un rectangle coloré comme placeholder
            margin = target_size // 6
            draw.rectangle([margin, margin, target_size-margin, target_size-margin], 
                          fill='#E0E0E0', outline='#CCCCCC')
            
            # Ajouter du texte "LOGO"
            try:
                # Essayer d'utiliser une police par défaut
                font = ImageFont.load_default()
                text = "LOGO"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (target_size - text_width) // 2
                y = (target_size - text_height) // 2
                draw.text((x, y), text, fill='#666666', font=font)
            except:
                # Si la police échoue, juste le rectangle
                pass
            
            # Sauvegarder en PNG
            output = io.BytesIO()
            img.save(output, format='PNG', optimize=True)
            return output.getvalue()
            
        except Exception as e:
            logger.warning(f"Erreur fallback SVG: {e}")
            return None
    
    def get_devoteam_logo(self) -> Optional[bytes]:
        """Récupère le logo Devoteam depuis les assets ou le télécharge"""
        # Chemin vers le logo local
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'devoteam_logo.png')
        
        # Essayer de charger depuis le fichier local
        if os.path.exists(logo_path):
            try:
                with open(logo_path, 'rb') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Impossible de charger le logo local: {e}")
        
        # Télécharger le logo Devoteam
        return self.search_company_logo("Devoteam")


# Instance globale du service
logo_service = LogoSearchService()
