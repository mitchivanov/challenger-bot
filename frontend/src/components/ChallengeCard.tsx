import { useState } from 'react';
import type { Challenge } from '../types';
import EventsModal from './EventsModal';
import { useChallenges } from '../hooks/useApi';

interface ChallengeCardProps {
    challenge: Challenge;
    onDelete: (id: number) => void;
}

const ChallengeCard = ({ challenge, onDelete }: ChallengeCardProps) => {
    const [isEventsModalOpen, setIsEventsModalOpen] = useState(false);
    const { deleteChallenge } = useChallenges();

    const handleDelete = async () => {
        try {
            await deleteChallenge(challenge.id);
            onDelete(challenge.id);
        } catch (error) {
            console.error('Ошибка при удалении челленджа:', error);
        }
    };

    return (
        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-semibold">{challenge.title}</h3>
                <button
                    onClick={handleDelete}
                    className="text-red-500 hover:text-red-700"
                >
                    ✕
                </button>
            </div>
            <p className="text-gray-600 mb-4">{challenge.description}</p>
            <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                <div>
                    <span className="text-gray-500">Начало:</span>{' '}
                    {new Date(challenge.start_date).toLocaleDateString()}
                </div>
                <div>
                    <span className="text-gray-500">Конец:</span>{' '}
                    {new Date(challenge.end_date).toLocaleDateString()}
                </div>
            </div>
            <div className="flex justify-end space-x-2">
                <button
                    onClick={() => setIsEventsModalOpen(true)}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
                >
                    Мероприятия
                </button>
            </div>

            <EventsModal
                isOpen={isEventsModalOpen}
                onClose={() => setIsEventsModalOpen(false)}
                challengeId={challenge.id}
            />
        </div>
    );
};

export default ChallengeCard; 