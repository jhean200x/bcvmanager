import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')

def obtener_tasas_bcv():
    """
    Función que hace scraping al BCV ignorando errores SSL
    """
    try:
        url = "https://www.bcv.org.ve/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Deshabilitar verificación SSL
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        tasas = {}
        
        # Dólar
        dolar_div = soup.find('div', id='dolar')
        if dolar_div:
            dolar_text = dolar_div.find('strong').text.strip()
            tasas['USD'] = float(dolar_text.replace(',', '.'))
        
        # Euro
        euro_div = soup.find('div', id='euro')
        if euro_div:
            euro_text = euro_div.find('strong').text.strip()
            tasas['EUR'] = float(euro_text.replace(',', '.'))
        
        # Yuan
        yuan_div = soup.find('div', id='yuan')
        if yuan_div:
            yuan_text = yuan_div.find('strong').text.strip()
            tasas['CNY'] = float(yuan_text.replace(',', '.'))
        

        # Rublo
        rublo_div = soup.find('div', id='rublo')
        if euro_div:
            rublo_text = rublo_div.find('strong').text.strip()
            tasas['RUB'] = float(rublo_text.replace(',', '.'))

        # Lira
        lira_div = soup.find('div', id='lira')
        if lira_div:
            lira_text = lira_div.find('strong').text.strip()
            tasas['TRY'] = float(lira_text.replace(',', '.'))

        return tasas
        
    except Exception as e:
        print(f"Error: {e}")
        return None


