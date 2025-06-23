// src/pages/Auth/Register.jsx - Улучшенная версия с правильной разметкой
import { useState } from 'react';
import { Card, Form, Input, Button, Typography, Alert, Row, Col, message, Divider, Steps } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, SafetyOutlined, UserAddOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../../services/authService';

const { Title, Text } = Typography;

const Register = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const onFinish = async (values) => {
    setLoading(true);
    setError(null);

    try {
      const result = await authService.register({
        email: values.email,
        password: values.password,
        first_name: values.first_name,
        last_name: values.last_name
      });

      message.success('Регистрация успешна! Теперь можете войти в систему.');
      console.log('Зарегистрирован пользователь:', result);
      
      // Перенаправляем на страницу входа
      navigate('/login');
      
    } catch (error) {
      console.error('Ошибка регистрации:', error);
      setError(error.detail || 'Ошибка регистрации. Попробуйте еще раз.');
    } finally {
      setLoading(false);
    }
  };

  return (
      <Row justify="center" align="middle" style={{ width: '100%', minHeight: '100vh' }}>
        <Col xs={22} sm={18} md={14} lg={12} xl={10}>
          <Card 
            style={{ 
              borderRadius: '16px',
              boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
              border: 'none'
            }}
          >
            {/* Заголовок */}
            <div style={{ textAlign: 'center', marginBottom: '40px' }}>
              <div style={{ 
                fontSize: '32px', 
                marginBottom: '16px',
                background: 'linear-gradient(45deg, #52c41a, #1890ff)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                📝
              </div>
              <Title level={2} style={{ margin: 0, color: '#262626', fontSize: '24px' }}>
                Создание аккаунта
              </Title>
              <Text type="secondary" style={{ fontSize: '14px' }}>
                Присоединяйтесь к нашему маркетплейсу
              </Text>
            </div>

            {/* Шаги регистрации */}
            <Steps
              size="small"
              current={0}
              style={{ marginBottom: '32px' }}
              items={[
                {
                  title: 'Данные',
                  icon: <UserOutlined />
                },
                {
                  title: 'Безопасность',
                  icon: <SafetyOutlined />
                },
                {
                  title: 'Готово',
                  icon: <UserAddOutlined />
                }
              ]}
            />

            {/* Ошибка */}
            {error && (
              <Alert
                message="Ошибка регистрации"
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
              name="register"
              onFinish={onFinish}
              autoComplete="off"
              size="medium"
              layout="vertical"
            >
              {/* Email */}
              <Form.Item
                name="email"
                label="Email адрес"
                rules={[
                  { required: true, message: 'Введите email!' },
                  { type: 'email', message: 'Введите корректный email!' }
                ]}
              >
                <Input 
                  prefix={<MailOutlined style={{ color: '#bfbfbf' }} />} 
                  placeholder="your@email.com"
                  autoComplete="email"
                  style={{ borderRadius: '8px', padding: '12px 16px' }}
                />
              </Form.Item>

              {/* Имя и фамилия */}
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="first_name"
                    label="Имя"
                    rules={[
                      { required: true, message: 'Введите имя!' },
                      { min: 2, message: 'Имя должно быть не менее 2 символов!' }
                    ]}
                  >
                    <Input 
                      prefix={<UserOutlined style={{ color: '#bfbfbf' }} />} 
                      placeholder="Ваше имя"
                      autoComplete="given-name"
                      style={{ borderRadius: '8px', padding: '12px 16px' }}
                    />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="last_name"
                    label="Фамилия"
                    rules={[
                      { required: true, message: 'Введите фамилию!' },
                      { min: 2, message: 'Фамилия должна быть не менее 2 символов!' }
                    ]}
                  >
                    <Input 
                      prefix={<UserOutlined style={{ color: '#bfbfbf' }} />} 
                      placeholder="Ваша фамилия"
                      autoComplete="family-name"
                      style={{ borderRadius: '8px', padding: '12px 16px' }}
                    />
                  </Form.Item>
                </Col>
              </Row>

              {/* Пароль */}
              <Form.Item
                name="password"
                label="Пароль"
                rules={[
                  { required: true, message: 'Введите пароль!' },
                  { min: 6, message: 'Пароль должен быть не менее 6 символов!' }
                ]}
                hasFeedback
              >
                <Input.Password
                  prefix={<LockOutlined style={{ color: '#bfbfbf' }} />}
                  placeholder="Минимум 6 символов"
                  autoComplete="new-password"
                  style={{ borderRadius: '8px', padding: '12px 16px' }}
                />
              </Form.Item>

              {/* Подтверждение пароля */}
              <Form.Item
                name="confirm_password"
                label="Подтверждение пароля"
                dependencies={['password']}
                hasFeedback
                rules={[
                  { required: true, message: 'Подтвердите пароль!' },
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || getFieldValue('password') === value) {
                        return Promise.resolve();
                      }
                      return Promise.reject(new Error('Пароли не совпадают!'));
                    },
                  }),
                ]}
              >
                <Input.Password
                  prefix={<LockOutlined style={{ color: '#bfbfbf' }} />}
                  placeholder="Повторите пароль"
                  autoComplete="new-password"
                  style={{ borderRadius: '8px', padding: '12px 16px' }}
                />
              </Form.Item>

              {/* Кнопка регистрации */}
              <Form.Item style={{ marginBottom: '24px', marginTop: '32px' }}>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  block
                  loading={loading}
                  style={{ 
                    height: '48px',
                    borderRadius: '8px',
                    fontSize: '16px',
                    fontWeight: '500',
                    background: 'linear-gradient(45deg, #52c41a, #73d13d)',
                    border: 'none'
                  }}
                >
                  {loading ? 'Создание аккаунта...' : 'Зарегистрироваться'}
                </Button>
              </Form.Item>
            </Form>

            <Divider style={{ margin: '24px 0' }}>
              <Text type="secondary">или</Text>
            </Divider>

            {/* Ссылка на вход */}
            <div style={{ textAlign: 'center', marginBottom: '24px' }}>
              <Text type="secondary">
                Уже есть аккаунт? 
              </Text>
              <br />
              <Link to="/login">
                <Button 
                  type="link" 
                  style={{ 
                    fontSize: '16px', 
                    fontWeight: '500',
                    padding: '4px 0',
                    height: 'auto'
                  }}
                >
                  Войти в систему
                </Button>
              </Link>
            </div>

            {/* Информация о ролях */}
            <Card 
              size="small"
              style={{ 
                background: '#f6ffed', 
                border: '1px solid #b7eb8f',
                borderRadius: '8px'
              }}
            >
              <div style={{ textAlign: 'center' }}>
                <Text strong style={{ color: '#389e0d' }}>
                  ℹ️ Информация о ролях
                </Text>
                <div style={{ marginTop: '12px', fontSize: '13px', color: '#52c41a' }}>
                  <div>👤 <strong>USER:</strong> Просмотр и покупка товаров</div>
                  <div>🏢 <strong>BUSINESS:</strong> Продажа товаров (обратитесь к админу)</div>
                  <div>👑 <strong>ADMIN:</strong> Полное управление платформой</div>
                </div>
              </div>
            </Card>
          </Card>
        </Col>
      </Row>
  );
};

export default Register;