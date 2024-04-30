import React, { useState } from 'react';
import { Upload, Button, Row, Col, Modal, Spin, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import axios from 'axios';

function ImageUploadAndDisplay() {
  const [loading, setLoading] = useState(false);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [processedImage, setProcessedImage] = useState('');
  const [fileList, setFileList] = useState([]);

  const handleUpload = (file) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    axios.post('http://127.0.0.1:5000/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }).then(response => {
      if (response.status === 200 && response.data.success) {
        setProcessedImage(response.data.image_data.content);
        message.success('Image processed successfully.');
      } else {
        message.error('Failed to process image.');
      }
    }).catch(error => {
      console.error('Error:', error);
      message.error('Error during image processing.');
    }).finally(() => {
      setLoading(false);
    });

    // Prevent upload
    return false;
  };

  const handleChange = (info) => {
    let newFileList = [...info.fileList].slice(-1); // Keep only the last file
    setFileList(newFileList);
    handleUpload(newFileList[0].originFileObj);
  };

  return (
    <Row gutter={16}>
      <Col span={12}>
        <Upload
          fileList={fileList}
          beforeUpload={() => false}
          onChange={handleChange}
          onRemove={() => {
            setFileList([]);
            setProcessedImage('');
          }}
        >
          {fileList.length >= 1 ? null : <Button icon={<UploadOutlined />}>Select Image</Button>}
        </Upload>
      </Col>
      <Col span={12}>
        {loading ? (
          <Spin tip="Processing...">
            <div style={{ height: 200, border: '1px solid #f0f0f0', background: '#fafafa' }} />
          </Spin>
        ) : (
          processedImage && (
            <img alt="Processed" style={{ width: '100%', maxHeight: 200 }} src={processedImage} />
          )
        )}
      </Col>
    </Row>
  );
}

export default ImageUploadAndDisplay;
