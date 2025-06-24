// frontend/src/components/Product/ProductForm.jsx
import { useState, useEffect } from 'react';
import { 
  Modal, Form, Input, InputNumber, Select, Upload, 
  Button, message, Row, Col, Card 
} from 'antd';
import { PlusOutlined, UploadOutlined } from '@ant-design/icons';
import { productsService } from '../../services/productsService';

const { TextArea } = Input;
const { Option } = Select;

const ProductForm = ({ 
  visible, 
  onCancel, 
  onSuccess, 
  product = null, // для редактирования
  mode = 'create' // 'create' или 'edit'
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState([]);
  const [imageList, setImageList] = useState([]);

  useEffect(() => {
    if (visible) {
      loadCategories();
      if (product && mode === 'edit') {
        // Заполняем форму данными товара для редактирования
        form.setFieldsValue({
          title: product.title,
          description: product.description,
          price: product.price,
          stock_quantity: product.stock_quantity,
          category_id: product.category_id,
        });
        
        // Устанавливаем изображения
        if (product.images && product.images.length > 0) {
          const images = product.images.map((img, index) => ({
            uid: `-${index}`,
            name: img,
            status: 'done',
            url: img, // В реальности здесь должен быть полный URL
          }));
          setImageList(images);
        }
      }
    } else {
      // Сбрасываем форму при закрытии
      form.resetFields();
      setImageList([]);
    }
  }, [visible, product, mode, form]);

  const loadCategories = async () => {
    try {
      const data = await productsService.getCategories();
      setCategories(data);
    } catch (error) {
      console.error('Ошибка загрузки категорий:', error);
    }
  };

  const handleSubmit = async (values) => {
    setLoading(true);
    
    try {
      // Подготавливаем данные
      const productData = {
        ...values,
        images: imageList.map(img => img.name || img.response?.filename || 'placeholder.jpg')
      };

      let result;
      if (mode === 'edit' && product) {
        result = await productsService.updateProduct(product.id, productData);
        message.success('Товар успешно обновлен!');
      } else {
        result = await productsService.createProduct(productData);
        message.success('Товар успешно создан!');
      }

      onSuccess(result);
      onCancel(); // Закрываем модальное окно
      
    } catch (error) {
      console.error('Ошибка сохранения товара:', error);
      message.error(error.detail || 'Ошибка сохранения товара');
    } finally {
      setLoading(false);
    }
  };

  // Настройки загрузки изображений
  const uploadProps = {
    name: 'file',
    multiple: true,
    fileList: imageList,
    onChange: ({ fileList }) => {
      setImageList(fileList);
    },
    beforeUpload: () => {
      // Пока что просто добавляем файлы в список без реальной загрузки
      return false;
    },
    onRemove: (file) => {
      setImageList(prev => prev.filter(item => item.uid !== file.uid));
    },
  };

  return (
    <Modal
      title={mode === 'edit' ? 'Редактировать товар' : 'Добавить новый товар'}
      open={visible}
      onCancel={onCancel}
      footer={null}
      width={800}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        autoComplete="off"
      >
        <Row gutter={16}>
          {/* Основная информация */}
          <Col span={24}>
            <Card title="Основная информация" size="small" style={{ marginBottom: 16 }}>
              <Form.Item
                name="title"
                label="Название товара"
                rules={[
                  { required: true, message: 'Введите название товара!' },
                  { min: 3, message: 'Название должно быть не менее 3 символов!' },
                  { max: 100, message: 'Название должно быть не более 100 символов!' }
                ]}
              >
                <Input 
                  placeholder="Например: iPhone 15 Pro Max 256GB"
                  showCount
                  maxLength={100}
                />
              </Form.Item>

              <Form.Item
                name="description"
                label="Описание"
                rules={[
                  { required: true, message: 'Введите описание товара!' },
                  { min: 10, message: 'Описание должно быть не менее 10 символов!' },
                  { max: 1000, message: 'Описание должно быть не более 1000 символов!' }
                ]}
              >
                <TextArea
                  rows={4}
                  placeholder="Детальное описание товара, его характеристики и особенности..."
                  showCount
                  maxLength={1000}
                />
              </Form.Item>

              <Form.Item
                name="category_id"
                label="Категория"
                rules={[{ required: true, message: 'Выберите категорию!' }]}
              >
                <Select 
                  placeholder="Выберите категорию товара"
                  showSearch
                  optionFilterProp="children"
                >
                  {categories.map(category => (
                    <Option key={category.id} value={category.id}>
                      {category.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Card>
          </Col>

          {/* Цена и количество */}
          <Col span={24}>
            <Card title="Цена и наличие" size="small" style={{ marginBottom: 16 }}>
              <Row gutter={16}>
                <Col xs={24} sm={12}>
                  <Form.Item
                    name="price"
                    label="Цена (₽)"
                    rules={[
                      { required: true, message: 'Введите цену!' },
                      { type: 'number', min: 1, message: 'Цена должна быть больше 0!' },
                      { type: 'number', max: 999999999, message: 'Цена слишком большая!' }
                    ]}
                  >
                    <InputNumber
                      style={{ width: '100%' }}
                      placeholder="0.00"
                      min={1}
                      max={999999999}
                      precision={2}
                      formatter={value => `₽ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                      parser={value => value.replace(/₽\s?|(,*)/g, '')}
                    />
                  </Form.Item>
                </Col>

                <Col xs={24} sm={12}>
                  <Form.Item
                    name="stock_quantity"
                    label="Количество в наличии"
                    rules={[
                      { required: true, message: 'Введите количество!' },
                      { type: 'number', min: 0, message: 'Количество не может быть отрицательным!' },
                      { type: 'number', max: 999999, message: 'Количество слишком большое!' }
                    ]}
                  >
                    <InputNumber
                      style={{ width: '100%' }}
                      placeholder="0"
                      min={0}
                      max={999999}
                      precision={0}
                    />
                  </Form.Item>
                </Col>
              </Row>
            </Card>
          </Col>

          {/* Изображения */}
          <Col span={24}>
            <Card title="Изображения товара" size="small" style={{ marginBottom: 16 }}>
              <Form.Item
                label="Загрузите изображения"
                extra="Рекомендуемый размер: 800x800px. Максимум 5 изображений."
              >
                <Upload
                  {...uploadProps}
                  listType="picture-card"
                  accept="image/*"
                  maxCount={5}
                >
                  {imageList.length >= 5 ? null : (
                    <div>
                      <PlusOutlined />
                      <div style={{ marginTop: 8 }}>Загрузить</div>
                    </div>
                  )}
                </Upload>
              </Form.Item>
            </Card>
          </Col>
        </Row>

        {/* Кнопки */}
        <Row justify="end" style={{ marginTop: 24 }}>
          <Col>
            <Button onClick={onCancel} style={{ marginRight: 8 }}>
              Отмена
            </Button>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading}
            >
              {mode === 'edit' ? 'Обновить товар' : 'Создать товар'}
            </Button>
          </Col>
        </Row>
      </Form>
    </Modal>
  );
};

export default ProductForm;