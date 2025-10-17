/**
 * AdminDashboardUtils
 *
 * Este módulo contiene la lógica para interactuar con un contrato inteligente
 * de Tickets usando Ethers.js, manejando la conexión de MetaMask y la
 * ejecución de funciones.
 *
 * @param {Object} config - Objeto con las constantes del contrato (ABI, Address, ChainID).
 * @param {Object} dom - Objeto con las referencias directas a los elementos del DOM.
 * @param {Array<string>} targetFunctions - Lista de nombres de funciones del ABI a exponer.
 * @returns {Object} Objeto público con métodos 'connectWallet', 'generateForms' y 'fetchContractBalance'.
 */
const AdminDashboardUtils = (config, dom, targetFunctions) => {

    // --- ESTADO GLOBAL WEB3 REAL ---
    let provider = null;
    let signer = null;
    let userAccount = null;

    // Desestructurar la configuración y el DOM
    const { ABI, CONTRACT_ADDRESS, REQUIRED_CHAIN_ID, REQUIRED_NETWORK_NAME } = config;
    const { statusTextEl, metamaskStatusCard, connectMetamaskBtn, executionFormsContainer } = dom;

    // Asegurarse de que ethers esté disponible
    if (typeof ethers === 'undefined') {
        console.error("Error en AdminDashboardUtils: Ethers.js no está cargado.");
        return {};
    }

    // --- Funciones Auxiliares ---

    /**
     * Sanitiza el resultado de una función view/pure de Ethers para una visualización simple.
     */
    const sanitizeResult = (rawResult) => {
        // Ethers devuelve objetos Result, que son arrays extendidos.
        // Convertimos a un objeto simple o un valor para facilitar la visualización.
        if (Array.isArray(rawResult)) {
            // Si es un array de valores, lo devuelve como un array normal.
            if (rawResult.every(item => typeof item !== 'object')) {
                 return rawResult.map(item => item instanceof BigInt ? item.toString() : item);
            }
            // Caso más complejo: mapea las propiedades nombradas a un objeto
            const resultObj = {};
            const keys = Object.keys(rawResult).filter(key => isNaN(parseInt(key))); // Filtra índices numéricos
            keys.forEach(key => {
                resultObj[key] = rawResult[key] instanceof BigInt ? rawResult[key].toString() : rawResult[key];
            });
            // Si solo hay una propiedad nombrada, devuelve solo ese valor.
            return keys.length === 1 ? resultObj[keys[0]] : resultObj;
        }
        // Si es un BigInt (número grande), lo convierte a string
        if (rawResult instanceof BigInt) {
            return rawResult.toString();
        }
        return rawResult;
    };

    /**
     * Mapea un tipo Solidity a un tipo de input HTML para la creación de formularios.
     */
    const getHtmlInputType = (solidityType) => {
        if (solidityType.includes('uint') || solidityType.includes('int')) {
            return 'number';
        }
        if (solidityType === 'bool') {
            return 'checkbox';
        }
        // address, bytes, string, arrays (e.g. string[])
        return 'text'; 
    };
    
    // --- LÓGICA AGREGADA: Obtener Balance del Contrato ---
    
    /**
     * Obtiene y formatea el balance del token nativo (ej. ETH) del Contrato.
     * Esta función solo requiere que el 'provider' esté inicializado (no requiere conexión de wallet).
     * * @returns {string} Balance formateado o 'N/A'.
     */
    const fetchContractBalance = async () => {
        // Nota: Solo necesitamos el 'provider', no el 'signer' ni la 'userAccount' para esta consulta.
        if (!provider || !CONTRACT_ADDRESS) return 'N/A';
        try {
            // Utilizamos el CONTRACT_ADDRESS para obtener el balance.
            const balanceWei = await provider.getBalance(CONTRACT_ADDRESS);
            // Convertir a Ether y formatear
            const balanceEth = ethers.formatEther(balanceWei);
            // Mostrar la moneda nativa (e.g., ETH, MATIC)
            return `${parseFloat(balanceEth).toFixed(4)} ${REQUIRED_NETWORK_NAME.toUpperCase()}`; 
        } catch (error) {
            console.error("Error al obtener el balance del contrato:", error);
            return 'Error';
        }
    };


    // --- Lógica de Conexión Web3 ---

    /**
     * Actualiza el estado visual de la conexión MetaMask en el DOM.
     */
    const updateStatus = (isConnected, message, colorClass, buttonText = 'Conectar Wallet') => {
        const icon = isConnected ? 'bi-check-circle-fill text-success' : 'bi-x-circle-fill text-danger';

        statusTextEl.innerHTML = `<i class="bi ${icon} me-1"></i> ${message}`;
        metamaskStatusCard.className = `card p-2 text-center bg-dark shadow-sm border ${colorClass}`;
        
        if (isConnected) {
            connectMetamaskBtn.style.display = 'none';
        } else {
            connectMetamaskBtn.style.display = 'block';
            connectMetamaskBtn.textContent = buttonText;
        }
    };

    /**
     * Intenta conectar MetaMask y verificar la red.
     */
    const connectWallet = async () => {
        if (window.ethereum) {
            try {
                updateStatus(false, 'Conectando...', 'border-warning', 'Reconectar');
                
                // 1. Obtener la cuenta
                const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
                userAccount = accounts[0];
                
                // 2. Crear Ethers Provider y Signer
                provider = new ethers.BrowserProvider(window.ethereum);
                signer = await provider.getSigner(userAccount);
                
                // 3. Verificar Chain ID
                const network = await provider.getNetwork();
                const currentChainId = Number(network.chainId); 

                if (currentChainId !== REQUIRED_CHAIN_ID) {
                    updateStatus(false, `Red incorrecta (ID: ${currentChainId}). Cambia a ${REQUIRED_NETWORK_NAME} (ID: ${REQUIRED_CHAIN_ID}).`, 'border-danger', 'Cambiar Red');
                    return; // No continuar si la red es incorrecta
                }

                // Éxito
                updateStatus(true, `Conectado: ${userAccount.substring(0, 6)}...${userAccount.substring(38)}`, 'border-success');
                
                // Escuchar cambios de cuenta y red
                window.ethereum.on('accountsChanged', handleAccountsChanged);
                window.ethereum.on('chainChanged', handleChainChanged);

            } catch (error) {
                console.error("Error al conectar la wallet:", error);
                updateStatus(false, 'Conexión Fallida.', 'border-danger');
            }
        } else {
            updateStatus(false, 'MetaMask no detectado.', 'border-danger', 'Instalar MetaMask');
        }
    };
    
    /** Maneja el cambio de cuenta. */
    const handleAccountsChanged = (accounts) => {
        if (accounts.length === 0) {
            updateStatus(false, 'Wallet Desconectada.', 'border-secondary', 'Conectar Wallet');
            userAccount = null;
            signer = null;
        } else {
            connectWallet(); 
        }
    };

    /** Maneja el cambio de red. */
    const handleChainChanged = () => {
        connectWallet();
    };


    // --- Lógica de Ejecución de Contrato ---

    /**
     * Maneja el evento de envío del formulario de ejecución de la función.
     */
    const handleFunctionExecution = async (event) => {
        event.preventDefault();
        
        const form = event.target;
        const functionName = form.getAttribute('data-function-name');
        const functionType = form.getAttribute('data-function-type');
        const resultDiv = document.getElementById(`result-${functionName}`);

        if (functionType === 'write' && !signer) {
            resultDiv.innerHTML = `<span class="text-danger"><i class="bi bi-x-circle-fill me-1"></i> Por favor, conecta y verifica tu wallet para ejecutar transacciones.</span>`;
            return;
        }

        // Bloquear UI
        const originalButton = form.querySelector('button[type="submit"]');
        const originalButtonText = originalButton.textContent;
        originalButton.disabled = true;
        originalButton.textContent = (functionType === 'read') ? 'Consultando...' : 'Confirmando TX...';
        
        resultDiv.innerHTML = `<span class="text-warning"><i class="bi bi-hourglass-split me-1"></i> Procesando llamada a ${functionName}...</span>`;

        // Recolectar datos del formulario
        const formData = new FormData(form);
        const args = [];
        let valueToSend = '0'; // Valor para msg.value (en Ether/Token)
        
        // Construir el array de argumentos en el orden del ABI
        const funcAbi = ABI.find(item => item.name === functionName);
        if (funcAbi && funcAbi.inputs.length > 0) {
             funcAbi.inputs.forEach(input => {
                const formValue = formData.get(input.name);
                
                // Manejo básico de arrays: asume valores separados por coma
                if (input.type.includes('[]')) {
                    args.push(formValue.split(',').map(s => s.trim()));
                } else {
                    args.push(formValue);
                }
            });
        }

        // Obtener el valor de Ether/Token a enviar si es una función 'payable'
        if (formData.has('_value')) {
            valueToSend = formData.get('_value') || '0';
        }
        
        try {
            // Determinar el Signer/Provider para la instancia del contrato
            const contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, functionType === 'read' ? provider : signer);
            
            if (functionType === 'read') {
                // --- LLAMADA .staticCall() para funciones view/pure ---
                
                const rawResult = await contract.getFunction(functionName).staticCall(...args);
                const result = sanitizeResult(rawResult);
                
                // Mostrar resultado de lectura
                resultDiv.innerHTML = `<div class="text-success small fw-bold mt-2">
                    <i class="bi bi-clipboard-check-fill me-1"></i> Resultado de la Consulta:
                    <pre class="mb-0 text-success bg-dark p-1 rounded" style="overflow-wrap: break-word;">${JSON.stringify(result, null, 2)}</pre>
                </div>`;

            } else {
                // --- LLAMADA .send() / Transacción ---

                // Convertir el valor de ETH a BigInt de Wei
                let txValue = { };
                if (valueToSend !== '0') {
                   txValue.value = ethers.parseEther(valueToSend);
                }
                
                // Llamar a la función de escritura
                const tx = await contract.getFunction(functionName)(...args, txValue);
                
                resultDiv.innerHTML = `<span class="text-info"><i class="bi bi-send-fill me-1"></i> Transacción enviada. Hash: <a href="#" target="_blank" class="text-info">${tx.hash.substring(0, 10)}...</a>. Esperando confirmación...</span>`;
                
                // Esperar la confirmación
                const receipt = await tx.wait(); 
                
                // Mostrar resultado de transacción exitosa
                resultDiv.innerHTML = `<div class="text-warning small fw-bold mt-2">
                    <i class="bi bi-check-circle-fill me-1"></i> Transacción Exitosa:
                    <pre class="mb-0 text-warning bg-dark p-1 rounded" style="overflow-wrap: break-word;">Bloque: ${receipt.blockNumber}\nHash: ${receipt.hash}</pre>
                    <small class="text-text-dim">La transacción ha sido confirmada en la blockchain.</small>
                </div>`;
            }

        } catch (error) {
            console.error(`Error durante la ejecución de ${functionName}:`, error);
            
            let errorMessage = "Fallo desconocido en la transacción o consulta.";

            if (error.code === 'ACTION_REJECTED') {
                errorMessage = "Transacción rechazada por el usuario en MetaMask.";
            } else if (error.reason) {
                errorMessage = `Error de Contrato: ${error.reason}`;
            } else if (error.message) {
                const match = error.message.match(/revert reason="(.*?)"/);
                errorMessage = match ? `Revertido: ${match[1]}` : `Error RPC: ${error.message.substring(0, 80)}...`;
            }

            resultDiv.innerHTML = `<div class="text-danger small fw-bold mt-2">
                <i class="bi bi-x-octagon-fill me-1"></i> Fallo de Ejecución: ${errorMessage}
            </div>`;

        } finally {
            // Desbloquear UI
            originalButton.disabled = false;
            originalButton.textContent = originalButtonText;
            
            // Si fue una transacción de escritura exitosa, actualiza el estado de la wallet
            if (functionType !== 'read' && resultDiv.innerHTML.includes('Transacción Exitosa')) {
                connectWallet();
            }
        }
    };

    /**
     * Itera sobre el ABI y genera dinámicamente los formularios de ejecución.
     */
    const generateForms = () => {
        executionFormsContainer.innerHTML = ''; 

        const writeForms = document.createElement('div');
        writeForms.innerHTML = '<h5 class="text-light mt-4 mb-3 border-bottom border-warning pb-1"><i class="bi bi-pencil-fill me-2"></i>Funciones de Escritura (Admin TX)</h5>';
        
        const readForms = document.createElement('div');
        readForms.innerHTML = '<h5 class="text-light mt-4 mb-3 border-bottom border-secondary pb-1"><i class="bi bi-eye-fill me-2"></i>Funciones de Lectura (Admin View)</h5>';
        
        // Filtrar funciones usando el parámetro targetFunctions
        const functions = ABI.filter(item => 
            item.type === 'function' && targetFunctions.includes(item.name)
        );

        functions.forEach(func => {
            const isRead = func.stateMutability === 'view' || func.stateMutability === 'pure';
            const container = isRead ? readForms : writeForms;

            // --- Creación del Colapso ---
            const card = document.createElement('div');
            card.className = 'card text-light border-info mb-3';
            card.style.backgroundColor = '#2A2E34'; // Gris pizarra oscuro
            
            const cardHeader = document.createElement('div');
            cardHeader.className = 'card-header';
            cardHeader.innerHTML = `
                <button class="btn btn-block w-100 text-start text-light fw-bold collapsed" 
                    type="button" 
                    data-bs-toggle="collapse" 
                    data-bs-target="#collapse-${func.name}" 
                    aria-expanded="false" 
                    aria-controls="collapse-${func.name}">
                    ${func.name} (${isRead ? 'LECTURA' : 'ESCRITURA'})
                </button>`;

            const collapseDiv = document.createElement('div');
            collapseDiv.id = `collapse-${func.name}`;
            collapseDiv.className = 'collapse';
            
            const cardBody = document.createElement('div');
            cardBody.className = 'card-body pt-0';
            
            const form = document.createElement('form');
            form.className = 'p-3 border rounded border-dark';
            form.setAttribute('data-function-name', func.name);
            form.setAttribute('data-function-type', isRead ? 'read' : 'write');
            
            // --- Campos de Input ---
            if (func.inputs.length > 0) {
                func.inputs.forEach(input => {
                    const formGroup = document.createElement('div');
                    formGroup.className = 'mb-3';
                    
                    const label = document.createElement('label');
                    label.className = 'form-label text-info small fw-bold';
                    const inputTypeLabel = input.type.includes('[]') ? 'array' : input.type;
                    label.textContent = `${input.name} (${inputTypeLabel}):`;
                    
                    const inputField = document.createElement('input');
                    inputField.className = 'form-control form-control-sm bg-dark text-light border-dark';
                    inputField.type = getHtmlInputType(input.type);
                    inputField.name = input.name;
                    inputField.required = true;
                    inputField.placeholder = input.type;
                    
                    // Añadir placeholder para arrays (ejemplo de formato)
                    if (input.type.includes('[]')) {
                         inputField.placeholder = `${input.type} (ej: valor1, valor2, ...)`
                    }
                    
                    formGroup.appendChild(label);
                    formGroup.appendChild(inputField);
                    form.appendChild(formGroup);
                });
            } else if (!isRead) {
                const info = document.createElement('p');
                info.className = 'text-warning small mb-3';
                info.textContent = 'Esta función no requiere argumentos de entrada.';
                form.appendChild(info);
            }
            
            // Campo de Valor (Msg.Value) si la función es 'payable'
            if (func.stateMutability === 'payable') {
                const valueGroup = document.createElement('div');
                valueGroup.className = 'mb-3';
                valueGroup.innerHTML = `
                    <label class="form-label text-warning small fw-bold">Valor a Enviar (ETH):</label>
                    <input type="text" min="0" class="form-control form-control-sm bg-dark text-light border-warning" name="_value" placeholder="Monto en ETH (e.g., 0.5)">
                    <small class="text-text-dim">Requerido para transacciones de pago.</small>
                `;
                form.appendChild(valueGroup);
            }

            // --- Botón de Ejecución ---
            const button = document.createElement('button');
            button.type = 'submit';
            button.className = isRead 
                ? 'btn btn-sm btn-outline-info w-100 mt-2' 
                : 'btn btn-sm btn-warning w-100 mt-2';
            button.textContent = isRead ? 'Consultar (CALL)' : 'Ejecutar (SEND TX)';
            form.appendChild(button);

            // Placeholder de Resultado
            const resultDiv = document.createElement('div');
            resultDiv.className = 'mt-3 p-2 border border-secondary rounded bg-dark small text-break';
            resultDiv.id = `result-${func.name}`;
            resultDiv.textContent = isRead ? 'Resultado de la consulta: --' : 'Esperando interacción de MetaMask...';
            form.appendChild(resultDiv);
            
            // Asignar manejador de envío
            form.addEventListener('submit', handleFunctionExecution);
            
            cardBody.appendChild(form);
            collapseDiv.appendChild(cardBody);
            card.appendChild(cardHeader);
            card.appendChild(collapseDiv);
            
            container.appendChild(card);
        });
        
        // Agregar secciones al contenedor principal
        executionFormsContainer.appendChild(writeForms);
        executionFormsContainer.appendChild(readForms);
        
        if (functions.length === 0) {
            executionFormsContainer.innerHTML = '<p class="text-danger">No se encontraron funciones administrativas válidas en el ABI.</p>';
        }
    };
    
    // Generar formularios al iniciar el módulo
    generateForms();

    return {
        connectWallet: connectWallet,
        generateForms: generateForms,
        // NUEVA FUNCIÓN EXPUESTA:
        fetchContractBalance: fetchContractBalance 
    };
};
