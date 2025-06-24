// src/App.jsx - исправленная версия без дублирования
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Button, Typography, Card, Space, Layout, Row, Col } from 'antd';
import { HomeOutlined, ShopOutlined, UserOutlined, LoginOutlined, LogoutOutlined } from '@ant-design/icons';
import { useState, useEffect } from 'react';

// Импорты страниц
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';
import ProductsPage from './pages/Products/ProductsPage';
import ProfilePage from './pages/Profile/ProfilePage';
import { authService } from './services/authService';

const { Title, Text } = Typography;
const { Header, Content, Footer } = Layout;

// Главная страница
const HomePage = () => (
  <div>
    <Title level={1}>🏠 Главная страница</Title>
    <Text type="secondary" style={{ fontSize: '16px', display: 'block', marginBottom: '24px' }}>
      Добро пожаловать в наш маркетплейс! Здесь вы можете покупать и продавать товары.
    </Text>
    
    <Row gutter={[16, 16]} style={{ marginTop: '32px' }}>
      <Col xs={24} sm={12} md={8}>
        <Card hoverable>
          <ShopOutlined style={{ fontSize: '48px', color: '#1890ff', marginBottom: '16px' }} />
          <Title level={4}>Покупать товары</Title>
          <Text>Тысячи товаров от проверенных продавцов</Text>
          <div style={{ marginTop: '16px' }}>
            <Link to="/products">
              <Button type="primary">Открыть каталог</Button>
            </Link>
          </div>
        </Card>
      </Col>
      <Col xs={24} sm={12} md={8}>
        <Card hoverable>
          <UserOutlined style={{ fontSize: '48px', color: '#52c41a', marginBottom: '16px' }} />
          <Title level={4}>Продавать товары</Title>
          <Text>Начните свой бизнес уже сегодня</Text>
          <div style={{ marginTop: '16px' }}>
            <Link to="/profile">
              <Button type="primary" style={{ background: '#52c41a', borderColor: '#52c41a' }}>
                Мой профиль
              </Button>
            </Link>
          </div>
        </Card>
      </Col>
      <Col xs={24} sm={12} md={8}>
        <Card hoverable>
          <LoginOutlined style={{ fontSize: '48px', color: '#faad14', marginBottom: '16px' }} />
          <Title level={4}>Присоединиться</Title>
          <Text>Создайте аккаунт за 2 минуты</Text>
          <div style={{ marginTop: '16px' }}>
            <Link to="/register">
              <Button type="primary" style={{ background: '#faad14', borderColor: '#faad14' }}>
                Регистрация
              </Button>
            </Link>
          </div>
        </Card>
      </Col>
    </Row>
  </div>
);

// Компонент навигации с поддержкой авторизации
const Navigation = () => {
  const location = useLocation();
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Проверяем авторизацию при загрузке
    if (authService.isAuthenticated()) {
      const userData = authService.getStoredUser();
      setUser(userData);
    }
  }, [location.pathname]); // Обновляем при смене страницы

  const handleLogout = () => {
    authService.logout();
    setUser(null);
    window.location.href = '/'; // Перенаправляем на главную
  };

  return (
    <Header 
      style={{ 
        background: '#fff', 
        padding: '0 24px', 
        borderBottom: '1px solid #f0f0f0',
        boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
      }}
    >
      <div 
        className="header-container"
        style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          maxWidth: '1600px',
          margin: '0 auto',
          flexWrap: 'wrap',
          gap: '16px'
        }}
      >
        <Link to="/" style={{ textDecoration: 'none' }}>
          <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
            🛒 Маркетплейс
          </Title>
        </Link>
        
        <div style={{ 
          display: 'flex', 
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '8px'
        }}>
          {user && (
            <Text style={{ 
              marginRight: '8px', 
              color: '#666',
              fontSize: '14px',
              whiteSpace: 'nowrap'
            }}>
              Привет, {user.first_name || user.email}!
            </Text>
          )}
          
          {/* Кастомное меню без сворачивания */}
          <div 
            className="nav-menu"
            style={{ 
              display: 'flex', 
              gap: '16px', 
              alignItems: 'center',
              flexWrap: 'wrap' // Позволяет переносить на следующую строку на маленьких экранах
            }}
          >
            <Link 
              to="/" 
              style={{ 
                color: location.pathname === '/' ? '#1890ff' : '#666',
                textDecoration: 'none',
                fontWeight: location.pathname === '/' ? 'bold' : 'normal',
                whiteSpace: 'nowrap'
              }}
            >
              <HomeOutlined style={{ marginRight: '4px' }} />
              Главная
            </Link>
            
            <Link 
              to="/products" 
              style={{ 
                color: location.pathname === '/products' ? '#1890ff' : '#666',
                textDecoration: 'none',
                fontWeight: location.pathname === '/products' ? 'bold' : 'normal',
                whiteSpace: 'nowrap'
              }}
            >
              <ShopOutlined style={{ marginRight: '4px' }} />
              Товары
            </Link>
            
            {user ? (
              <>
                <Link 
                  to="/profile" 
                  style={{ 
                    color: location.pathname === '/profile' ? '#1890ff' : '#666',
                    textDecoration: 'none',
                    fontWeight: location.pathname === '/profile' ? 'bold' : 'normal',
                    whiteSpace: 'nowrap'
                  }}
                >
                  <UserOutlined style={{ marginRight: '4px' }} />
                  Профиль
                </Link>
                
                <Button 
                  type="text" 
                  icon={<LogoutOutlined />}
                  onClick={handleLogout}
                  style={{ color: '#666' }}
                  size="small"
                >
                  Выйти
                </Button>
              </>
            ) : (
              <Link 
                to="/login" 
                style={{ 
                  color: location.pathname === '/login' ? '#1890ff' : '#666',
                  textDecoration: 'none',
                  fontWeight: location.pathname === '/login' ? 'bold' : 'normal',
                  whiteSpace: 'nowrap'
                }}
              >
                <LoginOutlined style={{ marginRight: '4px' }} />
                Вход
              </Link>
            )}
          </div>
        </div>
      </div>
    </Header>
  );
};

function App() {
  return (
    <Router>
      <Layout style={{ minHeight: '100vh', background: '#f5f5f5' }}>
        <Navigation />
        
        <Content style={{ padding: '24px' }}>
          <div style={{ 
            maxWidth: '1600px', 
            margin: '0 auto',
            background: '#fff', 
            padding: '32px', 
            borderRadius: '8px',
            minHeight: 'calc(100vh - 100px)',
            boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
          }}>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/products" element={<ProductsPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
            </Routes>
          </div>
        </Content>
        
        <Footer style={{ 
          textAlign: 'center', 
          background: '#f0f0f0',
          borderTop: '1px solid #e8e8e8'
        }}>
          Маркетплейс ©2024 | Создано с React + Ant Design
        </Footer>
      </Layout>
    </Router>
  );
}

export default App;