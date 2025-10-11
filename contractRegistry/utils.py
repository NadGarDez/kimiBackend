def extract_constructor_inputs_from_abi(abi_object):
    """
    Parsea el objeto ABI (asume que ya es un objeto de Python, no una cadena)
    para encontrar la definición del constructor y extraer sus argumentos.
    """
    if not isinstance(abi_object, list):
        return []

    constructor_definition = next(
        (item for item in abi_object if item.get('type') == 'constructor'), 
        None
    )
    
    if constructor_definition and 'inputs' in constructor_definition:
        return constructor_definition['inputs']
    else:
        return []