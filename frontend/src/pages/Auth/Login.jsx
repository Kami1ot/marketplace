// src/pages/Auth/Login.jsx
import { useState } from 'react';
import { Card, Form, Input, Button, Typography, Alert, Row, Col, message } from 'antd';
import { UserOutlined, LockOutlined, LoginOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../../services/authService';

const { Title, Text } = Typography;

const Login = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const onFinish = async (values) => {
    setLoading(true);
    setError(null);

    try {
      const result = await authService.login({
        email: values.username, // В форме поле называется username для совместимости с Ant Design
        password: values.password
      });

      message.success('Успешная авторизация!');
      console.log('Авторизован пользователь:', result.user);
      
      // Перенаправляем на главную страницу
      navigate('/');
      
      // Перезагружаем страницу для обновления состояния навигации
      window.location.reload();
      
    } catch (error) {
      console.error('Ошибка авторизации:', error);
      setError(error.detail || 'Ошибка авторизации. Проверьте данные.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center',
      background: '#f0f2f5',
      padding: '20px'
    }}>
      <Row justify="center" style={{ width: '100%' }}>
        <Col xs={24} sm={16} md={12} lg={8} xl={6}>
          <Card style={{ padding: '24px' }}>
            <div style={{ textAlign: 'center', marginBottom: '32px' }}>
              <Title level={2} style={{ color: '#1890ff', marginBottom: '8px' }}>
                🛒 Вход в Маркетплейс
              </Title>
              <Text type="secondary">
                Войдите в свой аккаунт для продолжения
              </Text>
            </div>

            {error && (
              <Alert
                message="Ошибка авторизации"
                description={error}
                type="error"
                showIcon
                style={{ marginBottom: '24px' }}
                closable
                onClose={() => setError(null)}
              />
            )}

            <Form
              form={form}
              name="login"
              onFinish={onFinish}
              autoComplete="off"
              size="large"
              layout="vertical"
            >
              <Form.Item
                name="username"
                label="Email"
                rules={[
                  { required: true, message: 'Введите email!' },
                  { type: 'email', message: 'Введите корректный email!' }
                ]}
              >
                <Input 
                  prefix={<UserOutlined />} 
                  placeholder="your@email.com"
                  autoComplete="username"
                />
              </Form.Item>

              <Form.Item
                name="password"
                label="Пароль"
                rules={[{ required: true, message: 'Введите пароль!' }]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="Ваш пароль"
                  autoComplete="current-password"
                />
              </Form.Item>

              <Form.Item style={{ marginBottom: '16px' }}>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  block 
                  icon={<LoginOutlined />}
                  loading={loading}
                >
                  {loading ? 'Вход...' : 'Войти'}
                </Button>
              </Form.Item>
            </Form>

            <div style={{ textAlign: 'center' }}>
              <Text type="secondary">
                Нет аккаунта? <Link to="/register" style={{ color: '#1890ff' }}>Зарегистрироваться</Link>
              </Text>
            </div>

            {/* Демо данные для тестирования */}
            <div style={{ 
              marginTop: '24px', 
              padding: '16px', 
              background: '#f9f9f9', 
              borderRadius: '6px' 
            }}>
              <Text strong>Для тестирования:</Text><br/>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                Admin: admin@marketplace.com / admin123<br/>
                Business: business@test.com / password<br/>
                User: user@test.com / password
              </Text>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Login;