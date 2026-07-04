# sites_manager.py

SITES = []

def get_sites():
    return SITES

def add_site(url):
    SITES.append(url)
    return True
