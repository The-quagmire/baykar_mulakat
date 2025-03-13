// static/baykar/js/api_client.js

// CSRF Token alma
function getCsrfToken() {
    // Form içindeki CSRF token'ı kontrol et
    const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (tokenInput) return tokenInput.value;

    // Django'nun cookie'den CSRF token'ı alınması
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') return value;
    }

    // Hiçbir yerden bulunamadıysa
    console.warn('CSRF token bulunamadı!');
    return '';
}

// Temel API çağrı fonksiyonu
async function apiCall(endpoint, method = 'GET', data = null) {
    const headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
    };

    const options = {
        method,
        headers,
        credentials: 'same-origin'
    };

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(endpoint.startsWith('/') ? endpoint : `/api/v1/${endpoint}`, options);

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `API hatası: ${response.status}`);
    }

    return response.json();
}

// Takım API fonksiyonları
const TeamApi = {
    getAll: () => apiCall('teams/'),
    getDetail: (id) => apiCall(`teams/${id}/`)
};

// Personel API fonksiyonları
const PersonnelApi = {
    getAll: () => apiCall('personnel/'),
    getDetail: (id) => apiCall(`personnel/${id}/`)
};

// Parça API fonksiyonları
const PartApi = {
    getAll: (filters = {}) => {
        let queryParams = new URLSearchParams(filters).toString();
        return apiCall(`parts/?${queryParams}`);
    },
    getDetail: (id) => apiCall(`parts/${id}/`),
    create: (data) => apiCall('parts/', 'POST', data),
    update: (id, data) => apiCall(`parts/${id}/`, 'PUT', data),
    delete: (id) => apiCall(`parts/${id}/`, 'DELETE'),
    recycle: (id) => apiCall(`parts/${id}/`, 'DELETE')
};

// Uçak API fonksiyonları
const AircraftApi = {
    getAll: (filters = {}) => {
        let queryParams = new URLSearchParams(filters).toString();
        return apiCall(`aircraft/?${queryParams}`);
    },
    getDetail: (id) => apiCall(`aircraft/${id}/`),
    create: (data) => apiCall('aircraft/', 'POST', data),
    update: (id, data) => apiCall(`aircraft/${id}/`, 'PUT', data),
    delete: (id) => apiCall(`aircraft/${id}/`, 'DELETE')
};

// Uyumlu parçaları getiren API fonksiyonu
const getCompatibleParts = (aircraftType) => {
    return apiCall(`compatible-parts/?aircraft_type=${aircraftType}`);
};


