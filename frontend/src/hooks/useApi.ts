import { useState } from 'react';
import type { Challenge, Event, Report } from '../types';

const VITE_API_URL = 'https://libertylib.online/api'

export const useChallenges = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleRequest = async <T>(request: () => Promise<T>): Promise<T> => {
        setLoading(true);
        setError(null);
        try {
            const result = await request();
            return result;
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Произошла ошибка');
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const getChallenges = () => handleRequest(async () => {
        const response = await fetch(`${VITE_API_URL}/challenges/`);
        if (!response.ok) throw new Error('Ошибка при получении челленджей');
        return response.json();
    });

    const getChallenge = (id: number) => handleRequest(async () => {
        const response = await fetch(`${VITE_API_URL}/challenges/${id}`);
        if (!response.ok) throw new Error('Ошибка при получении челленджа');
        return response.json();
    });

    const createChallenge = (data: Omit<Challenge, 'id'>) => handleRequest(async () => {
        const response = await fetch(`${VITE_API_URL}/challenges/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Ошибка при создании челленджа');
        return response.json();
    });

    const updateChallenge = (id: number, data: Partial<Challenge>) => handleRequest(async () => {
        const response = await fetch(`${VITE_API_URL}/challenges/${id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Ошибка при обновлении челленджа');
        return response.json();
    });

    const deleteChallenge = (id: number) => handleRequest(async () => {
        const response = await fetch(`${VITE_API_URL}/challenges/${id}`, {
            method: 'DELETE',
        });
        if (!response.ok) throw new Error('Ошибка при удалении челленджа');
    });

    const getChallengeEvents = (challengeId: number) => handleRequest(async () => {
        const response = await fetch(`${VITE_API_URL}/challenges/${challengeId}/events`);
        if (!response.ok) throw new Error('Ошибка при получении мероприятий');
        return response.json();
    });

    const createEvent = async (eventData: {
        challenge_id: number;
        title: string;
        description: string;
        date: string;
        points_per_report: number;
        required_photos: number;
    }) => handleRequest(async () => {
        const response = await fetch(`${VITE_API_URL}/events/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(eventData),
        });
        if (!response.ok) throw new Error('Ошибка при создании мероприятия');
        return response.json();
    });

    const updateEvent = (id: number, data: Partial<Event>) => handleRequest(async () => {
        const response = await fetch(`${VITE_API_URL}/events/${id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Ошибка при обновлении мероприятия');
        return response.json();
    });

    const deleteEvent = (id: number) => handleRequest(async () => {
        const response = await fetch(`${VITE_API_URL}/events/${id}`, {
            method: 'DELETE',
        });
        if (!response.ok) throw new Error('Ошибка при удалении мероприятия');
    });

    const getChallengeReports = (challengeId: number) => handleRequest(async () => {
        const response = await fetch(`${VITE_API_URL}/reports/challenge/${challengeId}`);
        if (!response.ok) throw new Error('Ошибка при получении отчетов');
        return response.json();
    });

    const getUserReports = (userId: number) => handleRequest(async () => {
        const response = await fetch(`${VITE_API_URL}/reports/user/${userId}`);
        if (!response.ok) throw new Error('Ошибка при получении отчетов пользователя');
        return response.json();
    });

    const rejectReport = async (reportId: number) => {
        setLoading(true);
        setError(null);
        try {
            console.log(`Rejecting report ${reportId}...`);
            const response = await fetch(`${VITE_API_URL}/reports/${reportId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rejected: true }),
            });
            
            console.log('Response status:', response.status);
            
            if (!response.ok) {
                const errorData = await response.text();
                console.error('Error response:', errorData);
                throw new Error(`Failed to reject report: ${response.status} ${errorData}`);
            }
            
            const result = await response.json();
            console.log('Report rejected successfully:', result);
            return result;
        } catch (err) {
            console.error('Error in rejectReport:', err);
            setError(err instanceof Error ? err.message : 'An error occurred');
            throw err;
        } finally {
            setLoading(false);
        }
    };

    return {
        loading,
        error,
        getChallenges,
        getChallenge,
        createChallenge,
        updateChallenge,
        deleteChallenge,
        getChallengeEvents,
        createEvent,
        updateEvent,
        deleteEvent,
        getChallengeReports,
        getUserReports,
        rejectReport
    };
}; 