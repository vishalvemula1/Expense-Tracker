import axios from 'axios';

const api = axios.create({
    baseURL: '/', // Proxy handles the rest
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Clear token and maybe redirect to login
            localStorage.removeItem('token');
            // window.location.href = '/login'; // Let the router handle this via context state instead of hard redirect
        }
        return Promise.reject(error);
    }
);

export default api;
