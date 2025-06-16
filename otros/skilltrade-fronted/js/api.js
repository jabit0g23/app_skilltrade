// ===== CONEXIÓN CON BACKEND =====

// ===== CONSTANTES =====
const WS_URL = 'ws://localhost:8000/ws'; // WebSocket del backend
const PREFIX_LEN = 5;
const INTERESTS_KEY = 'skilltrade_interests'; // Mantener intereses en localStorage hasta implementar en backend

// ===== WEBSOCKET CONNECTION MANAGER =====
class WebSocketManager {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.messageQueue = [];
        this.pendingRequests = new Map();
        this.requestId = 0;
    }

    connect() {
        return new Promise((resolve, reject) => {
            try {
                this.ws = new WebSocket(WS_URL);
                
                this.ws.onopen = () => {
                    console.log(' WebSocket conectado al backend');
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    
                    // Procesar mensajes en cola
                    this.processMessageQueue();
                    
                    resolve();
                };
                
                this.ws.onmessage = (event) => {
                    this.handleMessage(event.data);
                };
                
                this.ws.onclose = () => {
                    console.warn(' WebSocket desconectado');
                    this.isConnected = false;
                    this.attemptReconnect();
                };
                
                this.ws.onerror = (error) => {
                    console.error(' Error en WebSocket:', error);
                    this.isConnected = false;
                    reject(error);
                };
                
            } catch (error) {
                console.error(' Error al crear WebSocket:', error);
                reject(error);
            }
        });
    }

    handleMessage(data) {
        try {
            // El backend devuelve el prefijo + payload
            const prefixStr = data.slice(0, PREFIX_LEN);
            const length = parseInt(prefixStr);
            const serviceResponse = data.slice(PREFIX_LEN, PREFIX_LEN + length);
            
            console.log(' Respuesta del backend:', serviceResponse);
            
            // Procesar respuesta basada en el service ID
            const serviceId = serviceResponse.slice(0, 5);
            const response = serviceResponse.slice(5);
            
            // Resolver promesa pendiente si existe
            for (const [pendingServiceId, { resolve }] of this.pendingRequests.entries()) {
                if (serviceResponse.startsWith(pendingServiceId)) {
                    this.pendingRequests.delete(pendingServiceId);
                    resolve({ serviceId: pendingServiceId, response });
                    return;
                }
            }
            
        } catch (error) {
            console.error(' Error al procesar mensaje:', error);
        }
    }

    sendMessage(serviceId, payload) {
        return new Promise((resolve, reject) => {
            if (!this.isConnected) {
                console.warn(' WebSocket no conectado, agregando a cola...');
                this.messageQueue.push({ serviceId, payload, resolve, reject });
                this.connect().catch(reject);
                return;
            }

            try {
                const body = serviceId + payload;
                const prefix = String(body.length).padStart(PREFIX_LEN, '0');
                const message = prefix + body;
                
                console.log(' Enviando al backend:', { serviceId, payload, message });
                
                // Guardar promesa pendiente
                this.pendingRequests.set(serviceId, { resolve, reject });
                
                this.ws.send(message);
                
                // Timeout para evitar promesas colgadas
                setTimeout(() => {
                    if (this.pendingRequests.has(serviceId)) {
                        this.pendingRequests.delete(serviceId);
                        reject(new Error('Timeout: El backend no respondió'));
                    }
                }, 10000); // 10 segundos timeout
                
            } catch (error) {
                console.error(' Error al enviar mensaje:', error);
                reject(error);
            }
        });
    }

    processMessageQueue() {
        while (this.messageQueue.length > 0 && this.isConnected) {
            const { serviceId, payload, resolve, reject } = this.messageQueue.shift();
            this.sendMessage(serviceId, payload).then(resolve).catch(reject);
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(` Reintentando conexión (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
                this.connect().catch(console.error);
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.error(' Máximo de reintentos alcanzado. Backend no disponible.');
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
            this.isConnected = false;
        }
    }
}

// Instancia global del WebSocket manager
const wsManager = new WebSocketManager();

// ===== CATEGORÍAS (mantener del frontend) =====
const CATEGORIES = [
    { value: '', label: 'Todas las categorías' },
    { value: 'tecnología', label: 'Tecnología' },
    { value: 'idiomas', label: 'Idiomas' },
    { value: 'música', label: 'Música' },
    { value: 'arte', label: 'Arte y Diseño' },
    { value: 'deporte', label: 'Deporte y Fitness' },
    { value: 'cocina', label: 'Cocina' },
    { value: 'oficios', label: 'Oficios' },
    { value: 'bienestar', label: 'Bienestar' },
    { value: 'negocios', label: 'Negocios' },
    { value: 'educación', label: 'Educación' }
];

// ===== FUNCIONES DE USUARIOS =====
async function registerUser(userData) {
    try {
        // Asegurar conexión
        if (!wsManager.isConnected) {
            await wsManager.connect();
        }
        
        // Formato esperado por USREG: "nombre;email;contrasena"
        const payload = `${userData.name};${userData.email};${userData.password}`;
        const result = await wsManager.sendMessage('USREG', payload);
        
        if (result.response.startsWith('OK')) {
            // USREG-OK:user_id
            const userId = result.response.split(':')[1];
            
            return { 
                success: true, 
                user: {
                    id: parseInt(userId),
                    name: userData.name,
                    email: userData.email,
                    joinDate: new Date().toISOString(),
                    skills: '',
                    bio: '',
                    location: ''
                }
            };
        } else {
            // USREG-ERR:mensaje
            const errorMessage = result.response.split(':')[1] || 'Error en el registro';
            return { success: false, message: errorMessage };
        }
        
    } catch (error) {
        console.error(' Error en registerUser:', error);
        return { success: false, message: `Error de conexión: ${error.message}` };
    }
}

async function loginUser(email, password) {
    try {
        // Asegurar conexión
        if (!wsManager.isConnected) {
            await wsManager.connect();
        }
        
        // Formato esperado por USLOG: "email;contrasena"
        const payload = `${email};${password}`;
        const result = await wsManager.sendMessage('USLOG', payload);
        
        if (result.response.startsWith('OK')) {
            // USLOG-OK:user_id;nombre_usuario
            const [userId, userName] = result.response.split(':')[1].split(';');
            
            return { 
                success: true, 
                user: {
                    id: parseInt(userId),
                    name: userName,
                    email: email,
                    joinDate: new Date().toISOString(),
                    skills: '',
                    bio: '',
                    location: ''
                }
            };
        } else {
            // USLOG-ERR:mensaje
            const errorMessage = result.response.split(':')[1] || 'Credenciales inválidas';
            return { success: false, message: errorMessage };
        }
        
    } catch (error) {
        console.error(' Error en loginUser:', error);
        return { success: false, message: `Error de conexión: ${error.message}` };
    }
}

async function getUserById(userId) {
    try {
        if (!wsManager.isConnected) {
            await wsManager.connect();
        }
        
        // Formato esperado por USGET: "usuario_id"
        const payload = `${userId}`;
        const result = await wsManager.sendMessage('USGET', payload);
        
        if (result.response.startsWith('OK')) {
            // USGET-OK:usuario_id;nombre_usuario;email;reputacion
            const [id, name, email, reputation] = result.response.split(':')[1].split(';');
            
            return {
                id: parseInt(id),
                name: name,
                email: email,
                joinDate: new Date().toISOString(), // El backend no devuelve fecha, usar actual
                skills: '',
                bio: '',
                location: '',
                reputation: parseFloat(reputation) || 0
            };
        } else {
            console.error('Error al obtener usuario:', result.response);
            return null;
        }
        
    } catch (error) {
        console.error(' Error en getUserById:', error);
        return null;
    }
}

async function updateUser(userId, updates) {
    try {
        if (!wsManager.isConnected) {
            await wsManager.connect();
        }
        
        // Formato esperado por USUPD: "usuario_id;nombre;email;contrasena"
        // Nota: El backend actual requiere contraseña, necesitarías modificar el servicio para updates parciales
        const payload = `${userId};${updates.name};${updates.email};${updates.password || ''}`;
        const result = await wsManager.sendMessage('USUPD', payload);
        
        if (result.response.startsWith('OK')) {
            return { 
                success: true, 
                user: {
                    id: userId,
                    name: updates.name,
                    email: updates.email,
                    joinDate: new Date().toISOString(),
                    skills: updates.skills || '',
                    bio: updates.bio || '',
                    location: updates.location || ''
                }
            };
        } else {
            const errorMessage = result.response.split(':')[1] || 'Error al actualizar usuario';
            return { success: false, message: errorMessage };
        }
        
    } catch (error) {
        console.error(' Error en updateUser:', error);
        return { success: false, message: error.message };
    }
}

async function getUserPublications(userId) {
    try {
        if (!wsManager.isConnected) {
            await wsManager.connect();
        }
        
        // Para obtener publicaciones del usuario, usamos PBLST y luego filtramos
        // O implementamos un servicio específico en el backend
        const publications = await getAllPublications();
        return publications.filter(pub => pub.userId === parseInt(userId));
        
    } catch (error) {
        console.error(' Error en getUserPublications:', error);
        return [];
    }
}

async function getAllPublications() {
    try {
        if (!wsManager.isConnected) {
            await wsManager.connect();
        }
        
        // Para obtener todas las publicaciones, probablemente necesites usar PBLST con parámetros específicos
        // Formato PBLST: "tipo;texto_busqueda"
        const payload = 'oferta;'; // Buscar ofertas sin filtro de texto
        const result = await wsManager.sendMessage('PBLST', payload);
        
        if (result.response.startsWith('OK')) {
            const publicationsData = result.response.slice(3); // Remover "OK:"
            
            if (!publicationsData) {
                return [];
            }
            
            // Parsear publicaciones separadas por "|"
            const publications = publicationsData.split('|').map((pub, index) => {
                const [id, userId, tipo, descripcion, categoria, etiquetas] = pub.split(';');
                return {
                    id: parseInt(id) || index,
                    userId: parseInt(userId),
                    userName: 'Usuario', // El servicio actual no devuelve nombre
                    userEmail: '',
                    title: descripcion || 'Sin título',
                    description: descripcion || '',
                    skillOffered: descripcion || '',
                    skillWanted: '',
                    category: categoria || 'general',
                    tags: etiquetas ? etiquetas.split(',').map(tag => tag.trim()) : [],
                    createdAt: new Date().toISOString(),
                    status: 'active',
                    interests: 0,
                    views: 0
                };
            });
            
            return publications;
        } else {
            console.error('Error al obtener publicaciones:', result.response);
            return [];
        }
        
    } catch (error) {
        console.error(' Error en getAllPublications:', error);
        return [];
    }
}

// ===== FUNCIONES DE PUBLICACIONES ADICIONALES =====
async function searchPublications(searchQuery = '', categoryFilter = '', sortFilter = 'recent') {
    try {
        // Por ahora usar getAllPublications y filtrar en frontend
        // En el futuro se puede implementar búsqueda en el backend
        let publications = await getAllPublications();
        
        // Filtrar por búsqueda
        if (searchQuery) {
            publications = publications.filter(pub => 
                pub.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                pub.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                pub.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
            );
        }
        
        // Filtrar por categoría
        if (categoryFilter) {
            publications = publications.filter(pub => 
                pub.category.toLowerCase() === categoryFilter.toLowerCase()
            );
        }
        
        // Ordenar
        switch (sortFilter) {
            case 'popular':
                publications.sort((a, b) => (b.views + b.interests) - (a.views + a.interests));
                break;
            case 'interests':
                publications.sort((a, b) => b.interests - a.interests);
                break;
            case 'recent':
            default:
                publications.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
                break;
        }
        
        return publications;
    } catch (error) {
        console.error(' Error en searchPublications:', error);
        return [];
    }
}

async function getPublicationById(id) {
    try {
        if (!wsManager.isConnected) {
            await wsManager.connect();
        }
        
        // Usar PBGET para obtener detalles de una publicación específica
        const payload = `${id}`;
        const result = await wsManager.sendMessage('PBGET', payload);
        
        if (result.response.startsWith('OK')) {
            // PBGET-OK:publicacion_id;usuario_id;tipo_publicacion;descripcion_habilidad;cat;tags
            const [pubId, userId, tipo, descripcion, categoria, etiquetas] = result.response.split(':')[1].split(';');
            
            return {
                id: parseInt(pubId),
                userId: parseInt(userId),
                userName: 'Usuario', // El servicio actual no devuelve nombre
                userEmail: '',
                title: descripcion || 'Sin título',
                description: descripcion || '',
                skillOffered: descripcion || '',
                skillWanted: '',
                category: categoria || 'general',
                tags: etiquetas ? etiquetas.split(',').map(tag => tag.trim()) : [],
                createdAt: new Date().toISOString(),
                status: 'active',
                interests: 0,
                views: 0
            };
        } else {
            console.error('Error al obtener publicación:', result.response);
            return null;
        }
        
    } catch (error) {
        console.error(' Error en getPublicationById:', error);
        return null;
    }
}

async function createPublication(publicationData) {
    try {
        if (!wsManager.isConnected) {
            await wsManager.connect();
        }
        
        const currentUser = SkillTradeAuth.getCurrentUser();
        if (!currentUser) {
            return { success: false, message: 'Usuario no autenticado' };
        }
        
        // Formato PBNCR: "usuario_id;tipo;descripcion;categoria_id;et1,et2"
        // Por ahora usar tipo 'oferta' y categoria_id = 1
        const payload = `${currentUser.id};oferta;${publicationData.description};1;${publicationData.tags.join(',')}`;
        const result = await wsManager.sendMessage('PBNCR', payload);
        
        if (result.response.startsWith('OK')) {
            const publicationId = result.response.split(':')[1];
            return { 
                success: true, 
                publicationId: parseInt(publicationId)
            };
        } else {
            const errorMessage = result.response.split(':')[1] || 'Error al crear publicación';
            return { success: false, message: errorMessage };
        }
        
    } catch (error) {
        console.error(' Error en createPublication:', error);
        return { success: false, message: error.message };
    }
}

async function updatePublication(id, updates) {
    // El backend actual no tiene servicio de actualización
    // Por ahora retornar error
    return { success: false, message: 'Función de actualización no implementada en el backend' };
}

async function deletePublication(id) {
    try {
        if (!wsManager.isConnected) {
            await wsManager.connect();
        }
        
        const currentUser = SkillTradeAuth.getCurrentUser();
        if (!currentUser) {
            return { success: false, message: 'Usuario no autenticado' };
        }
        
        // Formato PBDEL: "usuario_id;publicacion_id"
        const payload = `${currentUser.id};${id}`;
        const result = await wsManager.sendMessage('PBDEL', payload);
        
        if (result.response.startsWith('OK')) {
            return { success: true };
        } else {
            const errorMessage = result.response.split(':')[1] || 'Error al eliminar publicación';
            return { success: false, message: errorMessage };
        }
        
    } catch (error) {
        console.error(' Error en deletePublication:', error);
        return { success: false, message: error.message };
    }
}

function validatePublication(data) {
    const errors = [];
    
    if (!data.title || data.title.trim().length < 3) {
        errors.push('El título debe tener al menos 3 caracteres');
    }
    
    if (!data.description || data.description.trim().length < 10) {
        errors.push('La descripción debe tener al menos 10 caracteres');
    }
    
    if (!data.skillOffered || data.skillOffered.trim().length < 3) {
        errors.push('Debes especificar qué habilidad ofreces');
    }
    
    if (!data.skillWanted || data.skillWanted.trim().length < 3) {
        errors.push('Debes especificar qué habilidad buscas');
    }
    
    if (!data.category) {
        errors.push('Debes seleccionar una categoría');
    }
    
    return {
        valid: errors.length === 0,
        errors
    };
}

function incrementViews(publicationId) {
    // Por ahora solo simular, en el futuro implementar en backend
    console.log(' Vista incrementada para publicación:', publicationId);
}

// ===== FUNCIÓN DE ESTADÍSTICAS (NUEVA) =====
async function getPublicationStats() {
    try {
        const currentUser = SkillTradeAuth.getCurrentUser();
        if (!currentUser) {
            return {
                totalPublications: 0,
                totalViews: 0,
                totalInterests: 0,
                averageViews: 0
            };
        }
        
        // Obtener publicaciones del usuario
        const userPubs = await getUserPublications(currentUser.id);
        
        // Calcular estadísticas
        const totalPublications = userPubs.length;
        const totalViews = userPubs.reduce((sum, pub) => sum + (pub.views || 0), 0);
        const totalInterests = userPubs.reduce((sum, pub) => sum + (pub.interests || 0), 0);
        const averageViews = totalPublications > 0 ? Math.round(totalViews / totalPublications) : 0;
        
        return {
            totalPublications,
            totalViews,
            totalInterests,
            averageViews
        };
        
    } catch (error) {
        console.error(' Error en getPublicationStats:', error);
        return {
            totalPublications: 0,
            totalViews: 0,
            totalInterests: 0,
            averageViews: 0
        };
    }
}

// ===== FUNCIONES DE INTERESES (TEMPORAL - localStorage) =====
function getInterests() {
    try {
        const interests = localStorage.getItem(INTERESTS_KEY);
        return interests ? JSON.parse(interests) : {};
    } catch (error) {
        console.error('Error al cargar intereses:', error);
        return {};
    }
}

function toggleInterest(publicationId) {
    try {
        const currentUser = SkillTradeAuth.getCurrentUser();
        if (!currentUser) {
            throw new Error('Usuario no autenticado');
        }
        
        const interests = getInterests();
        const userInterests = interests[currentUser.id] || [];
        const isInterested = userInterests.includes(parseInt(publicationId));
        
        if (isInterested) {
            interests[currentUser.id] = userInterests.filter(id => id !== parseInt(publicationId));
        } else {
            interests[currentUser.id] = [...userInterests, parseInt(publicationId)];
        }
        
        localStorage.setItem(INTERESTS_KEY, JSON.stringify(interests));
        
        return { 
            success: true, 
            interested: !isInterested, 
            totalInterests: 0
        };
    } catch (error) {
        return { success: false, message: error.message };
    }
}

function isUserInterested(publicationId) {
    const currentUser = SkillTradeAuth.getCurrentUser();
    if (!currentUser) return false;
    
    const interests = getInterests();
    const userInterests = interests[currentUser.id] || [];
    return userInterests.includes(parseInt(publicationId));
}

// ===== UTILIDADES =====
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Hace 1 día';
    if (diffDays < 7) return `Hace ${diffDays} días`;
    if (diffDays < 30) return `Hace ${Math.ceil(diffDays / 7)} semanas`;
    if (diffDays < 365) return `Hace ${Math.ceil(diffDays / 30)} meses`;
    return `Hace ${Math.ceil(diffDays / 365)} años`;
}

function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.abs(now - date) / (1000 * 60 * 60);
    
    if (diffInHours < 1) return 'Hace unos minutos';
    if (diffInHours < 24) return `Hace ${Math.round(diffInHours)} horas`;
    return formatDate(dateString);
}

// ===== FUNCIÓN DE ESTADO DE BACKEND (NUEVA) =====
function showBackendConnectionStatus(isConnected) {
    // Actualizar el elemento de estado del backend si existe
    const statusElement = document.getElementById('backendStatus');
    if (statusElement) {
        if (isConnected) {
            statusElement.innerHTML = `
                <span style="color: #28a745;"> Backend conectado</span><br>
                <small>WebSocket activo en ${WS_URL}</small>
            `;
        } else {
            statusElement.innerHTML = `
                <span style="color: #dc3545;"> Backend desconectado</span><br>
                <small>Verificar docker-compose</small>
            `;
        }
    }
}

// ===== INICIALIZACIÓN =====
document.addEventListener('DOMContentLoaded', function() {
    console.log(' SkillTrade API inicializando conexión al backend...');
    
    // Conectar automáticamente al cargar la página
    wsManager.connect()
        .then(() => {
            console.log(' Conexión al backend establecida');
            // Mostrar indicador de conexión exitosa
            showBackendConnectionStatus(true);
        })
        .catch((error) => {
            console.error(' Error al conectar con backend:', error);
            showBackendConnectionStatus(false);
        });
});

// ===== EXPORTAR FUNCIONES PARA USO GLOBAL =====
window.SkillTradeAPI = {
    // WebSocket Manager
    wsManager,
    
    // Usuarios
    registerUser,
    loginUser,
    getUserById,
    updateUser,
    
    // Publicaciones
    getAllPublications,
    getUserPublications,
    searchPublications,
    getPublicationById,
    createPublication,
    updatePublication,
    deletePublication,
    validatePublication,
    incrementViews,
    
    // Estadísticas
    getPublicationStats,
    
    // Intereses (temporal)
    toggleInterest,
    isUserInterested,
    
    // Utilidades
    formatDate,
    formatRelativeTime,
    
    // Constantes
    CATEGORIES,
    
    // Configuración
    WS_URL
};