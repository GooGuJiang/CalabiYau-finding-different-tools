import React, { useState, useEffect } from 'react';
import { Layout, Upload, message, Modal, Spin, Drawer, Button, Image} from 'antd';
import { InboxOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import axios from 'axios';
const { Header, Content, Footer } = Layout;

const App = () => {
  const [visible, setVisible] = useState(false);
  const [imageSrc, setImageSrc] = useState('');
  const [loading, setLoading] = useState(false);
  const [drawerVisible, setDrawerVisible] = useState(false);

  useEffect(() => {
    const handlePaste = async (event) => {
      const items = (event.clipboardData || event.originalEvent.clipboardData).items;
      for (const item of items) {
        if (item.kind === 'file' && item.type.startsWith('image/')) {
          const file = item.getAsFile();
          await uploadImage({ file });
        }
      }
    };

    window.addEventListener('paste', handlePaste);
    return () => {
      window.removeEventListener('paste', handlePaste);
    };
  }, []);

  const uploadImage = async (options) => {
    const { file } = options;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('https://calabiyau-find-api.gmoe.link/process', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      const data = response.data;
      if (data.success) {
        message.success('图片处理成功！');
        setImageSrc(`data:${data.image_data.mime_type};base64,${data.image_data.content}`);
        setVisible(true);
      } else {
        message.error(data.message || '上传失败，请重试。');
      }
    } catch (error) {
      message.error('上传失败，请重试。');
    }
    setLoading(false);
  };
  
  useEffect(() => {
    const hasVisited = localStorage.getItem('hasVisited');
    if (!hasVisited) {
      setDrawerVisible(true);
      localStorage.setItem('hasVisited', 'true');
    }
  }, []);

  const handleCancel = () => {
    setVisible(false);
  };

  const toggleDrawer = () => {
    setDrawerVisible(!drawerVisible);
  };


  const exampleImageUrl = "/img/example-image.jpg";

  return (
    <Layout>
      <Header style={{ 
        borderRadius: '10px', 
        margin: '16px',
        display: 'flex', 
        justifyContent: 'space-between',
         alignItems: 'center', 
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'

      }}>
        <h2 style={{ margin: '0 16px', fontSize: '24px', fontWeight: 'bold', color: 'white' }}>
          卡拉彼丘找不同小助手
        </h2>
        <Button icon={<QuestionCircleOutlined />} onClick={toggleDrawer} style={{ marginRight: 16 }}>
          使用教程
        </Button>
      </Header>
      <Content style={{ padding: '0 48px' }}>
        <Spin spinning={loading} tip="正在处理图片...">
          <div style={{ marginTop: 26, height: '72vh', padding: 24 }}>
            <Upload.Dragger
              name="file"
              multiple={false}
              customRequest={uploadImage}
              showUploadList={false}
              accept="image/*"
            >
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
              <p className="ant-upload-hint">
                也支持通过粘贴（Ctrl+V）上传图片。
              </p>
            </Upload.Dragger>
            <Modal
              visible={visible}
              footer={null}
              onCancel={handleCancel}
              title="(可能)不同的区域"
            >
              <Image alt="Uploaded" style={{ width: '100%', height: 'auto' ,borderRadius: '10px'}} src={imageSrc} />
            </Modal>
          </div>
        </Spin>
      </Content>
      <Drawer
        title="使用教程"
        placement="right"
        onClose={toggleDrawer}
        visible={drawerVisible}
        width={320}
      >
        <p>欢迎使用卡拉彼丘找不同小助手！</p>
        <p>1. 点击或拖拽图片到上传区域或者使用截图工具截取屏幕使用（Ctrl+V）直接上传图片。</p>
        <p>2. 图片会自动上传到服务器进行处理，可能会有点慢。</p>
        <p>3. 处理完成后，会通过一个弹窗展示处理后的图片结果。</p>
        <p>如有任何问题，请联系 <a href="https://github.com/googujiang">咕谷酱</a> </p>
        
        <p style={{color: 'red',fontWeight: 'bold'}}>注意</p>
        <p style={{color: 'red',fontWeight: 'bold'}}>开始游戏建议等待7秒钟等UI特效结束再截图</p>
        <p style={{color: 'red',fontWeight: 'bold'}}>图片请保证全屏截图，因为要对比两边图片</p>
        <p style={{color: 'red',fontWeight: 'bold'}}>由于算法限制，有时可能无法识别所有不同区域。如果这种情况发生，请尝试重新开始找不同试试。</p>
        <p style={{color: 'red',fontWeight: 'bold'}}>服务器不会记录你的图片</p>
        <p>示例截图：</p>
        <Image src={exampleImageUrl} alt="示例截图" style={{ width: '100%', marginTop: '20px' }} />
        <p>如果可以的话，请考虑支持一下，谢谢喵:</p>
        <Button type="primary" href="https://afdian.net/a/memesearch" target="_blank">
          支持一下
        </Button>

      </Drawer>
      <Footer style={{ textAlign: 'center' }}>
        卡拉彼丘找不同小助手 ©2024 Created by <a href="https://github.com/googujiang">咕谷酱</a>
      </Footer>
    </Layout>
  );
};

export default App;
