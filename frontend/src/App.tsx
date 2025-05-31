import { useState, useEffect } from 'react'
import { Layout, Menu, Button, Table, Modal, Form, Input, DatePicker, InputNumber, Switch, Tabs } from 'antd'
import { PlusOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import './App.css'

const { Header, Content } = Layout
const { TabPane } = Tabs

interface Challenge {
  id: number
  title: string
  description: string
  start_date: string
  end_date: string
  requires_phone: boolean
  points_per_report: number
  required_photos: number
}

interface Event {
  id: number
  challenge_id: number
  title: string
  description: string
  start_date: string
  end_date: string
  requires_phone: boolean
  points_per_report: number
  required_photos: number
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005'

function App() {
  const [challenges, setChallenges] = useState<Challenge[]>([])
  const [events, setEvents] = useState<Event[]>([])
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [isEventModalVisible, setIsEventModalVisible] = useState(false)
  const [form] = Form.useForm()
  const [eventForm] = Form.useForm()
  const [editingChallenge, setEditingChallenge] = useState<Challenge | null>(null)
  const [selectedChallengeId, setSelectedChallengeId] = useState<number | null>(null)

  const fetchChallenges = async () => {
    const response = await fetch(`${API_URL}/challenges/`)
    const data = await response.json()
    setChallenges(data)
  }

  const fetchEvents = async (challengeId: number) => {
    const response = await fetch(`${API_URL}/challenges/${challengeId}/events/`)
    const data = await response.json()
    setEvents(data)
  }

  useEffect(() => {
    fetchChallenges()
  }, [])

  const handleCreateChallenge = async (values: any) => {
    const response = await fetch(`${API_URL}/challenges/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...values,
        start_date: values.start_date.format('YYYY-MM-DD'),
        end_date: values.end_date.format('YYYY-MM-DD')
      })
    })
    if (response.ok) {
      fetchChallenges()
      setIsModalVisible(false)
      form.resetFields()
    }
  }

  const handleUpdateChallenge = async (values: any) => {
    if (!editingChallenge) return
    const response = await fetch(`${API_URL}/challenges/${editingChallenge.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...values,
        start_date: values.start_date.format('YYYY-MM-DD'),
        end_date: values.end_date.format('YYYY-MM-DD')
      })
    })
    if (response.ok) {
      fetchChallenges()
      setIsModalVisible(false)
      setEditingChallenge(null)
      form.resetFields()
    }
  }

  const handleCreateEvent = async (values: any) => {
    if (!selectedChallengeId) return
    const response = await fetch(`${API_URL}/events/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...values,
        challenge_id: selectedChallengeId,
        start_date: values.start_date.format('YYYY-MM-DD'),
        end_date: values.end_date.format('YYYY-MM-DD')
      })
    })
    if (response.ok) {
      fetchEvents(selectedChallengeId)
      setIsEventModalVisible(false)
      eventForm.resetFields()
    }
  }

  const columns = [
    { title: 'Название', dataIndex: 'title', key: 'title' },
    { title: 'Описание', dataIndex: 'description', key: 'description' },
    { title: 'Дата начала', dataIndex: 'start_date', key: 'start_date' },
    { title: 'Дата окончания', dataIndex: 'end_date', key: 'end_date' },
    { title: 'Баллы за отчет', dataIndex: 'points_per_report', key: 'points_per_report' },
    { title: 'Кол-во фото', dataIndex: 'required_photos', key: 'required_photos' },
    {
      title: 'Действия',
      key: 'actions',
      render: (text: string, record: Challenge) => (
        <>
          <Button type="link" onClick={() => {
            setEditingChallenge(record)
            form.setFieldsValue({
              ...record,
              start_date: dayjs(record.start_date),
              end_date: dayjs(record.end_date)
            })
            setIsModalVisible(true)
          }}>
            Редактировать
          </Button>
          <Button type="link" onClick={() => {
            setSelectedChallengeId(record.id)
            fetchEvents(record.id)
          }}>
            Мероприятия
          </Button>
        </>
      )
    }
  ]

  const eventColumns = [
    { title: 'Название', dataIndex: 'title', key: 'title' },
    { title: 'Описание', dataIndex: 'description', key: 'description' },
    { title: 'Дата начала', dataIndex: 'start_date', key: 'start_date' },
    { title: 'Дата окончания', dataIndex: 'end_date', key: 'end_date' },
    { title: 'Баллы за отчет', dataIndex: 'points_per_report', key: 'points_per_report' },
    { title: 'Кол-во фото', dataIndex: 'required_photos', key: 'required_photos' }
  ]

  return (
    <Layout className="layout">
      <Header>
        <div className="logo" />
        <Menu theme="dark" mode="horizontal" defaultSelectedKeys={['1']}>
          <Menu.Item key="1">Челленджи</Menu.Item>
        </Menu>
      </Header>
      <Content style={{ padding: '50px' }}>
        <div className="site-layout-content">
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setEditingChallenge(null)
              setIsModalVisible(true)
              form.resetFields()
            }}
            style={{ marginBottom: 16 }}
          >
            Новый челлендж
          </Button>

          <Tabs type="card">
            <TabPane tab="Челленджи" key="1">
              <Table columns={columns} dataSource={challenges} rowKey="id" />
            </TabPane>
            {selectedChallengeId && (
              <TabPane tab="Мероприятия" key="2">
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => {
                    setIsEventModalVisible(true)
                    eventForm.resetFields()
                  }}
                  style={{ marginBottom: 16 }}
                >
                  Новое мероприятие
                </Button>
                <Table columns={eventColumns} dataSource={events} rowKey="id" />
              </TabPane>
            )}
          </Tabs>
        </div>

        <Modal
          title={editingChallenge ? "Редактировать челлендж" : "Новый челлендж"}
          open={isModalVisible}
          onOk={form.submit}
          onCancel={() => setIsModalVisible(false)}
        >
          <Form
            form={form}
            layout="vertical"
            onFinish={editingChallenge ? handleUpdateChallenge : handleCreateChallenge}
          >
            <Form.Item name="title" label="Название" rules={[{ required: true }]}>
              <Input />
            </Form.Item>
            <Form.Item name="description" label="Описание" rules={[{ required: true }]}>
              <Input.TextArea />
            </Form.Item>
            <Form.Item name="start_date" label="Дата начала" rules={[{ required: true }]}>
              <DatePicker />
            </Form.Item>
            <Form.Item name="end_date" label="Дата окончания" rules={[{ required: true }]}>
              <DatePicker />
            </Form.Item>
            <Form.Item name="requires_phone" label="Требуется телефон" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item name="points_per_report" label="Баллы за отчет" rules={[{ required: true }]}>
              <InputNumber min={0} />
            </Form.Item>
            <Form.Item name="required_photos" label="Количество фото" rules={[{ required: true }]}>
              <InputNumber min={0} />
            </Form.Item>
          </Form>
        </Modal>

        <Modal
          title="Новое мероприятие"
          open={isEventModalVisible}
          onOk={eventForm.submit}
          onCancel={() => setIsEventModalVisible(false)}
        >
          <Form
            form={eventForm}
            layout="vertical"
            onFinish={handleCreateEvent}
          >
            <Form.Item name="title" label="Название" rules={[{ required: true }]}>
              <Input />
            </Form.Item>
            <Form.Item name="description" label="Описание" rules={[{ required: true }]}>
              <Input.TextArea />
            </Form.Item>
            <Form.Item name="start_date" label="Дата начала" rules={[{ required: true }]}>
              <DatePicker />
            </Form.Item>
            <Form.Item name="end_date" label="Дата окончания" rules={[{ required: true }]}>
              <DatePicker />
            </Form.Item>
            <Form.Item name="requires_phone" label="Требуется телефон" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item name="points_per_report" label="Баллы за отчет" rules={[{ required: true }]}>
              <InputNumber min={0} />
            </Form.Item>
            <Form.Item name="required_photos" label="Количество фото" rules={[{ required: true }]}>
              <InputNumber min={0} />
            </Form.Item>
          </Form>
        </Modal>
      </Content>
    </Layout>
  )
}

export default App
