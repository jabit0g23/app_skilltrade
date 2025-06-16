// ===== CONSTANTES =====
const AUTH_KEY = 'skilltrade_auth';
const USER_KEY = 'skilltrade_user';

// ===== VERIFICACIÓN DE AUTENTICACIÓN =====
function isAuthenticated() {
    return localStorage.getItem(AUTH_KEY) === 'true';
}

function getCurrentUser() {
    const userData = localStorage.getItem(USER_KEY);
    return userData ? JSON.parse(userData) : null;
}

// ===== CONFIGURACIÓN DEL NAVBAR SEGÚN ESTADO DE AUTENTICACIÓN =====
function setupNavbar() {
    const navbar = document.querySelector('.navbar');
    const navContainer = document.querySelector('.nav-container');
    
    if (!navbar || !navContainer) return;
    
    if (isAuthenticated()) {
        setupAuthenticatedNavbar();
    } else {
        setupPublicNavbar();
    }
}

function setupPublicNavbar() {
    const navContainer = document.querySelector('.nav-container');
    const navbar = document.querySelector('.navbar');
    
    navbar.classList.add('public-nav');
    
    navContainer.innerHTML = `
        <div class="nav-links">
            <a href="index.html" class="nav-link">INICIO</a>
            <a href="publicaciones.html" class="nav-link">PUBLICACIONES</a>
            <a href="#" class="nav-link">SOBRE NOSOTROS</a>
        </div>
    `;
    
    // Marcar enlace activo
    setActiveNavLink();
}

function setupAuthenticatedNavbar() {
    const navContainer = document.querySelector('.nav-container');
    const navbar = document.querySelector('.navbar');
    const user = getCurrentUser();
    
    navbar.classList.remove('public-nav');
    
    if (!user || !user.name) {
        console.warn(' Usuario sin datos válidos, cerrando sesión...');
        logout();
        return;
    }
    
    const userInitials = user.name.split(' ').map(n => n[0]).join('').toUpperCase();
    
    navContainer.innerHTML = `
        <div class="nav-links">
            <a href="dashboard.html" class="nav-link">PERFIL</a>
            <a href="publicaciones.html" class="nav-link">PUBLICACIONES</a>
        </div>
        <div class="user-info">
            <div class="user-avatar">${userInitials}</div>
            <span class="user-name">${user.name}</span>
            <button class="btn-logout" onclick="logout()">
                <i class="fas fa-sign-out-alt"></i> CERRAR SESIÓN
            </button>
        </div>
    `;
    
    // Marcar enlace activo
    setActiveNavLink();
}

function setActiveNavLink() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        const href = link.getAttribute('href');
        
        if (href === currentPage || 
            (currentPage === 'index.html' && href === 'index.html') ||
            (currentPage === 'publicaciones.html' && href === 'publicaciones.html') ||
            (currentPage === 'dashboard.html' && href === 'dashboard.html')) {
            link.classList.add('active');
        }
    });
}

// ===== FUNCIONES DE LOGIN Y LOGOUT =====
function login(userData) {
    try {
        localStorage.setItem(AUTH_KEY, 'true');
        localStorage.setItem(USER_KEY, JSON.stringify(userData));
        setupNavbar();
        return true;
    } catch (error) {
        console.error('Error al guardar datos de usuario:', error);
        return false;
    }
}

function logout() {
    localStorage.removeItem(AUTH_KEY);
    localStorage.removeItem(USER_KEY);
    
    // Mostrar mensaje de logout
    showLoading('Cerrando sesión...');
    
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 1500);
}

// ===== VALIDACIONES =====
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validatePassword(password) {
    if (password.length < 6) {
        return { valid: false, message: 'La contraseña debe tener al menos 6 caracteres' };
    }
    return { valid: true };
}

function validateName(name) {
    if (name.trim().length < 2) {
        return { valid: false, message: 'El nombre debe tener al menos 2 caracteres' };
    }
    return { valid: true };
}

// ===== MANEJO DE FORMULARIOS CON BACKEND REAL =====
async function handleLoginForm(email, password) {
    try {
        // Validaciones
        if (!email || !password) {
            throw new Error('Por favor completa todos los campos');
        }
        
        if (!isValidEmail(email)) {
            throw new Error('Por favor ingresa un email válido');
        }
        
        // Asegurar que el WebSocket esté conectado
        if (!SkillTradeAPI.wsManager.isConnected) {
            showLoading('Conectando al servidor...');
            await SkillTradeAPI.wsManager.connect();
            hideLoading();
        }
        
        // Intentar login con el backend real
        const result = await SkillTradeAPI.loginUser(email, password);
        
        if (result.success) {
            if (login(result.user)) {
                return { success: true, user: result.user };
            } else {
                throw new Error('Error al guardar los datos de usuario');
            }
        } else {
            throw new Error(result.message || 'Error de autenticación');
        }
        
    } catch (error) {
        console.error(' Error en login:', error);
        
        // Mostrar error específico según el tipo
        let message = error.message;
        if (error.message.includes('WebSocket') || error.message.includes('conexión')) {
            message = 'No se puede conectar al servidor. Verifica que el backend esté corriendo (docker-compose up).';
        } else if (error.message.includes('Timeout')) {
            message = 'El servidor no responde. Verifica que todos los servicios estén funcionando.';
        }
        
        return { success: false, message };
    }
}

async function handleRegisterForm(name, email, password, confirmPassword) {
    try {
        // Validaciones
        if (!name || !email || !password || !confirmPassword) {
            throw new Error('Por favor completa todos los campos');
        }
        
        const nameValidation = validateName(name);
        if (!nameValidation.valid) {
            throw new Error(nameValidation.message);
        }
        
        if (!isValidEmail(email)) {
            throw new Error('Por favor ingresa un email válido');
        }
        
        const passwordValidation = validatePassword(password);
        if (!passwordValidation.valid) {
            throw new Error(passwordValidation.message);
        }
        
        if (password !== confirmPassword) {
            throw new Error('Las contraseñas no coinciden');
        }
        
        // Asegurar que el WebSocket esté conectado
        if (!SkillTradeAPI.wsManager.isConnected) {
            showLoading('Conectando al servidor...');
            await SkillTradeAPI.wsManager.connect();
            hideLoading();
        }
        
        // Intentar registro con el backend real
        const userData = {
            name: name.trim(),
            email: email.trim().toLowerCase(),
            password: password
        };
        
        const result = await SkillTradeAPI.registerUser(userData);
        
        if (result.success) {
            if (login(result.user)) {
                return { success: true, user: result.user };
            } else {
                throw new Error('Error al guardar los datos de usuario');
            }
        } else {
            throw new Error(result.message || 'Error al crear la cuenta');
        }
        
    } catch (error) {
        console.error(' Error en registro:', error);
        
        // Mostrar error específico según el tipo
        let message = error.message;
        if (error.message.includes('WebSocket') || error.message.includes('conexión')) {
            message = 'No se puede conectar al servidor. Verifica que el backend esté corriendo (docker-compose up).';
        } else if (error.message.includes('Timeout')) {
            message = 'El servidor no responde. Verifica que todos los servicios estén funcionando.';
        }
        
        return { success: false, message };
    }
}

// ===== UTILIDADES DE UI =====
function showError(errorDiv, message) {
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

function showLoading(message = 'Cargando...') {
    let overlay = document.getElementById('loadingOverlay');
    
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <i class="fas fa-spinner fa-spin"></i>
                <p>${message}</p>
            </div>
        `;
        document.body.appendChild(overlay);
    } else {
        const loadingText = overlay.querySelector('p');
        if (loadingText) {
            loadingText.textContent = message;
        }
    }
    
    overlay.style.display = 'flex';
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

function showSuccessMessage(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span>${message}</span>
    `;
    document.body.appendChild(successDiv);
    
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// ===== PROTECCIÓN DE RUTAS =====
function requireAuth() {
    if (!isAuthenticated()) {
        showLoading('Redirigiendo al login...');
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1500);
        return false;
    }
    return true;
}

function redirectIfAuthenticated() {
    if (isAuthenticated()) {
        showLoading('Redirigiendo al dashboard...');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1500);
        return true;
    }
    return false;
}

// ===== MANEJO DE MODALES =====
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        
        // Limpiar errores previos
        const errorDiv = modal.querySelector('.error-message');
        if (errorDiv) {
            errorDiv.style.display = 'none';
            errorDiv.textContent = '';
        }
        
        // Focus en primer input
        setTimeout(() => {
            const firstInput = modal.querySelector('input');
            if (firstInput) {
                firstInput.focus();
            }
        }, 300);
        
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        
        // Resetear formulario
        const form = modal.querySelector('form');
        if (form) {
            form.reset();
        }
        
        // Limpiar errores
        const errorDiv = modal.querySelector('.error-message');
        if (errorDiv) {
            errorDiv.style.display = 'none';
            errorDiv.textContent = '';
        }
        
        document.body.style.overflow = 'auto';
    }
}

function closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (modal.style.display === 'block') {
            closeModal(modal.id);
        }
    });
}

// ===== FUNCIÓN DE ESTADO DE BACKEND (NUEVA) =====
function showBackendStatus(isConnected, statusMessage = '') {
    // Actualizar cualquier elemento de estado del backend
    const statusElement = document.getElementById('backendStatus');
    if (statusElement) {
        if (isConnected) {
            statusElement.innerHTML = `
                <span style="color: #28a745;"> Backend conectado</span><br>
                <small>${statusMessage || 'WebSocket activo'}</small>
            `;
        } else {
            statusElement.innerHTML = `
                <span style="color: #dc3545;"> Backend desconectado</span><br>
                <small>${statusMessage || 'Verificar docker-compose'}</small>
            `;
        }
    }
    
    // También actualizar en consola
    if (isConnected) {
        console.log(` Estado del backend: Conectado - ${statusMessage}`);
    } else {
        console.warn(` Estado del backend: Desconectado - ${statusMessage}`);
    }
}

// ===== VERIFICACIÓN DE CONECTIVIDAD DEL BACKEND =====
async function checkBackendConnection() {
    // Verificar que SkillTradeAPI esté disponible con reintentos
    let attempts = 0;
    const maxAttempts = 5;
    
    const waitForAPI = () => {
        return new Promise((resolve) => {
            const checkAPI = () => {
                attempts++;
                if (typeof SkillTradeAPI !== 'undefined') {
                    console.log(` SkillTradeAPI disponible después de ${attempts} intentos`);
                    resolve(true);
                } else if (attempts < maxAttempts) {
                    console.log(` Esperando SkillTradeAPI... intento ${attempts}/${maxAttempts}`);
                    setTimeout(checkAPI, 500);
                } else {
                    console.warn(' SkillTradeAPI no está disponible después de múltiples intentos');
                    resolve(false);
                }
            };
            checkAPI();
        });
    };
    
    const apiAvailable = await waitForAPI();
    
    if (!apiAvailable) {
        showBackendStatus(false, 'API no cargada');
        return false;
    }
    
    try {
        if (SkillTradeAPI.wsManager.isConnected) {
            console.log(' WebSocket ya conectado');
            showBackendStatus(true, 'Conectado');
            return true;
        }
        
        console.log(' Intentando conectar al backend...');
        await SkillTradeAPI.wsManager.connect();
        
        // Probar un servicio simple
        await SkillTradeAPI.getUserById(999999); // Usuario que no existe, solo para probar
        
        console.log(' Backend conectado correctamente');
        showBackendStatus(true, 'Conectado y funcionando');
        return true;
        
    } catch (error) {
        console.warn(' Backend no disponible:', error.message);
        showBackendStatus(false, error.message);
        return false;
    }
}

// ===== INICIALIZACIÓN AUTOMÁTICA =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('SkillTrade Auth inicializando...');
    setupNavbar();
    
    // Verificar conexión del backend después de que se cargue la API
    // Usar un timeout más largo para asegurar que SkillTradeAPI esté disponible
    setTimeout(() => {
        checkBackendConnection();
    }, 2000);
});

// ===== EXPORTAR FUNCIONES PARA USO GLOBAL =====
window.SkillTradeAuth = {
    isAuthenticated,
    getCurrentUser,
    login,
    logout,
    requireAuth,
    redirectIfAuthenticated,
    handleLoginForm,
    handleRegisterForm,
    setupNavbar,
    openModal,
    closeModal,
    showError,
    showLoading,
    hideLoading,
    showSuccessMessage,
    isValidEmail,
    validatePassword,
    validateName,
    checkBackendConnection,
    showBackendStatus
};