// ===== LÓGICA ESPECÍFICA PARA PUBLICACIONES.HTML =====

// ===== VARIABLES GLOBALES =====
let currentPage = 1;
const itemsPerPage = 6;
let currentPublications = [];
let editingPublicationId = null;

// ===== INICIALIZACIÓN =====
document.addEventListener('DOMContentLoaded', function() {
    initializePublicationsPage();
});

function initializePublicationsPage() {
    setupUIElements();
    setupEventListeners();
    loadAndDisplayPublications();
    setupModalCloseEvents();
    
    // Manejar parámetros de URL del dashboard
    handleURLParameters();
}

function handleURLParameters() {
    const urlParams = new URLSearchParams(window.location.search);
    const editId = urlParams.get('edit');
    const viewId = urlParams.get('view');
    
    if (editId) {
        // Abrir modal de editar publicación
        setTimeout(() => {
            editPublication(parseInt(editId));
        }, 1000);
    } else if (viewId) {
        // Mostrar detalles de publicación
        setTimeout(() => {
            showPublicationDetails(parseInt(viewId));
        }, 1000);
    }
}

function setupUIElements() {
    // Mostrar botón de crear publicación solo si está autenticado
    const createBtn = document.getElementById('createPublicationBtn');
    if (SkillTradeAuth.isAuthenticated()) {
        createBtn.style.display = 'flex';
    }

    // Llenar select de categorías
    populateCategorySelects();
}

function populateCategorySelects() {
    const categoryFilter = document.getElementById('categoryFilter');
    const pubCategory = document.getElementById('pubCategory');
    
    // Llenar filtro de categorías
    categoryFilter.innerHTML = '';
    SkillTradeAPI.CATEGORIES.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat.value;
        option.textContent = cat.label;
        categoryFilter.appendChild(option);
    });

    // Llenar select del modal (sin la opción "Todas")
    if (pubCategory) {
        pubCategory.innerHTML = '<option value="">Selecciona una categoría</option>';
        SkillTradeAPI.CATEGORIES.slice(1).forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.value;
            option.textContent = cat.label;
            pubCategory.appendChild(option);
        });
    }
}

function setupEventListeners() {
    // Búsqueda en tiempo real con debounce
    let searchTimeout;
    document.getElementById('searchInput').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentPage = 1;
            loadAndDisplayPublications();
        }, 300);
    });

    // Filtros
    document.getElementById('categoryFilter').addEventListener('change', () => {
        currentPage = 1;
        loadAndDisplayPublications();
    });

    document.getElementById('sortFilter').addEventListener('change', () => {
        currentPage = 1;
        loadAndDisplayPublications();
    });

    // Botón crear publicación
    const createBtn = document.getElementById('createPublicationBtn');
    if (createBtn) {
        createBtn.addEventListener('click', openCreatePublicationModal);
    }

    // Formulario de publicación
    const pubForm = document.getElementById('publicationForm');
    if (pubForm) {
        pubForm.addEventListener('submit', handlePublicationSubmit);
    }

    // Paginación
    document.getElementById('prevPage').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            loadAndDisplayPublications();
        }
    });

    document.getElementById('nextPage').addEventListener('click', () => {
        const totalPages = Math.ceil(currentPublications.length / itemsPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            loadAndDisplayPublications();
        }
    });
}

function setupModalCloseEvents() {
    const closeButtons = document.querySelectorAll('.modal-close');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const modalId = btn.getAttribute('data-modal');
            SkillTradeAuth.closeModal(modalId);
        });
    });
}

// ===== CARGA Y VISUALIZACIÓN DE PUBLICACIONES =====
async function loadAndDisplayPublications() {
    const searchQuery = document.getElementById('searchInput').value;
    const categoryFilter = document.getElementById('categoryFilter').value;
    const sortFilter = document.getElementById('sortFilter').value;

    try {
        // Mostrar loading
        SkillTradeAuth.showLoading('Cargando publicaciones...');
        
        // Obtener publicaciones filtradas del backend
        currentPublications = await SkillTradeAPI.searchPublications(searchQuery, categoryFilter, sortFilter);
        
        SkillTradeAuth.hideLoading();
        displayPublications();
        updatePagination();
        
    } catch (error) {
        console.error('Error al cargar publicaciones:', error);
        SkillTradeAuth.hideLoading();
        SkillTradeAuth.showError(null, 'Error al cargar las publicaciones');
        currentPublications = [];
        displayPublications();
    }
}

function displayPublications() {
    const grid = document.getElementById('publicationsGrid');
    const emptyState = document.getElementById('emptyState');
    
    // Calcular publicaciones para la página actual
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const publicationsToShow = currentPublications.slice(startIndex, endIndex);

    if (publicationsToShow.length === 0) {
        grid.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }

    grid.style.display = 'grid';
    emptyState.style.display = 'none';

    grid.innerHTML = publicationsToShow.map(pub => createPublicationCard(pub)).join('');

    // Agregar event listeners a las tarjetas
    setupCardEventListeners();
}

function createPublicationCard(publication) {
    const isInterested = SkillTradeAPI.isUserInterested(publication.id);
    const currentUser = SkillTradeAuth.getCurrentUser();
    const isOwner = currentUser && currentUser.id === publication.userId;
    const userInitials = publication.userName.split(' ').map(n => n[0]).join('').toUpperCase();

    return `
        <div class="publication-card" data-id="${publication.id}">
            <div class="publication-header">
                <div class="user-avatar-small">${userInitials}</div>
                <div class="publication-meta">
                    <h3>${publication.userName}</h3>
                    <div class="date">${SkillTradeAPI.formatRelativeTime(publication.createdAt)}</div>
                </div>
            </div>
            
            <div class="publication-content">
                <h4>${publication.title}</h4>
                <p>${publication.description.length > 120 ? 
                    publication.description.substring(0, 120) + '...' : 
                    publication.description}</p>
                
                <div class="publication-tags">
                    ${publication.tags.map(tag => `<span class="tag">#${tag}</span>`).join('')}
                </div>
            </div>
            
            <div class="publication-actions">
                <div class="publication-stats">
                    <span><i class="fas fa-eye"></i> ${publication.views}</span>
                    <span><i class="fas fa-heart"></i> ${publication.interests}</span>
                </div>
                
                <div class="action-buttons-card">
                    <button class="btn-action view-details" data-id="${publication.id}">
                        <i class="fas fa-eye"></i> Ver
                    </button>
                    ${currentUser ? `
                        <button class="btn-action ${isInterested ? 'interested' : ''}" 
                                onclick="toggleInterest(${publication.id})" 
                                data-id="${publication.id}">
                            <i class="fas fa-heart"></i> 
                            ${isInterested ? 'Interesado' : 'Me interesa'}
                        </button>
                        ${isOwner ? `
                            <button class="btn-action edit-pub" data-id="${publication.id}">
                                <i class="fas fa-edit"></i> Editar
                            </button>
                            <button class="btn-action delete-pub" data-id="${publication.id}">
                                <i class="fas fa-trash"></i> Eliminar
                            </button>
                        ` : ''}
                    ` : `
                        <button class="btn-action" onclick="SkillTradeAuth.openModal('loginModal')">
                            <i class="fas fa-sign-in-alt"></i> Inicia sesión
                        </button>
                    `}
                </div>
            </div>
        </div>
    `;
}

function setupCardEventListeners() {
    // Ver detalles
    document.querySelectorAll('.view-details').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = parseInt(btn.dataset.id);
            showPublicationDetails(id);
        });
    });

    // Editar publicación
    document.querySelectorAll('.edit-pub').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = parseInt(btn.dataset.id);
            editPublication(id);
        });
    });

    // Eliminar publicación
    document.querySelectorAll('.delete-pub').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = parseInt(btn.dataset.id);
            deletePublication(id);
        });
    });

    // Click en tarjeta para ver detalles
    document.querySelectorAll('.publication-card').forEach(card => {
        card.addEventListener('click', () => {
            const id = parseInt(card.dataset.id);
            showPublicationDetails(id);
        });
    });
}

// ===== MANEJO DE INTERESES =====
async function toggleInterest(publicationId) {
    if (!SkillTradeAuth.isAuthenticated()) {
        SkillTradeAuth.openModal('loginModal');
        return;
    }

    try {
        const result = SkillTradeAPI.toggleInterest(publicationId);
        
        if (result.success) {
            // Actualizar UI
            const btn = document.querySelector(`button[data-id="${publicationId}"]`);
            if (btn && btn.classList.contains('btn-action')) {
                if (result.interested) {
                    btn.classList.add('interested');
                    btn.innerHTML = '<i class="fas fa-heart"></i> Interesado';
                } else {
                    btn.classList.remove('interested');
                    btn.innerHTML = '<i class="fas fa-heart"></i> Me interesa';
                }
            }
            
            SkillTradeAuth.showSuccessMessage(
                result.interested ? '¡Interés agregado!' : 'Interés removido'
            );
        } else {
            SkillTradeAuth.showError(null, result.message);
        }
    } catch (error) {
        console.error('Error al toggle interest:', error);
        SkillTradeAuth.showError(null, 'Error al procesar tu interés');
    }
}

// ===== PAGINACIÓN =====
function updatePagination() {
    const totalPages = Math.ceil(currentPublications.length / itemsPerPage);
    const pagination = document.getElementById('pagination');
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');
    const pageNumbers = document.getElementById('pageNumbers');

    if (totalPages <= 1) {
        pagination.style.display = 'none';
        return;
    }

    pagination.style.display = 'flex';
    
    // Botones anterior/siguiente
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages;

    // Números de página
    pageNumbers.innerHTML = '';
    for (let i = 1; i <= totalPages; i++) {
        const btn = document.createElement('button');
        btn.textContent = i;
        btn.classList.toggle('active', i === currentPage);
        btn.addEventListener('click', () => {
            currentPage = i;
            loadAndDisplayPublications();
        });
        pageNumbers.appendChild(btn);
    }
}

// ===== MODALES =====
function openCreatePublicationModal() {
    if (!SkillTradeAuth.isAuthenticated()) {
        SkillTradeAuth.openModal('loginModal');
        return;
    }

    editingPublicationId = null;
    document.getElementById('modalTitle').textContent = 'Nueva Publicación';
    document.getElementById('submitBtnText').textContent = 'Publicar';
    document.getElementById('publicationForm').reset();
    SkillTradeAuth.openModal('publicationModal');
}

async function editPublication(id) {
    try {
        const publication = await SkillTradeAPI.getPublicationById(id);
        if (!publication) {
            SkillTradeAuth.showError(null, 'Publicación no encontrada');
            return;
        }

        editingPublicationId = id;
        document.getElementById('modalTitle').textContent = 'Editar Publicación';
        document.getElementById('submitBtnText').textContent = 'Actualizar';
        
        // Llenar formulario
        document.getElementById('pubTitle').value = publication.title;
        document.getElementById('pubDescription').value = publication.description;
        document.getElementById('pubSkillOffered').value = publication.skillOffered;
        document.getElementById('pubSkillWanted').value = publication.skillWanted;
        document.getElementById('pubCategory').value = publication.category;
        document.getElementById('pubTags').value = publication.tags.join(', ');
        
        SkillTradeAuth.openModal('publicationModal');
    } catch (error) {
        console.error('Error al cargar publicación para editar:', error);
        SkillTradeAuth.showError(null, 'Error al cargar la publicación');
    }
}

async function deletePublication(id) {
    if (confirm('¿Estás seguro de que quieres eliminar esta publicación?')) {
        try {
            SkillTradeAuth.showLoading('Eliminando publicación...');
            
            const result = await SkillTradeAPI.deletePublication(id);
            
            SkillTradeAuth.hideLoading();
            
            if (result.success) {
                SkillTradeAuth.showSuccessMessage('Publicación eliminada correctamente');
                loadAndDisplayPublications();
            } else {
                SkillTradeAuth.showError(null, result.message);
            }
        } catch (error) {
            SkillTradeAuth.hideLoading();
            console.error('Error al eliminar publicación:', error);
            SkillTradeAuth.showError(null, 'Error al eliminar la publicación');
        }
    }
}

async function showPublicationDetails(id) {
    try {
        const publication = await SkillTradeAPI.getPublicationById(id);
        if (!publication) {
            SkillTradeAuth.showError(null, 'Publicación no encontrada');
            return;
        }

        // Incrementar vistas
        SkillTradeAPI.incrementViews(id);

        const currentUser = SkillTradeAuth.getCurrentUser();
        const isInterested = SkillTradeAPI.isUserInterested(id);
        const userInitials = publication.userName.split(' ').map(n => n[0]).join('').toUpperCase();

        document.getElementById('detailTitle').textContent = publication.title;
        document.getElementById('detailContent').innerHTML = `
            <div class="publication-detail">
                <div class="detail-header">
                    <div class="user-avatar-small">${userInitials}</div>
                    <div>
                        <h3>${publication.userName}</h3>
                        <p class="detail-date">${SkillTradeAPI.formatRelativeTime(publication.createdAt)}</p>
                    </div>
                </div>
                
                <div class="detail-content">
                    <h4>Descripción</h4>
                    <p class="detail-description">${publication.description}</p>
                    
                    <div class="detail-skills">
                        <div class="skill-box offered">
                            <h5><i class="fas fa-gift"></i> Ofrece</h5>
                            <p>${publication.skillOffered}</p>
                        </div>
                        <div class="skill-box wanted">
                            <h5><i class="fas fa-search"></i> Busca</h5>
                            <p>${publication.skillWanted}</p>
                        </div>
                    </div>
                    
                    <div class="detail-tags">
                        <h5>Etiquetas</h5>
                        <div class="tags-container">
                            ${publication.tags.map(tag => `<span class="tag">#${tag}</span>`).join('')}
                        </div>
                    </div>
                    
                    <div class="detail-stats">
                        <span><i class="fas fa-eye"></i> ${publication.views} vistas</span>
                        <span><i class="fas fa-heart"></i> ${publication.interests} interesados</span>
                        <span><i class="fas fa-tag"></i> ${publication.category}</span>
                    </div>
                    
                    ${currentUser && currentUser.id !== publication.userId ? `
                        <div class="detail-actions">
                            <button class="btn btn-primary" onclick="toggleInterest(${publication.id}); SkillTradeAuth.closeModal('detailModal');">
                                <i class="fas fa-heart"></i> 
                                ${isInterested ? 'Ya no me interesa' : 'Me interesa este intercambio'}
                            </button>
                            <button class="btn btn-secondary" onclick="contactUser('${publication.userEmail}')">
                                <i class="fas fa-envelope"></i> Contactar
                            </button>
                        </div>
                    ` : currentUser ? `
                        <div class="detail-actions">
                            <button class="btn btn-secondary" onclick="SkillTradeAuth.closeModal('detailModal'); editPublication(${publication.id});">
                                <i class="fas fa-edit"></i> Editar
                            </button>
                            <button class="btn btn-logout" onclick="SkillTradeAuth.closeModal('detailModal'); deletePublication(${publication.id});">
                                <i class="fas fa-trash"></i> Eliminar
                            </button>
                        </div>
                    ` : `
                        <div class="detail-actions">
                            <button class="btn btn-primary" onclick="SkillTradeAuth.closeModal('detailModal'); SkillTradeAuth.openModal('loginModal');">
                                <i class="fas fa-sign-in-alt"></i> Inicia sesión para interactuar
                            </button>
                        </div>
                    `}
                </div>
            </div>
        `;

        SkillTradeAuth.openModal('detailModal');
    } catch (error) {
        console.error('Error al mostrar detalles:', error);
        SkillTradeAuth.showError(null, 'Error al cargar los detalles de la publicación');
    }
}

function contactUser(email) {
    const subject = encodeURIComponent('Interés en tu publicación de SkillTrade');
    const body = encodeURIComponent('Hola, me interesa tu publicación en SkillTrade. Me gustaría conversar sobre un posible intercambio de habilidades.');
    window.location.href = `mailto:${email}?subject=${subject}&body=${body}`;
}

// ===== MANEJO DEL FORMULARIO =====
async function handlePublicationSubmit(e) {
    e.preventDefault();
    
    const formData = {
        title: document.getElementById('pubTitle').value.trim(),
        description: document.getElementById('pubDescription').value.trim(),
        skillOffered: document.getElementById('pubSkillOffered').value.trim(),
        skillWanted: document.getElementById('pubSkillWanted').value.trim(),
        category: document.getElementById('pubCategory').value,
        tags: document.getElementById('pubTags').value.split(',').map(tag => tag.trim()).filter(tag => tag)
    };

    const errorDiv = document.getElementById('publicationError');
    const submitBtn = e.target.querySelector('button[type="submit"]');
    
    // Validación
    const validation = SkillTradeAPI.validatePublication(formData);
    if (!validation.valid) {
        SkillTradeAuth.showError(errorDiv, validation.errors.join('\n'));
        return;
    }

    try {
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
        submitBtn.disabled = true;

        let result;
        if (editingPublicationId) {
            result = await SkillTradeAPI.updatePublication(editingPublicationId, formData);
        } else {
            result = await SkillTradeAPI.createPublication(formData);
        }

        if (result.success) {
            SkillTradeAuth.closeModal('publicationModal');
            SkillTradeAuth.showSuccessMessage(
                editingPublicationId ? 'Publicación actualizada' : 'Publicación creada'
            );
            loadAndDisplayPublications();
        } else {
            SkillTradeAuth.showError(errorDiv, result.message);
        }

        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;

    } catch (error) {
        console.error('Error al enviar formulario:', error);
        SkillTradeAuth.showError(errorDiv, 'Error inesperado. Inténtalo nuevamente.');
        submitBtn.innerHTML = '<i class="fas fa-save"></i> <span id="submitBtnText">Publicar</span>';
        submitBtn.disabled = false;
    }
}

// ===== FUNCIONES GLOBALES EXPUESTAS =====
window.toggleInterest = toggleInterest;
window.editPublication = editPublication;
window.deletePublication = deletePublication;
window.contactUser = contactUser;