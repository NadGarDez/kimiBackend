from web3 import Web3
from django.conf import settings

NODE_URL = getattr(settings, "ETHEREUM_NODE_URL", "http://127.0.0.1:8545")

try:
    # 3. Crear la instancia de Web3
    w3 = Web3(Web3.HTTPProvider(NODE_URL))
    
    if not w3.is_connected():
        print(f"❌ ADVERTENCIA: Web3 no pudo conectar al nodo en {NODE_URL}")
        w3 = None 


except Exception as e:
    print(f"❌ ERROR CRÍTICO al inicializar Web3: {e}")
    w3 = None