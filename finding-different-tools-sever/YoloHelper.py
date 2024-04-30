from ultralytics import YOLO
from PIL import Image

class YOLOImageProcessor:
    def __init__(self, model_path):
        """初始化 YOLO 模型"""
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            raise ValueError(f"Failed to load model: {e}")
        
    def extract_names(self,results):
        detected_names = []
        # 遍历每个结果对象
        for r in results:
            boxes = r.boxes
            for box in boxes:
                c = box.cls
                detected_names.append(self.model.names[int(c)])

        return detected_names

    def detect_and_crop(self, image_path):
        """加载图片、预测并裁剪对象"""
        try:
            img = Image.open(image_path)
        except IOError:
            raise IOError("Image could not be loaded")

        try:
            results = self.model.predict(source=img)
        except Exception as e:
            raise RuntimeError(f"Prediction failed: {e}")

        if results is None or len(results) == 0:
            return {'status': False, 'message': "没有检测结果返回"}

        result = results[0]
        width, height = img.size
        
        if len(result.boxes.xyxy) != 2:
            return {'status': False, 'message': "检测到的对象数量不为2"}

        detected_names = self.extract_names(results)

        left_obj, right_obj = None, None
        for box in result.boxes.xyxy:
            x1, y1, x2, y2 = box.numpy()
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            obj_center = (x2 + x1) // 2

            if obj_center < width // 2 and left_obj is None:
                left_obj = (x1, y1, x2, y2)
            elif obj_center >= width // 2 and right_obj is None:
                right_obj = (x1, y1, x2, y2)

        if left_obj and right_obj:
            left_crop = img.crop(left_obj)
            right_crop = img.crop(right_obj)
            return {'status': True, 'left_crop': left_crop, 'right_crop': right_crop,'detected_names': detected_names}
        else:
            return {'status': False, 'message': "未能正确地在图像的左右两侧找到对象"}

if __name__ == "__main__":
    # 使用示例：
    processor = YOLOImageProcessor("./model/model.pt")
    result = processor.detect_and_crop("87216384dbfd666ed24609ea80a4f5a4.jpg")
    if result['status']:
        # 如果检测并裁剪成功保存图片
        result['left_crop'].save("left_crop.png")
        result['right_crop'].save("right_crop.png")
        print("Objects detected and cropped successfully.")
        # 这里可以显示或保存裁剪的图片，例如 result['left_crop'] 和 result['right_crop']
    else:
        # 输出错误信息
        print(result['message'])
