import { Button, Typography } from 'antd';
import 'antd/dist/reset.css';

const { Title } = Typography;

function App() {
  return (
    <div style={{ padding: '50px' }}>
      <Title level={1}>🛒 Маркетплейс</Title>
      <Button type="primary" size="large">
        Ant Design работает!
      </Button>
    </div>
  );
}

export default App;