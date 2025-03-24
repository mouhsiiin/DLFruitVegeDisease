import React, { useState, useRef } from 'react';
import { 
  Upload, 
  message, 
  Card, 
  Input, 
  Button, 
  Modal, 
  Image, 
  Typography, 
  Space, 
  Spin, 
  Alert 
} from 'antd';
import {
  InboxOutlined,
  LinkOutlined,
  CameraOutlined,
  CloudUploadOutlined,
} from '@ant-design/icons';
import Webcam from 'react-webcam';
import OllamaChat from './OllamaChat';

const { Dragger } = Upload;
const { Title, Paragraph } = Typography;

interface Prediction {
  prediction: string;
  confidence: number;
}

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

const FruitVeggieHealthApp: React.FC = () => {
  const [imageUrl, setImageUrl] = useState('');
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [cameraMode, setCameraMode] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ollamaChat, setOllamaChat] = useState(false);

  const webcamRef = useRef<Webcam>(null);

  const validateFile = (file: File): boolean => {
    if (!ALLOWED_FILE_TYPES.includes(file.type)) {
      message.error('Please upload a valid image file (JPEG, PNG, or WebP)');
      return false;
    }
    if (file.size > MAX_FILE_SIZE) {
      message.error('File size must be less than 5MB');
      return false;
    }
    return true;
  };

  const handlePrediction = async () => {
    if (!selectedFile && !imageUrl) {
      message.error('Please select an image or provide a URL first');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const formData = new FormData();
      if (selectedFile) {
        formData.append('image', selectedFile);
      }

      const response = await fetch('http://localhost:5050/predict', {
        method: 'POST',
        body: selectedFile ? formData : JSON.stringify({ image_url: imageUrl }),
        headers: selectedFile ? undefined : { 'Content-Type': 'application/json' },
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to process image');
      }

      setPrediction(data);
      setModalVisible(true);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Network error. Please try again.';
      setError(errorMessage);
      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (file: File) => {
    if (!validateFile(file)) {
      return false;
    }

    setSelectedFile(file);
    setImageUrl('');
    setError(null);
    
    const reader = new FileReader();
    reader.onload = () => setPreviewUrl(reader.result as string);
    reader.readAsDataURL(file);
    
    return false; // Prevent default upload behavior
  };

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setImageUrl(e.target.value);
    setSelectedFile(null);
    setPreviewUrl(e.target.value);
    setError(null);
  };

  const handleWebcamCapture = () => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (!imageSrc) {
      message.error('Failed to capture image');
      return;
    }

    setPreviewUrl(imageSrc);
    fetch(imageSrc)
      .then(res => res.blob())
      .then(blob => {
        const file = new File([blob], 'captured-image.jpg', { type: 'image/jpeg' });
        if (validateFile(file)) {
          setSelectedFile(file);
          setImageUrl('');
          setCameraMode(false);
        }
      })
      .catch(() => {
        message.error('Failed to process camera image');
      });
  };



  return (
    <div className='p-8'>
      {/* simple nav bar */}
      <div className='flex justify-center space-x-4 m-8'>
        <Button onClick={() => setOllamaChat(false)}>Fruit & Veggie Health Classifier</Button>
        <Button onClick={() => setOllamaChat(true)}>llama3.1 8b Chat</Button>
      </div>

      {ollamaChat && <OllamaChat />}
      
      {!ollamaChat &&
      
      <Space className='max-w-3xl mx-auto flex' direction="vertical" size="large">
        {/* Header Section */}
        <div style={{ textAlign: 'center' }}>
          <Image
            src="/logo.webp"
            alt="Logo"
            preview={false}
            style={{ width: 128, height: 128, borderRadius: '50%' }}
          />
          <Title level={2}>Fruit & Veggie Health Classifier</Title>
          <Paragraph type="secondary">
            Upload an image or provide a URL to identify fruits and vegetables and learn about their health benefits.
          </Paragraph>
        </div>




        {/* Main Input Card */}
        <Card title="Image Input" loading={loading}>
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Input
              placeholder="Enter image URL"
              value={imageUrl}
              onChange={handleUrlChange}
              prefix={<LinkOutlined />}
              disabled={loading}
            />

            <Dragger
              accept="image/*"
              beforeUpload={handleFileSelect}
              showUploadList={false}
              disabled={loading}
            >
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">Click or drag file to upload</p>
              <p className="ant-upload-hint">
                Support for JPEG, PNG, or WebP. Max size: 5MB
              </p>
            </Dragger>

            <Button
              type="dashed"
              icon={<CameraOutlined />}
              onClick={() => setCameraMode(true)}
              block
              disabled={loading}
            >
              Take a Picture
            </Button>

            {error && (
              <Alert
                message="Error"
                description={error}
                type="error"
                showIcon
                closable
                onClose={() => setError(null)}
              />
            )}

            {previewUrl && (
              <div style={{ textAlign: 'center' }}>
                <Image
                  src={previewUrl}
                  alt="Preview"
                  style={{ maxHeight: '300px' }}
                />
              </div>
            )}

            <Button
              type="primary"
              icon={<CloudUploadOutlined />}
              size='large'
              onClick={handlePrediction}
              block
              disabled={!previewUrl || loading}
            >
              {loading ? <Spin /> : 'Analyze Image'}
            </Button>
          </Space>
        </Card>

        {/* Results Card */}
        {prediction && (
          <Card title="Results">
            <div style={{ textAlign: 'center' }}>
              <Title level={3}>{prediction.prediction}</Title>
              <Paragraph>
                Confidence: {(prediction.confidence * 100).toFixed(1)}%
              </Paragraph>
            </div>
          </Card>
        )}

        {/* Camera Modal */}
        <Modal
          title="Take a Picture"
          open={cameraMode}
          onCancel={() => setCameraMode(false)}
          footer={[
            <Button key="back" onClick={() => setCameraMode(false)}>
              Cancel
            </Button>,
            <Button key="submit" type="primary" onClick={handleWebcamCapture}>
              Capture
            </Button>,
          ]}
        >
          <Webcam
            audio={false}
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            style={{ width: '100%' }}
          />
        </Modal>

        {/* Results Modal */}
        <Modal
          title="Prediction Result"
          open={modalVisible}
          centered
          onCancel={() => setModalVisible(false)}
          footer={[
            <Button key="close" type="primary" onClick={() => setModalVisible(false)}>
              Close
            </Button>,
          ]}
        >
          {prediction && (
            <div style={{ textAlign: 'center' }}>
              <Title level={3}>{prediction.prediction}</Title>
              <Paragraph>
                Confidence: {(prediction.confidence * 100).toFixed(1)}%
              </Paragraph>
            </div>
          )}
        </Modal>
      </Space>
      }
    </div>
  );
};

export default FruitVeggieHealthApp;