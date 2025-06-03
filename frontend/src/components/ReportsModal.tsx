import { useEffect, useState, useMemo } from 'react';
import { Modal, Table, Image, Typography, Space, Tag, Select, Button, Popconfirm, message } from 'antd';
import { DeleteOutlined } from '@ant-design/icons';
import type { Report, User } from '../types';
import { useChallenges } from '../hooks/useApi';
import dayjs from 'dayjs';

const { Text } = Typography;

interface ReportsModalProps {
    isOpen: boolean;
    onClose: () => void;
    challengeId: number;
}

const ReportsModal = ({ isOpen, onClose, challengeId }: ReportsModalProps) => {
    const [reports, setReports] = useState<Report[]>([]);
    const [selectedUser, setSelectedUser] = useState<number | null>(null);
    const [loadingReports, setLoadingReports] = useState<number[]>([]);
    const { getChallengeReports, loading, error, rejectReport } = useChallenges();

    useEffect(() => {
        if (isOpen && challengeId) {
            fetchReports();
        }
    }, [isOpen, challengeId]);

    const fetchReports = async () => {
        try {
            const data = await getChallengeReports(challengeId);
            setReports(data);
        } catch (err) {
            message.error('Ошибка при загрузке отчетов');
            setReports([]);
        }
    };

    const handleRejectReport = async (reportId: number) => {
        try {
            setLoadingReports(prev => [...prev, reportId]);
            await rejectReport(reportId);
            message.success('Отчет успешно отклонен, баллы сняты');
            await fetchReports(); // Обновляем список отчетов после отклонения
        } catch (err) {
            console.error('Error rejecting report:', err);
            message.error('Ошибка при отклонении отчета');
        } finally {
            setLoadingReports(prev => prev.filter(id => id !== reportId));
        }
    };

    const uniqueUsers = useMemo(() => {
        const users = reports.map(report => report.user);
        return Array.from(new Set(users.map(user => user.id)))
            .map(id => users.find(user => user.id === id))
            .filter((user): user is User => user !== undefined);
    }, [reports]);

    const filteredReports = useMemo(() => {
        if (!selectedUser) return reports;
        return reports.filter(report => report.user.id === selectedUser);
    }, [reports, selectedUser]);

    const columns = [
        {
            title: 'Пользователь',
            dataIndex: 'user',
            key: 'user',
            width: 200,
            minWidth: 200,
            render: (user: User) => (
                <Space>
                    <Text>{user.username || 'Аноним'}</Text>
                    {user.phone_number && <Tag color="blue">{user.phone_number}</Tag>}
                </Space>
            )
        },
        {
            title: 'Текст отчета',
            dataIndex: 'text_content',
            key: 'text_content',
            width: 250,
            minWidth: 250,
            render: (text: string) => (
                <div style={{ 
                    whiteSpace: 'pre-wrap', 
                    wordBreak: 'break-word',
                    maxWidth: 250,
                    overflow: 'hidden'
                }}>
                    {text}
                </div>
            )
        },
        {
            title: 'Фотографии',
            dataIndex: 'photos',
            key: 'photos',
            width: 300,
            minWidth: 300,
            render: (photos: any[]) => (
                <Image.PreviewGroup>
                    <div style={{ 
                        display: 'flex', 
                        flexWrap: 'wrap', 
                        gap: '8px',
                        maxWidth: 300
                    }}>
                        {photos.map((photo, index) => (
                            <Image
                                key={index}
                                width={60}
                                height={60}
                                style={{ objectFit: 'cover' }}
                                src={`${import.meta.env.VITE_API_URL}/uploads/${photo.photo_url}`}
                                alt={`Фото ${index + 1}`}
                            />
                        ))}
                    </div>
                </Image.PreviewGroup>
            )
        },
        {
            title: 'Дата создания',
            dataIndex: 'created_at',
            key: 'created_at',
            width: 150,
            minWidth: 150,
            render: (date: string) => dayjs(date).format('DD.MM.YYYY HH:mm')
        },
        {
            title: 'Статус',
            key: 'status',
            width: 100,
            minWidth: 100,
            render: (_: any, record: Report) => (
                record.rejected ? (
                    <Tag color="red">Отклонен</Tag>
                ) : (
                    <Tag color="green">Принят</Tag>
                )
            )
        },
        {
            title: 'Действия',
            key: 'actions',
            width: 120,
            minWidth: 120,
            render: (_: any, record: Report) => (
                !record.rejected && (
                    <Popconfirm
                        title="Отклонить отчет?"
                        description="Это действие нельзя отменить. Баллы пользователя будут уменьшены."
                        onConfirm={() => handleRejectReport(record.id)}
                        okText="Да"
                        cancelText="Нет"
                    >
                        <Button 
                            danger 
                            icon={<DeleteOutlined />}
                            type="text"
                            loading={loadingReports.includes(record.id)}
                            disabled={loadingReports.includes(record.id)}
                        >
                            Отклонить
                        </Button>
                    </Popconfirm>
                )
            )
        }
    ];

    return (
        <Modal
            title="Отчеты"
            open={isOpen}
            onCancel={onClose}
            footer={null}
            width={1200}
        >
            <Space direction="vertical" style={{ width: '100%', marginBottom: 16 }}>
                <Select
                    style={{ width: 200 }}
                    placeholder="Фильтр по пользователю"
                    allowClear
                    onChange={(value) => setSelectedUser(value)}
                    options={uniqueUsers.map(user => ({
                        value: user.id,
                        label: user.username || 'Аноним'
                    }))}
                />
            </Space>
            <Table
                columns={columns}
                dataSource={filteredReports}
                rowKey="id"
                loading={loading}
                locale={{ emptyText: error ? `Ошибка: ${error}` : 'Нет доступных отчетов' }}
                pagination={{ pageSize: 5 }}
                scroll={{ x: 1120 }}
            />
        </Modal>
    );
};

export default ReportsModal; 