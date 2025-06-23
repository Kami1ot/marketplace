// src/pages/Auth/Login.jsx - Улучшенная версия с правильной разметкой
import { useState } from 'react';
import { Card, Form, Input, Button, Typography, Alert, Row, Col, message, Divider } from 'antd';
import { UserOutlined, LockOutlined, LoginOutlined, ShopOutlined } from '@ant-design/icons';
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
        email: values.username,
        password: values.password
      });

      message.success('Успешная авторизация!');
      console.log('Авторизован пользователь:', result.user);
      
      navigate('/');
      window.location.reload();
      
    } catch (error) {
      console.error('Ошибка авторизации:', error);
      setError(error.detail || 'Ошибка авторизации. Проверьте данные.');
    } finally {
      setLoading(false);
    }
  };

  return (
      <Row justify="center" align="middle" style={{ width: '100%'}}>
        <Col xs={22} sm={16} md={12} lg={10} xl={8}>
          <Card 
            style={{ 
              padding: '32px',
              borderRadius: '16px',
              boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
              border: 'none',
              marginBottom: '200px'
            }}
          >
            {/* Заголовок */}
            <div style={{ textAlign: 'center', marginBottom: '32px' }}>
              <div style={{ 
                fontSize: '36px', 
                marginBottom: '12px',
                background: 'linear-gradient(45deg, #1890ff, #52c41a)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                🛒
              </div>
              <Title level={3} style={{ margin: 0, color: '#262626', fontSize: '20px' }}>
                Вход в Маркетплейс
              </Title>
              <Text type="secondary" style={{ fontSize: '14px' }}>
                Войдите в свой аккаунт для продолжения
              </Text>
            </div>

            {/* Ошибка */}
            {error && (
              <Alert
                message="Ошибка авторизации"
                description={error}
                type="error"
                showIcon
                style={{ marginBottom: '24px', borderRadius: '8px' }}
                closable
                onClose={() => setError(null)}
              />
            )}

            {/* Форма */}
            <Form
              form={form}
              name="login"
              onFinish={onFinish}
              autoComplete="off"
              layout="vertical"
            >
              <Form.Item
                name="username"
                label="Email адрес"
                rules={[
                  { required: true, message: 'Введите email!' },
                  { type: 'email', message: 'Введите корректный email!' }
                ]}
              >
                <Input 
                  prefix={<UserOutlined style={{ color: '#bfbfbf' }} />} 
                  placeholder="your@email.com"
                  autoComplete="username"
                  style={{ borderRadius: '6px', padding: '8px 12px' }}
                />
              </Form.Item>

              <Form.Item
                name="password"
                label="Пароль"
                rules={[{ required: true, message: 'Введите пароль!' }]}
              >
                <Input.Password
                  prefix={<LockOutlined style={{ color: '#bfbfbf' }} />}
                  placeholder="Ваш пароль"
                  autoComplete="current-password"
                  style={{ borderRadius: '6px', padding: '8px 12px' }}
                />
              </Form.Item>

              <Form.Item style={{ marginBottom: '20px', marginTop: '24px' }}>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  block 
                  icon={<LoginOutlined />}
                  loading={loading}
                  style={{ 
                    height: '40px',
                    borderRadius: '6px',
                    fontSize: '14px',
                    fontWeight: '500',
                    background: 'linear-gradient(45deg, #1890ff, #40a9ff)',
                    border: 'none'
                  }}
                >
                  {loading ? 'Вход...' : 'Войти в систему'}
                </Button>
              </Form.Item>
            </Form>

            <Divider style={{ margin: '20px 0' }}>
              <Text type="secondary" style={{ fontSize: '12px' }}>или</Text>
            </Divider>

            {/* Ссылка на регистрацию */}
            <div style={{ textAlign: 'center', marginBottom: '20px' }}>
              <Text type="secondary" style={{ fontSize: '14px' }}>
                Нет аккаунта? 
              </Text>
              <br />
              <Link to="/register">
                <Button 
                  type="link" 
                  style={{ 
                    fontSize: '14px', 
                    fontWeight: '500',
                    padding: '4px 0',
                    height: 'auto'
                  }}
                >
                  Создать новый аккаунт
                </Button>
              </Link>
            </div>

            {/* Демо данные */}
            <Card 
              size="small"
              style={{ 
                background: '#f9f9f9', 
                border: '1px solid #e8e8e8',
                borderRadius: '6px'
              }}
            >
              <div style={{ textAlign: 'center' }}>
                <Text strong style={{ color: '#595959', fontSize: '13px' }}>
                  <ShopOutlined style={{ marginRight: '6px' }} />
                  Тестовые аккаунты
                </Text>
                <div style={{ marginTop: '8px', fontSize: '12px', color: '#8c8c8c' }}>
                  <div><strong>Admin:</strong> admin@marketplace.com / admin123</div>
                  <div><strong>Business:</strong> business@test.com / password</div>
                  <div><strong>User:</strong> user@test.com / password</div>
                </div>
              </div>
            </Card>
          </Card>
        </Col>
      </Row>
  );
};

export default Login;