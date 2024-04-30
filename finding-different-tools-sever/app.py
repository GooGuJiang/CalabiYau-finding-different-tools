from flask import Flask, request, send_file,jsonify
from PIL import Image
import io
from ImgHelper import *
from YoloHelper import YOLOImageProcessor
import json
import base64
from flask_cors import CORS

app = Flask(__name__)
yolo_processor = YOLOImageProcessor("./model/model.pt")
CORS(app)
def process_image(image_stream):
    yolo_re =yolo_processor.detect_and_crop(image_stream)
    byte_stream = process_and_get_image_bytes(yolo_re["left_crop"], yolo_re["right_crop"])
    return byte_stream

@app.route('/process', methods=['POST'])
def upload_and_process():
    if 'file' not in request.files:
        out_json = {
            "success": False,
            "status": "error",
            "message": "你文件去哪里了"
        }
        return jsonify(out_json)
    
    file = request.files['file']
    if file:
        yolo_re =yolo_processor.detect_and_crop(file)
        if yolo_re.get("status") == False:
            out_json = {
                "success": False,
                "status": "error",
                "message": yolo_re.get("message")
            }
            return jsonify(out_json)
        byte_stream = process_and_get_image_bytes(yolo_re["left_crop"], yolo_re["right_crop"])
        result_image_stream = io.BytesIO(byte_stream)
        result_image_stream = result_image_stream.getvalue()
        # 将处理后的图片字节流转换为 Base64 编码字符串
        image_base64 = base64.b64encode(result_image_stream).decode('utf-8')
        #full_base64_image = f'data:image/jpeg;base64,{image_base64}'
        response_data = {
            "success": True,
            "message": "图片处理成功",
            "image_data": {
                "content": image_base64,
                "mime_type": "image/jpeg"
            }
        }
        return jsonify(response_data)
    else:
        return jsonify({"success": False, "message": "图片未上传"})

if __name__ == '__main__':
    app.run(debug=False)
