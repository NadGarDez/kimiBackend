import datetime

# Datos de ejemplo simplificados para simular un contrato
STATIC_CONTRACT_DATA = {
    'id': 1,
    'name': 'HashPoolAdmin',
    'description': 'Contrato base para la administración de instancias de HashPool. Permite la gestión de parámetros clave y la configuración de comisiones.',
    'internal_id': 1001,
    'latest_update': datetime.date(2024, 10, 3),
    
    # ----------------------------------------------------------------------
    # Datos de la Versión Activa
    'version': {
        'number': 'v2.1.3',
        # Bytecode simplificado a ~50 caracteres
        'bytecode': '0x608060405234801561001057600080fd5b50604051803b9060209081526000908', 
        'hash_file': '0x1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f90ab', # Hash de ejemplo
        'date_uploaded': '2024-08-15',
        
        # ABI como objeto de Python (list of dicts) para usar | pprint
        'abi': [
            {"type": "constructor", "stateMutability": "nonpayable", "inputs": []},
            {"type": "function", "name": "getAdmin", "outputs": [{"type": "address", "name": "addr1"}], "stateMutability": "view", "inputs": []},
            {"type": "function", "name": "setFee", "outputs": [{"type": "bool"}], "stateMutability": "nonpayable", "inputs": [{"type": "uint256", "name": "newFee"}]},
            {"type": "function", "name": "upgradeLogic", "outputs": [], "stateMutability": "nonpayable", "inputs": [{"type": "address", "name": "newLogic"}]},
            {"type": "function", "name": "getVersion", "outputs": [{"type": "string", "name": "ver"}], "stateMutability": "view", "inputs": []},
            {"type": "event", "name": "FeeUpdated", "inputs": [{"type": "uint256", "name": "oldFee", "indexed": True}, {"type": "uint256", "name": "newFee", "indexed": True}], "anonymous": False},
            {"type": "event", "name": "LogicUpgraded", "inputs": [{"type": "address", "name": "oldLogic"}, {"type": "address", "name": "newLogic"}], "anonymous": False},
            {"type": "function", "name": "pauseContract", "outputs": [], "stateMutability": "nonpayable", "inputs": []},
            {"type": "function", "name": "unpauseContract", "outputs": [], "stateMutability": "nonpayable", "inputs": []},
            {"type": "function", "name": "deposit", "outputs": [], "stateMutability": "payable", "inputs": []},
            {"type": "function", "name": "withdraw", "outputs": [{"type": "bool"}], "stateMutability": "nonpayable", "inputs": [{"type": "uint256", "name": "amount"}]},
            {"type": "function", "name": "getPoolBalance", "outputs": [{"type": "uint256"}], "stateMutability": "view", "inputs": []},
            {"type": "function", "name": "transferOwnership", "outputs": [], "stateMutability": "nonpayable", "inputs": [{"type": "address", "name": "newOwner"}]},
            {"type": "function", "name": "owner", "outputs": [{"type": "address"}], "stateMutability": "view", "inputs": []},
            {"type": "function", "name": "totalPools", "outputs": [{"type": "uint256"}], "stateMutability": "view", "inputs": []},
            {"type": "function", "name": "addPool", "outputs": [], "stateMutability": "nonpayable", "inputs": [{"type": "address", "name": "poolAddr"}]},
            {"type": "function", "name": "removePool", "outputs": [], "stateMutability": "nonpayable", "inputs": [{"type": "address", "name": "poolAddr"}]},
            {"type": "function", "name": "isPoolActive", "outputs": [{"type": "bool"}], "stateMutability": "view", "inputs": [{"type": "address", "name": "poolAddr"}]},
            {"type": "function", "name": "getFee", "outputs": [{"type": "uint256"}], "stateMutability": "view", "inputs": []},
            {"type": "function", "name": "initialize", "outputs": [], "stateMutability": "nonpayable", "inputs": [{"type": "address", "name": "_admin"}]}
        ],
    },

    # ----------------------------------------------------------------------
    # Datos de Historial (para la Pestaña "Versiones")
    'history': [
        {'version': 'v2.1.3', 'hash_file': '0x1a2b3c4d5e6f7a8b9c0d1e2f...', 'date_uploaded': '2024-08-15'},
        {'version': 'v2.0.0', 'hash_file': '0x5f6g7h8i9j0k1l2m3n4o5p6q...', 'date_uploaded': '2024-06-20'},
        {'version': 'v1.0.0', 'hash_file': '0xabcdef0123456789abcdef01...', 'date_uploaded': '2024-04-01'},
    ],

    # ----------------------------------------------------------------------
    # Datos de Despliegues (para la Pestaña "Despliegues Activos")
    'deployments': [
        {'network': 'Sepolia', 'address': '0xAbCdE...12345', 'version': 'v2.1.3', 'status': 'Activo'},
        {'network': 'Mainnet (ETH)', 'address': '0xFeDcB...98765', 'version': 'v2.0.0', 'status': 'Retirado'},
        {'network': 'Local Dev', 'address': '0x45678...0AbCd', 'version': 'v2.1.3', 'status': 'Activo'},
    ]
}