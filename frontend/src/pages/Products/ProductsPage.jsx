// src/pages/Products/ProductsPage.jsx
import { useState, useEffect } from 'react';
import { 
  Row, Col, Card, Typography, Input, Select, Button, Spin, 
  Empty, Alert, Tag, Space, Slider, InputNumber, Pagination,
  Badge, Tooltip, message 
} from 'antd';
import { 
  SearchOutlined, FilterOutlined, ShopOutlined, 
  EyeOutlined, HeartOutlined, ShoppingCartOutlined 
} from '@ant-design/icons';
import { productsService } from '../../services/productsService';

const { Title, Text, Paragraph } = Typography;
const { Search } = Input;
const { Option } = Select;

const ProductsPage = () => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Фильтры
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [priceRange, setPriceRange] = useState([0, 100000]);
  const [customPriceRange, setCustomPriceRange] = useState([0, 100000]);
  
  // Пагинация
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(12);
  const [total, setTotal] = useState(0);

  // Загрузка данных
  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Загружаем категории и товары параллельно
      const [categoriesData, productsData] = await Promise.all([
        productsService.getCategories(),
        productsService.getProducts({
          skip: (currentPage - 1) * pageSize,
          limit: pageSize,
          category_id: selectedCategory,
          search: searchTerm || undefined,
          min_price: priceRange[0] > 0 ? priceRange[0] : undefined,
          max_price: priceRange[1] < 100000 ? priceRange[1] : undefined
        })
      ]);
      
      setCategories(categoriesData);
      setProducts(productsData);
      setTotal(productsData.length); // В реальности API должен возвращать total count
      
    } catch (error) {
      console.error('Ошибка загрузки:', error);
      setError(error.detail || 'Ошибка загрузки товаров');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [currentPage, selectedCategory, searchTerm, priceRange]);

  // Применить фильтры
  const handleApplyFilters = () => {
    setPriceRange([...customPriceRange]);
    setCurrentPage(1);
  };

  // Сброс фильтров
  const handleResetFilters = () => {
    setSearchTerm('');
    setSelectedCategory(null);
    setPriceRange([0, 100000]);
    setCustomPriceRange([0, 100000]);
    setCurrentPage(1);
  };

  // Форматирование цены
  const formatPrice = (price) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0
    }).format(price);
  };

  // Карточка товара
  const ProductCard = ({ product }) => {
    const [liked, setLiked] = useState(false);

    return (
      <Card
        hoverable
        style={{ height: '100%', borderRadius: '12px' }}
        cover={
          <div 
            style={{ 
              height: '200px', 
              background: 'linear-gradient(45deg, #f0f2f5, #d9d9d9)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '48px',
              position: 'relative'
            }}
          >
            🛍️
            <div style={{ position: 'absolute', top: '8px', right: '8px' }}>
              <Space>
                <Button 
                  type="text" 
                  shape="circle" 
                  icon={<HeartOutlined style={{ color: liked ? '#ff4d4f' : '#bfbfbf' }} />}
                  onClick={() => setLiked(!liked)}
                  style={{ background: 'rgba(255,255,255,0.9)' }}
                />
              </Space>
            </div>
          </div>
        }
        actions={[
          <Tooltip title="Подробнее">
            <Button type="text" icon={<EyeOutlined />} />
          </Tooltip>,
          <Tooltip title="В корзину">
            <Button 
              type="text" 
              icon={<ShoppingCartOutlined />}
              onClick={() => message.success('Товар добавлен в корзину!')}
            />
          </Tooltip>
        ]}
      >
        <Card.Meta
          title={
            <div>
              <Text strong style={{ fontSize: '16px' }}>
                {product.title}
              </Text>
              {product.stock_quantity < 5 && (
                <Tag color="orange" size="small" style={{ marginLeft: '8px' }}>
                  Мало в наличии
                </Tag>
              )}
            </div>
          }
          description={
            <div>
              <Paragraph 
                ellipsis={{ rows: 2 }}
                style={{ marginBottom: '12px', color: '#666' }}
              >
                {product.description}
              </Paragraph>
              
              <div style={{ marginBottom: '8px' }}>
                <Text strong style={{ fontSize: '18px', color: '#52c41a' }}>
                  {formatPrice(product.price)}
                </Text>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  В наличии: {product.stock_quantity} шт.
                </Text>
                
                {product.category && (
                  <Tag color="blue" style={{ fontSize: '11px' }}>
                    {product.category.name}
                  </Tag>
                )}
              </div>
              
              {product.seller && (
                <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #f0f0f0' }}>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    <ShopOutlined style={{ marginRight: '4px' }} />
                    {product.seller.first_name} {product.seller.last_name}
                  </Text>
                </div>
              )}
            </div>
          }
        />
      </Card>
    );
  };

  if (error) {
    return (
      <Alert
        message="Ошибка загрузки товаров"
        description={error}
        type="error"
        showIcon
        action={
          <Button onClick={loadData} type="primary">
            Попробовать снова
          </Button>
        }
      />
    );
  }

  return (
    <div>
      {/* Заголовок */}
      <div style={{ marginBottom: '32px', textAlign: 'center' }}>
        <Title level={1} style={{ margin: 0 }}>
          🛍️ Каталог товаров
        </Title>
        <Text type="secondary" style={{ fontSize: '16px' }}>
          Найдите то, что ищете среди тысяч товаров
        </Text>
      </div>

      {/* Панель фильтров */}
      <Card 
        style={{ marginBottom: '24px', borderRadius: '12px' }}
        bodyStyle={{ padding: '20px' }}
      >
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={12} md={8}>
            <Search
              placeholder="Поиск товаров..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onSearch={loadData}
              style={{ width: '100%' }}
              enterButton={<SearchOutlined />}
            />
          </Col>
          
          <Col xs={24} sm={12} md={6}>
            <Select
              placeholder="Выберите категорию"
              value={selectedCategory}
              onChange={setSelectedCategory}
              style={{ width: '100%' }}
              allowClear
            >
              {categories.map(category => (
                <Option key={category.id} value={category.id}>
                  {category.name}
                </Option>
              ))}
            </Select>
          </Col>
          
          <Col xs={24} md={10}>
            <div>
              <Text strong style={{ marginBottom: '8px', display: 'block' }}>
                Диапазон цен
              </Text>
              
              {/* Поля ввода цены */}
              <Row gutter={8} style={{ marginBottom: '12px' }}>
                <Col span={10}>
                  <InputNumber
                    placeholder="От"
                    value={customPriceRange[0]}
                    onChange={(value) => setCustomPriceRange([value || 0, customPriceRange[1]])}
                    min={0}
                    max={customPriceRange[1]}
                    formatter={value => `₽ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                    parser={value => value.replace(/₽\s?|(,*)/g, '')}
                    style={{ width: '100%' }}
                    size="small"
                  />
                </Col>
                <Col span={4} style={{ textAlign: 'center', lineHeight: '24px' }}>
                  <Text type="secondary">—</Text>
                </Col>
                <Col span={10}>
                  <InputNumber
                    placeholder="До"
                    value={customPriceRange[1]}
                    onChange={(value) => setCustomPriceRange([customPriceRange[0], value || 100000])}
                    min={customPriceRange[0]}
                    max={1000000}
                    formatter={value => `₽ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                    parser={value => value.replace(/₽\s?|(,*)/g, '')}
                    style={{ width: '100%' }}
                    size="small"
                  />
                </Col>
              </Row>
              
              {/* Слайдер */}
              <Row gutter={8} align="middle">
                <Col span={16}>
                  <Slider
                    range
                    min={0}
                    max={100000}
                    step={1000}
                    value={customPriceRange}
                    onChange={setCustomPriceRange}
                    tooltip={{ 
                      formatter: (value) => formatPrice(value),
                    }}
                  />
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#999', marginTop: '4px' }}>
                    <span>0₽</span>
                    <span>{formatPrice(customPriceRange[0])} - {formatPrice(customPriceRange[1])}</span>
                    <span>100k₽</span>
                  </div>
                </Col>
                <Col span={8}>
                  <Space direction="vertical" size="small">
                    <Button 
                      type="primary" 
                      size="small"
                      onClick={handleApplyFilters}
                      icon={<FilterOutlined />}
                      style={{ width: '100%' }}
                    >
                      Применить
                    </Button>
                    <Button 
                      size="small"
                      onClick={handleResetFilters}
                      style={{ width: '100%' }}
                    >
                      Сброс
                    </Button>
                  </Space>
                </Col>
              </Row>
            </div>
          </Col>
        </Row>
      </Card>

      {/* Результаты */}
      <div style={{ marginBottom: '16px' }}>
        <Space>
          <Text type="secondary">
            {loading ? 'Загрузка...' : `Найдено товаров: ${products.length}`}
          </Text>
          {searchTerm && (
            <Tag closable onClose={() => setSearchTerm('')}>
              Поиск: "{searchTerm}"
            </Tag>
          )}
          {selectedCategory && (
            <Tag closable onClose={() => setSelectedCategory(null)} color="blue">
              {categories.find(c => c.id === selectedCategory)?.name}
            </Tag>
          )}
        </Space>
      </div>

      {/* Товары */}
      <Spin spinning={loading}>
        {products.length === 0 ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="Товары не найдены"
            style={{ margin: '60px 0' }}
          >
            <Button type="primary" onClick={handleResetFilters}>
              Сбросить фильтры
            </Button>
          </Empty>
        ) : (
          <>
            <Row gutter={[16, 16]}>
              {products.map(product => (
                <Col xs={24} sm={12} md={8} lg={6} key={product.id}>
                  <ProductCard product={product} />
                </Col>
              ))}
            </Row>
            
            {/* Пагинация */}
            <div style={{ textAlign: 'center', marginTop: '32px' }}>
              <Pagination
                current={currentPage}
                pageSize={pageSize}
                total={total}
                onChange={setCurrentPage}
                showSizeChanger={false}
                showQuickJumper
                showTotal={(total, range) => 
                  `${range[0]}-${range[1]} из ${total} товаров`
                }
              />
            </div>
          </>
        )}
      </Spin>
    </div>
  );
};

export default ProductsPage;