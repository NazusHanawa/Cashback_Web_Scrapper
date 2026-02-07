HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

STORES = [
    {"name": "Magazine Luiza", "url": "https://www.magazineluiza.com.br"},
    {"name": "Amazon", "url": "https://www.amazon.com.br"},
    {"name": "Shopee", "url": "https://shopee.com.br"},
    {"name": "AliExpress", "url": "https://pt.aliexpress.com"},
    {"name": "LG", "url": "https://www.lg.com/br"},
    {"name": "KaBuM!", "url": "https://www.kabum.com.br"},
    {"name": "Americanas", "url": "https://www.americanas.com.br"},
    {"name": "Casas Bahia", "url": "https://www.casasbahia.com.br"}
]

PLATFORMS = [
    {
        "name": "Méliuz", 
        "url": "https://www.meliuz.com.br/desconto",
        "cashback_value_path": "div.container > aside > div.redirect-btn > button > span",
        "cashback_description_path": None
    },
    {
        "name": "Cuponomia", 
        "url": "https://www.cuponomia.com.br/desconto",
        "cashback_value_path": "#middle > div.store_header.js-storeHeader.container > div.store_header__logo.js-storeLogo > aside > button > span",
        "cashback_description_path": None
    }
    # Inter
    # Buscapé / Zoom
]