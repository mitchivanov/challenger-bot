import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Typography, Space } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useAuth } from '../hooks/useAuth';

const { Title, Text } = Typography;

interface LoginFormData {
  username: string;
  password: string;
}

const LoginForm: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (values: LoginFormData) => {
    setLoading(true);
    try {
      const success = login(values.username, values.password);
      if (success) {
        message.success('Добро пожаловать!');
      } else {
        message.error('Неверный логин или пароль');
      }
    } catch (error) {
      message.error('Произошла ошибка при входе');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      height: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '20px'
    }}>
      <Card
        style={{
          width: '100%',
          maxWidth: 400,
          borderRadius: 12,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
        }}
        bodyStyle={{ padding: '40px' }}
      >
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center' }}>
            <Title level={2} style={{ margin: 0, color: '#1f2937' }}>
              Вход в систему
            </Title>
            <Text type="secondary" style={{ fontSize: '14px' }}>
              Введите ваши данные для входа
            </Text>
          </div>

          <Form
            form={form}
            layout="vertical"
            onFinish={handleSubmit}
            autoComplete="off"
            size="large"
          >
            <Form.Item
              name="username"
              label="Логин"
              rules={[{ required: true, message: 'Пожалуйста, введите логин!' }]}
            >
              <Input
                prefix={<UserOutlined style={{ color: '#6b7280' }} />}
                placeholder="Введите логин"
                style={{ borderRadius: 8 }}
              />
            </Form.Item>

            <Form.Item
              name="password"
              label="Пароль"
              rules={[{ required: true, message: 'Пожалуйста, введите пароль!' }]}
            >
              <Input.Password
                prefix={<LockOutlined style={{ color: '#6b7280' }} />}
                placeholder="Введите пароль"
                style={{ borderRadius: 8 }}
              />
            </Form.Item>

            <Form.Item style={{ marginBottom: 0 }}>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                style={{
                  width: '100%',
                  height: 48,
                  borderRadius: 8,
                  fontSize: '16px',
                  fontWeight: 500,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  border: 'none'
                }}
              >
                {loading ? 'Вход...' : 'Войти'}
              </Button>
            </Form.Item>
          </Form>
        </Space>
      </Card>
    </div>
  );
};

export default LoginForm; 