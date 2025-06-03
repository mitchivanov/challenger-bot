import { useEffect, useState } from 'react';
import { Modal, Button, Table, Form, Input, DatePicker, InputNumber, message, Popconfirm, Space } from 'antd';
import type { Event } from '../types';
import { useChallenges } from '../hooks/useApi';
import dayjs from 'dayjs';

interface EventsModalProps {
    isOpen: boolean;
    onClose: () => void;
    challengeId: number;
}

const EventsModal = ({ isOpen, onClose, challengeId }: EventsModalProps) => {
    const [events, setEvents] = useState<Event[]>([]);
    const { getChallengeEvents, createEvent, loading, error, deleteEvent, updateEvent } = useChallenges();
    const [isCreateVisible, setIsCreateVisible] = useState(false);
    const [isEditVisible, setIsEditVisible] = useState(false);
    const [form] = Form.useForm();
    const [editForm] = Form.useForm();
    const [submitting, setSubmitting] = useState(false);
    const [editingEvent, setEditingEvent] = useState<Event | null>(null);

    useEffect(() => {
        if (isOpen && challengeId) {
            fetchEvents();
        }
    }, [isOpen, challengeId]);

    useEffect(() => {
        if (!isOpen) {
            setIsCreateVisible(false);
            setIsEditVisible(false);
            setEditingEvent(null);
            form.resetFields();
            editForm.resetFields();
        }
    }, [isOpen, form, editForm]);

    const fetchEvents = async () => {
        try {
            const data = await getChallengeEvents(challengeId);
            setEvents(data);
        } catch (err) {
            setEvents([]);
        }
    };

    const handleSubmit = async (values: any) => {
        setSubmitting(true);
        try {
            await createEvent({
                ...values,
                challenge_id: challengeId,
                date: values.date.format('YYYY-MM-DD')
            });
            message.success('Мероприятие создано');
            form.resetFields();
            setIsCreateVisible(false);
            await fetchEvents();
        } catch (err) {
            message.error('Ошибка при создании мероприятия');
        } finally {
            setSubmitting(false);
        }
    };

    const handleEdit = (event: Event) => {
        setEditingEvent(event);
        editForm.setFieldsValue({
            ...event,
            date: event.date ? dayjs(event.date) : null,
        });
        setIsEditVisible(true);
    };

    const handleUpdate = async (values: any) => {
        if (!editingEvent) return;
        setSubmitting(true);
        try {
            await updateEvent(editingEvent.id, {
                ...values,
                date: values.date.format('YYYY-MM-DD'),
            });
            message.success('Мероприятие обновлено');
            setIsEditVisible(false);
            setEditingEvent(null);
            editForm.resetFields();
            await fetchEvents();
        } catch (err) {
            message.error('Ошибка при обновлении мероприятия');
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (eventId: number) => {
        try {
            await deleteEvent(eventId);
            message.success('Мероприятие удалено');
            await fetchEvents();
        } catch (err) {
            message.error('Ошибка при удалении мероприятия');
        }
    };

    const handleCreateCancel = () => {
        setIsCreateVisible(false);
        form.resetFields();
    };

    const handleEditCancel = () => {
        setIsEditVisible(false);
        setEditingEvent(null);
        editForm.resetFields();
    };

    const columns = [
        { title: 'Название', dataIndex: 'title', key: 'title' },
        { title: 'Описание', dataIndex: 'description', key: 'description' },
        { title: 'Дата', dataIndex: 'date', key: 'date' },
        { title: 'Баллы за отчет', dataIndex: 'points_per_report', key: 'points_per_report' },
        { title: 'Кол-во фото', dataIndex: 'required_photos', key: 'required_photos' },
        {
            title: 'Действия',
            key: 'actions',
            render: (_: any, record: Event) => (
                <Space>
                    <Button type="link" onClick={() => handleEdit(record)}>Редактировать</Button>
                    <Popconfirm
                        title="Удалить мероприятие?"
                        onConfirm={() => handleDelete(record.id)}
                        okText="Да"
                        cancelText="Нет"
                    >
                        <Button type="link" danger>Удалить</Button>
                    </Popconfirm>
                </Space>
            )
        }
    ];

    return (
        <Modal
            title="Мероприятия"
            open={isOpen}
            onCancel={onClose}
            footer={null}
            width={800}
        >
            {isCreateVisible ? (
                <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleSubmit}
                >
                    <Form.Item
                        name="title"
                        label="Название"
                        rules={[{ required: true, message: 'Введите название' }]}
                    >
                        <Input />
                    </Form.Item>
                    <Form.Item
                        name="description"
                        label="Описание"
                        rules={[{ required: true, message: 'Введите описание' }]}
                    >
                        <Input.TextArea />
                    </Form.Item>
                    <Form.Item
                        name="date"
                        label="Дата"
                        rules={[{ required: true, message: 'Выберите дату' }]}
                    >
                        <DatePicker style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item
                        name="points_per_report"
                        label="Баллы за отчет"
                        rules={[{ required: true, message: 'Введите количество баллов' }]}
                    >
                        <InputNumber min={0} style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item
                        name="required_photos"
                        label="Требуемое количество фото"
                        rules={[{ required: true, message: 'Введите количество фото' }]}
                    >
                        <InputNumber min={0} style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item>
                        <Space>
                            <Button onClick={handleCreateCancel}>Назад</Button>
                            <Button type="primary" htmlType="submit" loading={submitting}>
                                Создать
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            ) : isEditVisible && editingEvent ? (
                <Form
                    form={editForm}
                    layout="vertical"
                    onFinish={handleUpdate}
                    initialValues={{
                        ...editingEvent,
                        date: editingEvent.date ? dayjs(editingEvent.date) : null,
                    }}
                >
                    <Form.Item
                        name="title"
                        label="Название"
                        rules={[{ required: true, message: 'Введите название' }]}
                    >
                        <Input />
                    </Form.Item>
                    <Form.Item
                        name="description"
                        label="Описание"
                        rules={[{ required: true, message: 'Введите описание' }]}
                    >
                        <Input.TextArea />
                    </Form.Item>
                    <Form.Item
                        name="date"
                        label="Дата"
                        rules={[{ required: true, message: 'Выберите дату' }]}
                    >
                        <DatePicker style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item
                        name="points_per_report"
                        label="Баллы за отчет"
                        rules={[{ required: true, message: 'Введите количество баллов' }]}
                    >
                        <InputNumber min={0} style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item
                        name="required_photos"
                        label="Требуемое количество фото"
                        rules={[{ required: true, message: 'Введите количество фото' }]}
                    >
                        <InputNumber min={0} style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item>
                        <Space>
                            <Button onClick={handleEditCancel}>Назад</Button>
                            <Button type="primary" htmlType="submit" loading={submitting}>
                                Сохранить
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            ) : (
                <>
                    <Button 
                        type="primary" 
                        style={{ marginBottom: 16 }} 
                        onClick={() => setIsCreateVisible(true)}
                    >
                        Создать мероприятие
                    </Button>
                    <Table
                        columns={columns}
                        dataSource={events}
                        rowKey="id"
                        loading={loading}
                        locale={{ emptyText: error ? `Ошибка: ${error}` : 'Нет мероприятий' }}
                        pagination={{ pageSize: 5 }}
                    />
                </>
            )}
        </Modal>
    );
};

export default EventsModal; 