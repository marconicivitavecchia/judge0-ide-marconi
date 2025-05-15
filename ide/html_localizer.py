#!/usr/bin/env python3
import os
import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import mimetypes
from pathlib import Path
import hashlib

class HTMLLocalizer:
    def __init__(self, html_file, output_dir=None, assets_dir="assets"):
        """
        Inizializza il localizzatore HTML
        
        Args:
            html_file (str): Percorso del file HTML di input
            output_dir (str): Directory di output (default: stessa directory del file HTML)
            assets_dir (str): Nome della cartella per gli assets (default: "assets")
        """
        self.html_file = html_file
        self.output_dir = output_dir or os.path.dirname(html_file)
        self.assets_dir = os.path.join(self.output_dir, assets_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Crea la directory degli assets se non esiste
        Path(self.assets_dir).mkdir(parents=True, exist_ok=True)
        
        # Contatori per statistiche
        self.downloaded_count = 0
        self.failed_count = 0
        self.skipped_count = 0
    
    def is_external_url(self, url):
        """Verifica se un URL è esterno"""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    
    def get_file_extension(self, url, content_type=None):
        """Ottiene l'estensione del file dall'URL o dal content-type"""
        parsed = urlparse(url)
        path = parsed.path
        
        # Prova a ottenere l'estensione dall'URL
        if path and '.' in os.path.basename(path):
            return os.path.splitext(path)[1]
        
        # Se non c'è estensione nell'URL, prova a indovinarla dal content-type
        if content_type:
            extension = mimetypes.guess_extension(content_type.split(';')[0])
            if extension:
                return extension
        
        # Fallback per tipi comuni
        if 'javascript' in (content_type or ''):
            return '.js'
        elif 'css' in (content_type or ''):
            return '.css'
        
        return ''
    
    def download_file(self, url, filename):
        """Scarica un file da un URL"""
        try:
            print(f"Scaricando: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Crea la directory se necessario
            filepath = os.path.join(self.assets_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Salva il file
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            self.downloaded_count += 1
            return True
            
        except Exception as e:
            print(f"Errore nel download di {url}: {e}")
            self.failed_count += 1
            return False
    
    def generate_local_filename(self, url):
        """Genera un nome file locale per un URL esterno"""
        parsed = urlparse(url)
        
        # Usa il nome del file dall'URL se esiste
        if parsed.path and os.path.basename(parsed.path):
            filename = os.path.basename(parsed.path)
            # Rimuovi parametri query dal nome file
            filename = filename.split('?')[0]
        else:
            # Genera un hash dell'URL come nome file
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename = f"resource_{url_hash}"
        
        # Assicurati che il file abbia un'estensione
        if not os.path.splitext(filename)[1]:
            # Prova a indovinare l'estensione dall'URL
            if 'css' in url.lower():
                filename += '.css'
            elif 'js' in url.lower() or 'javascript' in url.lower():
                filename += '.js'
            elif any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg']):
                # L'estensione è già nell'URL
                pass
            else:
                # Fallback: prova a scaricare l'header per il content-type
                try:
                    response = self.session.head(url, timeout=10)
                    content_type = response.headers.get('content-type', '')
                    ext = self.get_file_extension(url, content_type)
                    if ext:
                        filename += ext
                except:
                    pass
        
        return filename
    
    def process_html(self):
        """Processa il file HTML e localizza le dipendenze"""
        with open(self.html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Trova tutti i link esterni
        external_resources = []
        
        # CSS files (link rel="stylesheet")
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href and self.is_external_url(href):
                external_resources.append(('css', link, 'href', href))
        
        # JavaScript files (script src)
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src and self.is_external_url(src):
                external_resources.append(('js', script, 'src', src))
        
        # Images (img src)
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src and self.is_external_url(src):
                external_resources.append(('img', img, 'src', src))
        
        # Other resources (link href, object data, embed src, etc.)
        for tag in soup.find_all(['link', 'object', 'embed']):
            for attr in ['href', 'data', 'src']:
                url = tag.get(attr)
                if url and self.is_external_url(url):
                    # Evita duplicati (già processati sopra)
                    if not any(res[3] == url for res in external_resources):
                        external_resources.append(('other', tag, attr, url))
        
        # CSS inline con @import o url()
        style_tags = soup.find_all('style')
        for style in style_tags:
            if style.string:
                # Trova URL nelle regole CSS
                css_urls = re.findall(r'url\(["\']?(https?://[^"\']+)["\']?\)', style.string)
                css_imports = re.findall(r'@import\s+["\']?(https?://[^"\']+)["\']?', style.string)
                
                for url in css_urls + css_imports:
                    if url not in [res[3] for res in external_resources]:
                        external_resources.append(('css_inline', style, 'content', url))
        
        print(f"Trovate {len(external_resources)} risorse esterne")
        
        # Scarica e sostituisce le risorse
        for resource_type, element, attr, url in external_resources:
            local_filename = self.generate_local_filename(url)
            
            # Verifica se il file esiste già
            local_path = os.path.join(self.assets_dir, local_filename)
            if os.path.exists(local_path):
                print(f"File già esistente: {local_filename}")
                self.skipped_count += 1
            else:
                # Scarica il file
                if not self.download_file(url, local_filename):
                    continue
            
            # Aggiorna il riferimento nell'HTML
            if resource_type == 'css_inline':
                # Sostituisce URL nel CSS inline
                new_url = f"./{os.path.relpath(local_path, self.output_dir)}"
                element.string = element.string.replace(url, new_url)
            else:
                # Sostituisce l'attributo
                new_url = f"./{os.path.relpath(local_path, self.output_dir)}"
                element[attr] = new_url
        
        # Salva il file HTML modificato
        output_file = os.path.join(self.output_dir, 'index_local.html')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        return output_file
    
    def print_statistics(self):
        """Stampa le statistiche del processo"""
        total = self.downloaded_count + self.failed_count + self.skipped_count
        print(f"\n--- Statistiche ---")
        print(f"Totale risorse trovate: {total}")
        print(f"Scaricate con successo: {self.downloaded_count}")
        print(f"Già esistenti (saltate): {self.skipped_count}")
        print(f"Fallite: {self.failed_count}")


def main():
    """Funzione principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Localizza le dipendenze esterne di un file HTML')
    parser.add_argument('html_file', help='Percorso del file HTML da processare')
    parser.add_argument('-o', '--output-dir', help='Directory di output (default: stessa del file HTML)')
    parser.add_argument('-a', '--assets-dir', default='assets', help='Nome cartella assets (default: assets)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.html_file):
        print(f"Errore: Il file {args.html_file} non esiste")
        return
    
    # Crea l'istanza del localizzatore
    localizer = HTMLLocalizer(
        html_file=args.html_file,
        output_dir=args.output_dir,
        assets_dir=args.assets_dir
    )
    
    try:
        # Processa il file HTML
        output_file = localizer.process_html()
        
        # Stampa statistiche
        localizer.print_statistics()
        
        print(f"\nFile HTML localizzato salvato come: {output_file}")
        print(f"Assets salvati in: {localizer.assets_dir}")
        
    except Exception as e:
        print(f"Errore durante il processo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

