// src/pages/Auth/Register.jsx
import { useState } from 'react';
import { Card, Form, Input, Button, Typography, Alert, Row, Col, message } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
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
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center',
      background: '#f0f2f5',
      padding: '20px'
    }}>
      <Row justify="center" style={{ width: '100%' }}>
        <Col xs={24} sm={20} md={16} lg={12} xl={8}>
          <Card style={{ padding: '24px' }}>
            <div style={{ textAlign: 'center', marginBottom: '32px' }}>
              <Title level={2} style={{ color: '#1890ff', marginBottom: '8px' }}>
                📝 Регистрация
              </Title>
              <Text type="secondary">
                Создайте аккаунт для покупки и продажи товаров
              </Text>
            </div>

            {error && (
              <Alert
                message="Ошибка регистрации"
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
              name="register"
              onFinish={onFinish}
              autoComplete="off"
              size="large"
              layout="vertical"
            >
              <Form.Item
                name="email"
                label="Email"
                rules={[
                  { required: true, message: 'Введите email!' },
                  { type: 'email', message: 'Введите корректный email!' }
                ]}
              >
                <Input 
                  prefix={<MailOutlined />} 
                  placeholder="your@email.com"
                  autoComplete="email"
                />
              </Form.Item>

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
                      prefix={<UserOutlined />} 
                      placeholder="Ваше имя"
                      autoComplete="given-name"
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
                      prefix={<UserOutlined />} 
                      placeholder="Ваша фамилия"
                      autoComplete="family-name"
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item
                name="password"
                label="Пароль"
                rules={[
                  { required: true, message: 'Введите пароль!' },
                  { min: 6, message: 'Пароль должен быть не менее 6 символов!' }
                ]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="Минимум 6 символов"
                  autoComplete="new-password"
                />
              </Form.Item>

              <Form.Item
                name="confirm_password"
                label="Подтверждение пароля"
                dependencies={['password']}
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
                  prefix={<LockOutlined />}
                  placeholder="Повторите пароль"
                  autoComplete="new-password"
                />
              </Form.Item>

              <Form.Item style={{ marginBottom: '16px' }}>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  block
                  loading={loading}
                >
                  {loading ? 'Регистрация...' : 'Зарегистрироваться'}
                </Button>
              </Form.Item>
            </Form>

            <div style={{ textAlign: 'center' }}>
              <Text type="secondary">
                Уже есть аккаунт? <Link to="/login" style={{ color: '#1890ff' }}>Войти</Link>
              </Text>
            </div>

            <div style={{ 
              marginTop: '24px', 
              padding: '16px', 
              background: '#f9f9f9', 
              borderRadius: '6px' 
            }}>
              <Text strong>Информация:</Text><br/>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                • Обычные пользователи могут просматривать товары<br/>
                • Для продажи товаров нужен бизнес-аккаунт<br/>
                • Обратитесь к админу для повышения роли
              </Text>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Register;