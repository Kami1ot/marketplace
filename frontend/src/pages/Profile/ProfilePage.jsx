// src/pages/Profile/ProfilePage.jsx - ИСПРАВЛЕННАЯ ВЕРСИЯ
import { useState, useEffect } from 'react';
import { 
  Card, Typography, Row, Col, Avatar, Tag, Button, Statistic, 
  Tabs, Table, Space, message, Modal, Alert, Descriptions,
  Badge, Tooltip, Divider
} from 'antd';
import { 
  UserOutlined, ShopOutlined, StarOutlined, SettingOutlined,
  PlusOutlined, EditOutlined, EyeOutlined, DeleteOutlined,
  BarChartOutlined, DollarOutlined, InboxOutlined,
  ExclamationCircleOutlined, CheckCircleOutlined
} from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../../services/authService';
import { productsService } from '../../services/productsService';
// ИСПРАВЛЕННЫЙ ИМПОРТ
import ProductForm from '../../components/Product/ProductForm';

const { Title, Text, Paragraph } = Typography;
const { confirm } = Modal;

const ProfilePage = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [myProducts, setMyProducts] = useState([]);
  const [productsStats, setProductsStats] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [showProductForm, setShowProductForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    checkAuthAndLoadData();
  }, []);

  const checkAuthAndLoadData = async () => {
    try {
      // Проверяем авторизацию
      if (!authService.isAuthenticated()) {
        navigate('/login');
        return;
      }

      // Получаем актуальные данные пользователя с сервера
      const userData = await authService.getCurrentUser();
      setUser(userData);

      // Загружаем дополнительные данные для бизнес-пользователей
      if (userData.role === 'seller' || userData.role === 'admin') {
        await Promise.all([
          loadMyProducts(),
          loadProductsStats()
        ]);
      }
    } catch (error) {
      console.error('Ошибка загрузки данных:', error);
      if (error.detail === 'Could not validate credentials') {
        authService.logout();
        navigate('/login');
      } else {
        message.error('Ошибка загрузки профиля');
      }
    } finally {
      setLoading(false);
    }
  };

  const loadMyProducts = async () => {
    try {
      const products = await productsService.getMyProducts(true); // включая неактивные
      setMyProducts(products);
    } catch (error) {
      console.error('Ошибка загрузки товаров:', error);
      message.error('Ошибка загрузки товаров');
    }
  };

  const loadProductsStats = async () => {
    try {
      const stats = await productsService.getMyProductsStats();
      setProductsStats(stats);
    } catch (error) {
      console.error('Ошибка загрузки статистики:', error);
      message.error('Ошибка загрузки статистики');
    }
  };

  const handleProductAction = async (action, productId) => {
    try {
      switch (action) {
        case 'activate':
          await productsService.activateProduct(productId);
          message.success('Товар активирован');
          break;
        case 'deactivate':
          await productsService.deactivateProduct(productId);
          message.success('Товар деактивирован');
          break;
        case 'delete':
          await productsService.deleteProduct(productId);
          message.success('Товар удален');
          break;
      }
      await loadMyProducts();
      await loadProductsStats();
    } catch (error) {
      console.error('Ошибка выполнения операции:', error);
      message.error('Ошибка выполнения операции');
    }
  };

  const confirmDelete = (productId, productTitle) => {
    confirm({
      title: 'Удалить товар?',
      content: `Вы действительно хотите удалить "${productTitle}"? Это действие необратимо.`,
      okText: 'Удалить',
      okType: 'danger',
      cancelText: 'Отмена',
      onOk() {
        handleProductAction('delete', productId);
      }
    });
  };

  // Обработчики для формы товара
  const handleCreateProduct = () => {
    setEditingProduct(null);
    setShowProductForm(true);
  };

  const handleEditProduct = (product) => {
    setEditingProduct(product);
    setShowProductForm(true);
  };

  const handleProductFormSuccess = () => {
    setShowProductForm(false);
    setEditingProduct(null);
    loadMyProducts();
    loadProductsStats();
  };

  const handleProductFormCancel = () => {
    setShowProductForm(false);
    setEditingProduct(null);
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0
    }).format(price);
  };

  // Колонки таблицы товаров
  const productsColumns = [
    {
      title: 'Товар',
      dataIndex: 'title',
      key: 'title',
      render: (text, record) => (
        <div>
          <Text strong>{text}</Text>
          <br />
          <Text type="secondary" style={{ fontSize: '12px' }}>
            ID: {record.id}
          </Text>
        </div>
      ),
    },
    {
      title: 'Цена',
      dataIndex: 'price',
      key: 'price',
      render: (price) => <Text strong>{formatPrice(price)}</Text>,
      sorter: (a, b) => a.price - b.price,
    },
    {
      title: 'Количество',
      dataIndex: 'stock_quantity',
      key: 'stock_quantity',
      render: (qty, record) => (
        <Badge 
          count={qty} 
          style={{ 
            backgroundColor: qty > 0 ? '#52c41a' : '#ff4d4f',
            fontSize: '12px'
          }}
          overflowCount={999}
        />
      ),
      sorter: (a, b) => a.stock_quantity - b.stock_quantity,
    },
    {
      title: 'Статус',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? 'Активен' : 'Неактивен'}
        </Tag>
      ),
      filters: [
        { text: 'Активные', value: true },
        { text: 'Неактивные', value: false },
      ],
      onFilter: (value, record) => record.is_active === value,
    },
    {
      title: 'Создан',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleDateString('ru-RU'),
      sorter: (a, b) => new Date(a.created_at) - new Date(b.created_at),
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="Просмотреть">
            <Button type="text" icon={<EyeOutlined />} size="small" />
          </Tooltip>
          <Tooltip title="Редактировать">
            <Button 
              type="text" 
              icon={<EditOutlined />} 
              size="small"
              onClick={() => handleEditProduct(record)}
            />
          </Tooltip>
          {record.is_active ? (
            <Tooltip title="Деактивировать">
              <Button 
                type="text" 
                icon={<ExclamationCircleOutlined />} 
                size="small"
                onClick={() => handleProductAction('deactivate', record.id)}
              />
            </Tooltip>
          ) : (
            <Tooltip title="Активировать">
              <Button 
                type="text" 
                icon={<CheckCircleOutlined />} 
                size="small"
                onClick={() => handleProductAction('activate', record.id)}
              />
            </Tooltip>
          )}
          <Tooltip title="Удалить">
            <Button 
              type="text" 
              danger 
              icon={<DeleteOutlined />} 
              size="small"
              onClick={() => confirmDelete(record.id, record.title)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Title level={4}>Загрузка профиля...</Title>
      </div>
    );
  }

  if (!user) {
    return (
      <div>
        <Title level={1}>👤 Профиль пользователя</Title>
        <Card>
          <Text>Для просмотра профиля необходимо авторизоваться</Text>
          <div style={{ marginTop: '16px' }}>
            <Link to="/login">
              <Button type="primary">Войти в систему</Button>
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  // Определяем иконку и цвет для роли
  const getRoleInfo = (role) => {
    switch (role) {
      case 'admin':
        return { icon: <StarOutlined />, color: '#faad14', text: 'Администратор' };
      case 'seller':
        return { icon: <ShopOutlined />, color: '#52c41a', text: 'Бизнес-аккаунт' };
      default:
        return { icon: <UserOutlined />, color: '#1890ff', text: 'Пользователь' };
    }
  };

  const roleInfo = getRoleInfo(user.role);

  return (
    <div>
      {/* Заголовок */}
      <div style={{ marginBottom: '24px' }}>
        <Title level={1}>👤 Профиль пользователя</Title>
      </div>

      {/* Основная информация о пользователе */}
      <Card style={{ marginBottom: '24px' }}>
        <Row gutter={24} align="middle">
          <Col xs={24} sm={6} md={4} style={{ textAlign: 'center' }}>
            <Avatar 
              size={80} 
              style={{ backgroundColor: roleInfo.color }}
              icon={roleInfo.icon}
            />
          </Col>
          <Col xs={24} sm={18} md={20}>
            <div>
              <Title level={2} style={{ margin: 0, marginBottom: '8px' }}>
                {user.first_name} {user.last_name}
                <Tag 
                  color={roleInfo.color} 
                  style={{ marginLeft: '12px', fontSize: '14px' }}
                >
                  {roleInfo.text}
                </Tag>
              </Title>
              <Text type="secondary" style={{ fontSize: '16px', display: 'block', marginBottom: '8px' }}>
                {user.email}
              </Text>
              <Text type="secondary">
                Статус: {user.status ? 
                  <Tag color="green">Активен</Tag> : 
                  <Tag color="red">Заблокирован</Tag>
                }
              </Text>
            </div>
          </Col>
        </Row>
      </Card>

      {/* Контент в зависимости от роли */}
      <Tabs 
        activeKey={activeTab} 
        onChange={setActiveTab}
        items={[
          // Обзор - доступен всем
          {
            key: 'overview',
            label: 'Обзор',
            children: (
              <Row gutter={[16, 16]}>
                <Col xs={24} lg={12}>
                  <Card title="Информация о профиле" size="small">
                    <Descriptions column={1} size="small">
                      <Descriptions.Item label="Email">{user.email}</Descriptions.Item>
                      <Descriptions.Item label="Имя">{user.first_name || 'Не указано'}</Descriptions.Item>
                      <Descriptions.Item label="Фамилия">{user.last_name || 'Не указано'}</Descriptions.Item>
                      <Descriptions.Item label="Роль">{roleInfo.text}</Descriptions.Item>
                      <Descriptions.Item label="Дата регистрации">
                        {new Date(user.created_at).toLocaleDateString('ru-RU')}
                      </Descriptions.Item>
                    </Descriptions>
                  </Card>
                </Col>
                
                <Col xs={24} lg={12}>
                  <Card title="Быстрые действия" size="small">
                    <Space direction="vertical" style={{ width: '100%' }}>
                      {user.role === 'user' && (
                        <Alert
                          message="Хотите продавать товары?"
                          description="Обратитесь к администратору для получения бизнес-аккаунта"
                          type="info"
                          showIcon
                          action={
                            <Button size="small" type="primary">
                              Связаться
                            </Button>
                          }
                        />
                      )}
                      
                      {(user.role === 'seller' || user.role === 'admin') && (
                        <Button 
                          type="primary" 
                          icon={<PlusOutlined />} 
                          block
                          onClick={handleCreateProduct}
                        >
                          Добавить товар
                        </Button>
                      )}
                      
                      <Button icon={<SettingOutlined />} block>
                        Настройки профиля
                      </Button>
                    </Space>
                  </Card>
                </Col>
              </Row>
            )
          },
          
          // Мои товары - только для seller и admin
          ...(user.role === 'seller' || user.role === 'admin' ? [{
            key: 'products',
            label: 'Мои товары',
            children: (
              <div>
                {/* Статистика */}
                {productsStats && (
                  <Row gutter={16} style={{ marginBottom: '24px' }}>
                    <Col xs={12} sm={6}>
                      <Card size="small">
                        <Statistic
                          title="Всего товаров"
                          value={productsStats.total_products}
                          prefix={<InboxOutlined />}
                        />
                      </Card>
                    </Col>
                    <Col xs={12} sm={6}>
                      <Card size="small">
                        <Statistic
                          title="Активные"
                          value={productsStats.active_products}
                          valueStyle={{ color: '#3f8600' }}
                          prefix={<CheckCircleOutlined />}
                        />
                      </Card>
                    </Col>
                    <Col xs={12} sm={6}>
                      <Card size="small">
                        <Statistic
                          title="Неактивные"
                          value={productsStats.inactive_products}
                          valueStyle={{ color: '#cf1322' }}
                          prefix={<ExclamationCircleOutlined />}
                        />
                      </Card>
                    </Col>
                    <Col xs={12} sm={6}>
                      <Card size="small">
                        <Statistic
                          title="Стоимость"
                          value={productsStats.total_inventory_value}
                          precision={0}
                          prefix={<DollarOutlined />}
                          suffix="₽"
                        />
                      </Card>
                    </Col>
                  </Row>
                )}

                {/* Действия */}
                <div style={{ marginBottom: '16px' }}>
                  <Space>
                    <Button 
                      type="primary" 
                      icon={<PlusOutlined />}
                      onClick={handleCreateProduct}
                    >
                      Добавить товар
                    </Button>
                    <Button icon={<BarChartOutlined />}>
                      Аналитика
                    </Button>
                  </Space>
                </div>

                {/* Таблица товаров */}
                <Card>
                  <Table
                    columns={productsColumns}
                    dataSource={myProducts}
                    rowKey="id"
                    loading={loading}
                    size="small"
                    scroll={{ x: 800 }}
                    pagination={{
                      pageSize: 10,
                      showTotal: (total, range) => 
                        `${range[0]}-${range[1]} из ${total} товаров`,
                      showSizeChanger: true,
                      showQuickJumper: true,
                    }}
                  />
                </Card>
              </div>
            )
          }] : []),

          // Админ панель - только для admin
          ...(user.role === 'admin' ? [{
            key: 'admin',
            label: 'Админ панель',
            children: (
              <div>
                <Alert
                  message="Административные функции"
                  description="Здесь будет находиться панель администратора для управления пользователями и системой"
                  type="info"
                  showIcon
                  style={{ marginBottom: '24px' }}
                />
                
                <Row gutter={[16, 16]}>
                  <Col xs={24} sm={12} md={8}>
                    <Card title="Управление пользователями" size="small">
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Button block>Список пользователей</Button>
                        <Button block>Создать пользователя</Button>
                        <Button block>Роли и права</Button>
                      </Space>
                    </Card>
                  </Col>
                  
                  <Col xs={24} sm={12} md={8}>
                    <Card title="Управление товарами" size="small">
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Button block>Все товары</Button>
                        <Button block>Категории</Button>
                        <Button block>Модерация</Button>
                      </Space>
                    </Card>
                  </Col>
                  
                  <Col xs={24} sm={12} md={8}>
                    <Card title="Аналитика" size="small">
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Button block>Статистика платформы</Button>
                        <Button block>Отчеты</Button>
                        <Button block>Мониторинг</Button>
                      </Space>
                    </Card>
                  </Col>
                </Row>
              </div>
            )
          }] : [])
        ]}
      />

      {/* Форма создания/редактирования товара */}
      <ProductForm
        visible={showProductForm}
        onCancel={handleProductFormCancel}
        onSuccess={handleProductFormSuccess}
        product={editingProduct}
        mode={editingProduct ? 'edit' : 'create'}
      />
    </div>
  );
};

export default ProfilePage;