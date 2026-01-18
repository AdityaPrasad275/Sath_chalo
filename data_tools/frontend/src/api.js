import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
});

export const getStops = async () => {
    const response = await api.get('/stops');
    return response.data;
};

export const getRoutes = async () => {
    const response = await api.get('/routes');
    return response.data;
};

export const getTrips = async (routeId) => {
    const response = await api.get(`/trips/${routeId}`);
    return response.data;
};

export const getTripStops = async (tripId) => {
    const response = await api.get(`/trips/${tripId}/stops`);
    return response.data;
};

export const getTimetable = async (routeId) => {
    const response = await api.get(`/timetable/${routeId}`);
    return response.data;
};
