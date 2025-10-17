// -------------------------------------------------------------------------
// CÓDIGO UTILITARIO Y LÓGICA DE GENERACIÓN DE FORMULARIOS (REAL Ethers.js)
// -------------------------------------------------------------------------

// Verificación de disponibilidad de Ethers
if (typeof ethers === 'undefined') {
    console.error("Ethers.js no está cargado. Asegúrate de incluirlo correctamente.");
}

/**
 * Objeto de Utilidades para el Dashboard de Administración
 * Maneja la conexión Web3 y la ejecución de funciones de contrato usando Ethers.js.
 */
const AdminDashboardUtils = (() => {

    // --- ESTADO GLOBAL WEB3 REAL ---
    let provider = null;
    let signer = null;
    let userAccount = null;

    // Carga de datos de contexto
    const CONTRACT_ADDRESS = JSON.parse(document.getElementById('contract-address-data').textContent);
    const ABI = JSON.parse(document.getElementById('contract-abi-data').textContent);
    const REQUIRED_CHAIN_ID = parseInt(document.getElementById('contract-chain-id-data').textContent);
    const REQUIRED_RPC_URL = JSON.parse(document.getElementById('contract-rpc-url-data').textContent);
    const REQUIRED_NETWORK_NAME = document.getElementById('required-network-name').textContent;


    // Referencias del DOM
    const statusTextEl = document.getElementById('metamask-status-text');
    const connectBtnEl = document.getElementById('connect-metamask-btn');
    const statusCardEl = document.getElementById('metamask-status-card');

    /**
     * Maneja el cambio forzado de red en MetaMask.
     * @param {number} chainIdDecimal - El ID de la cadena en formato decimal.
     */
    const switchNetwork = async (chainIdDecimal) => {
        const chainIdHex = ethers.toBeHex(chainIdDecimal);
        try {
            // Intenta cambiar de red (si ya existe en MetaMask)
            await window.ethereum.request({
                method: 'wallet_switchEthereumChain',
                params: [{ chainId: chainIdHex }],
            });
            // Si tiene éxito, se recarga automáticamente por el listener 'chainChanged'
        } catch (switchError) {
            // Si la red no está en MetaMask, intenta añadirla
            if (switchError.code === 4902) {
                try {
                    await window.ethereum.request({
                        method: 'wallet_addEthereumChain',
                        params: [{
                            chainId: chainIdHex,
                            rpcUrls: [REQUIRED_RPC_URL],
                            chainName: REQUIRED_NETWORK_NAME,
                            nativeCurrency: { name: 'ETH', symbol: 'ETH', decimals: 18 } // Asunción de ETH, esto podría ser más específico
                        }],
                    });
                } catch (addError) {
                    console.error("No se pudo añadir la red:", addError);
                    statusTextEl.innerHTML = `<i class="bi bi-x-octagon-fill text-danger me-1"></i> Fallo al añadir la red.`;
                }
            } else {
                console.error("Error al cambiar de red:", switchError);
                statusTextEl.innerHTML = `<i class="bi bi-exclamation-octagon-fill text-danger me-1"></i> Error al cambiar de red.`;
            }
        }
    };

    /**
     * Actualiza la interfaz de usuario para reflejar el estado de la conexión de MetaMask.
     * @param {string | null} account - La dirección de la cuenta conectada.
     * @param {number | null} currentChainId - El Chain ID de la red actual de MetaMask.
     */
    const updateConnectionStatus = (account, currentChainId) => {
        statusCardEl.classList.remove('border-secondary', 'border-success', 'border-warning', 'wrong-network');

        if (!account) {
            userAccount = null;
            signer = null;
            provider = null;
            statusTextEl.innerHTML = `<i class="bi bi-x-circle-fill text-danger me-1"></i> Wallet Desconectada`;
            connectBtnEl.textContent = 'Conectar Wallet';
            connectBtnEl.disabled = false;
            statusCardEl.classList.add('border-secondary');
            return;
        }

        // 1. Verificar la Red
        const isOnRequiredNetwork = currentChainId === REQUIRED_CHAIN_ID;

        if (!isOnRequiredNetwork) {
            // Red Incorrecta
            statusTextEl.innerHTML = `<i class="bi bi-exclamation-triangle-fill text-warning me-1"></i> Red Incorrecta (ID: ${currentChainId || '?'})`;
            connectBtnEl.textContent = `Cambiar a ${REQUIRED_NETWORK_NAME}`;
            connectBtnEl.disabled = false;
            connectBtnEl.onclick = () => switchNetwork(REQUIRED_CHAIN_ID);
            statusCardEl.classList.add('wrong-network');
            // IMPORTANTE: Bloquear la ejecución de transacciones si la red es incorrecta.
            userAccount = null;
        } else {
            // Conectado y Red Correcta
            userAccount = account;
            const shortAddress = `${account.substring(0, 6)}...${account.substring(account.length - 4)}`;
            statusTextEl.innerHTML = `<i class="bi bi-wallet-fill text-success me-1"></i> Conectado: ${shortAddress}`;
            connectBtnEl.textContent = 'Wallet Conectada';
            connectBtnEl.disabled = true;
            connectBtnEl.onclick = null; // Quita el manejador de cambio de red
            statusCardEl.classList.add('border-success');
        }
    };

    /**
     * Inicializa el Provider y el Signer, y maneja la conexión con MetaMask.
     */
    const connectWallet = async () => {
        if (typeof window.ethereum === 'undefined' || typeof ethers === 'undefined') {
            statusTextEl.innerHTML = `<i class="bi bi-exclamation-triangle-fill text-danger me-1"></i> MetaMask no detectado`;
            statusCardEl.classList.add('border-danger');
            return;
        }

        try {
            // 1. Crear el BrowserProvider de Ethers
            provider = new ethers.BrowserProvider(window.ethereum);

            // 2. Solicitar cuentas y obtener el signer
            const accounts = await provider.send("eth_requestAccounts", []);
            const connectedAccount = accounts[0];

            signer = await provider.getSigner();

            // 3. Obtener el Chain ID actual
            const network = await provider.getNetwork();
            const currentChainId = parseInt(network.chainId); // Chain ID en decimal

            updateConnectionStatus(connectedAccount, currentChainId);

            // 4. Establecer listeners para cambios de cuenta/red
            window.ethereum.on('accountsChanged', (newAccounts) => {
                window.location.reload(); // Simple y efectivo para resincronizar el estado
            });

            window.ethereum.on('chainChanged', () => {
                window.location.reload(); // Resincroniza la página con la nueva red
            });

        } catch (error) {
            console.error("Error al conectar MetaMask:", error);
            // 4001 es generalmente "user rejected request"
            if (error.code !== 4001) {
                statusTextEl.innerHTML = `<i class="bi bi-exclamation-triangle-fill text-danger me-1"></i> Conexión fallida`;
                statusCardEl.classList.remove('border-secondary');
                statusCardEl.classList.add('border-warning');
            }
            updateConnectionStatus(null, null);
        }
    };

    /**
     * Mapea tipos de Solidity a tipos de input HTML.
     */
    const getHtmlInputType = (solidityType) => {
        return 'text';
    };

    /**
     * Convierte el resultado de una función de contrato (incluidos BigInt) a un JSON legible.
     */
    const sanitizeResult = (result) => {
        if (result === null || typeof result !== 'object') {
            return result;
        }

        if (Array.isArray(result)) {
            return result.map(item => sanitizeResult(item));
        }

        // Manejo de BigInt (Ethers v6)
        if (typeof result === 'bigint') {
            return result.toString();
        }

        // Manejo de objetos, incluyendo los resultados con nombres (como Ethers los devuelve)
        const sanitized = {};
        for (const key in result) {
            // Filtra keys numéricas redundantes de tuplas (Ethers)
            if (isNaN(parseInt(key))) {
                sanitized[key] = sanitizeResult(result[key]);
            }
        }
        return sanitized;
    }

    /**
     * Maneja el envío del formulario, realizando una llamada Web3 real.
     */
    const handleFunctionExecution = async (event) => {
        event.preventDefault();

        const form = event.target;
        const functionName = form.getAttribute('data-function-name');
        const functionType = form.getAttribute('data-function-type');
        const resultDiv = document.getElementById(`result-${functionName}`);

        // --- VERIFICACIÓN CRÍTICA DE ESTADO ---
        if (!userAccount && functionType === 'write') {
            resultDiv.innerHTML = `<div class="text-danger small fw-bold mt-2">
                    <i class="bi bi-lock-fill me-1"></i> Debes conectar tu wallet a la red **correcta** para enviar transacciones.
                </div>`;
            return;
        }
        if (!signer && functionType === 'write') {
            resultDiv.innerHTML = `<div class="text-danger small fw-bold mt-2">
                    <i class="bi bi-lock-fill me-1"></i> La wallet no está lista. Intenta reconectar.
                </div>`;
            return;
        }
        // ------------------------------------

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
                    // Ethers espera un Array de strings para la mayoría de los arrays.
                    args.push(formValue.split(',').map(s => s.trim()));
                } else {
                    // Simplemente empujar el valor de cadena. Ethers intentará parsear los tipos.
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

                // Usa getFunction().staticCall()
                const rawResult = await contract.getFunction(functionName).staticCall(...args);

                // Sanear el resultado
                const result = sanitizeResult(rawResult);

                // Mostrar resultado de lectura
                resultDiv.innerHTML = `<div class="text-success small fw-bold mt-2">
                        <i class="bi bi-clipboard-check-fill me-1"></i> Resultado de la Consulta:
                        <pre class="mb-0 text-success bg-dark p-1 rounded" style="overflow-wrap: break-word;">${JSON.stringify(result, null, 2)}</pre>
                    </div>`;

            } else {
                // --- LLAMADA .send() / Transacción ---

                // Convertir el valor de ETH a BigInt de Wei
                let txValue = {};
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
                // Intenta parsear un error de revert más detallado de MetaMask/Ethers
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
        }
    };

    /**
     * Itera sobre el ABI para generar los formularios de ejecución.
     * @param {Array} abi - El Array del Contrato ABI.
     * @param {Array} targetFunctions - La lista de nombres de funciones a incluir.
     */
    const generateForms = (abi, targetFunctions) => {
        const executionFormsContainer = document.getElementById('execution-forms-container');
        executionFormsContainer.innerHTML = '';

        const writeForms = document.createElement('div');
        writeForms.innerHTML = '<h5 class="text-light mt-4 mb-3 border-bottom border-warning pb-1"><i class="bi bi-pencil-fill me-2"></i>Funciones de Escritura (Admin TX)</h5>';

        const readForms = document.createElement('div');
        readForms.innerHTML = '<h5 class="text-light mt-4 mb-3 border-bottom border-secondary pb-1"><i class="bi bi-eye-fill me-2"></i>Funciones de Lectura (Admin View)</h5>';

        // Filtrar funciones usando el parámetro targetFunctions
        const functions = abi.filter(item =>
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

    return {
        generateForms: generateForms,
        connectWallet: connectWallet
    };
})();