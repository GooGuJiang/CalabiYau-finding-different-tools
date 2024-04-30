from PIL import Image, ImageEnhance
import numpy as np
import cv2
from skimage.metrics import structural_similarity as compare_ssim
import imutils
from io import BytesIO

def apply_mask(image, mask_height):
    """应用掩模以屏蔽图像的上下边界区域"""
    h, w = image.shape[:2]
    mask = np.ones((h, w), dtype=np.uint8)  # 创建全1的掩模
    mask[:mask_height, :] = 0  # 屏蔽上边界
    mask[h-mask_height:, :] = 0  # 屏蔽下边界
    return cv2.bitwise_and(image, image, mask=mask)

def enhance_image(image_path):
    try:
        img = Image.open(image_path)
    except:
        img = image_path
    
    contrast = ImageEnhance.Contrast(img)
    img = contrast.enhance(2.0)

    brightness = ImageEnhance.Brightness(img)
    img = brightness.enhance(1.5)

    sharpness = ImageEnhance.Sharpness(img)
    img = sharpness.enhance(2.0)

    color = ImageEnhance.Color(img)
    img = color.enhance(1.5)

    return img
def pil_to_opencv(pil_image):

    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')

    open_cv_image = np.array(pil_image)
    open_cv_image = open_cv_image[:, :, ::-1].copy() 
    return open_cv_image


def align_images(main_image, diff_image):

    sift = cv2.SIFT_create()
    keypoints_1, descriptors_1 = sift.detectAndCompute(main_image, None)
    keypoints_2, descriptors_2 = sift.detectAndCompute(diff_image, None)

    matcher = cv2.BFMatcher()
    matches = matcher.knnMatch(descriptors_1, descriptors_2, k=2)
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)

    if len(good) > 10:
        src_pts = np.float32([keypoints_1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([keypoints_2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        matrix, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
        
        height, width = main_image.shape[:2]
        aligned_diff = cv2.warpPerspective(diff_image, matrix, (width, height))

        return main_image, aligned_diff

    else:
        print("Not enough matches are found - {}/{}".format(len(good), 10))
        return main_image, diff_image
def is_similar_color(c1, c2, threshold=30):

    return np.sqrt(np.sum((c1[:3] - c2[:3]) ** 2)) < threshold

def remove_border(image_path, target_color_hex, threshold=90):
    target_color = np.array([int(target_color_hex[i:i+2], 16) for i in (0, 2, 4)])
    
    try:
        image = Image.open(image_path)
    except:
        image = image_path
    data = np.array(image)
    height, width, _ = data.shape
    top, bottom, left, right = 0, height, 0, width
    while top < bottom and np.all([is_similar_color(pixel, target_color, threshold) for pixel in data[top]]):
        top += 1
    while bottom > top and np.all([is_similar_color(pixel, target_color, threshold) for pixel in data[bottom-1]]):
        bottom -= 1
    while left < right and np.all([is_similar_color(data[row, left], target_color, threshold) for row in range(height)]):
        left += 1
    while right > left and np.all([is_similar_color(data[row, right-1], target_color, threshold) for row in range(height)]):
        right -= 1
    cropped_image = image.crop((left, top, right, bottom))
    return cropped_image

def find_differences(img1_path, img2_path):
    cropped_image_main = remove_border(img1_path, '805d43')
    cropped_image_diff = remove_border(img2_path, '805d43')

    cropped_image_main_show = pil_to_opencv(cropped_image_main)
    cropped_image_diff_show = pil_to_opencv(cropped_image_diff)

    cropped_image_main = enhance_image(cropped_image_main)
    cropped_image_diff = enhance_image(cropped_image_diff)

    cropped_image_main = pil_to_opencv(cropped_image_main)
    cropped_image_diff = pil_to_opencv(cropped_image_diff)

    cropped_image_main, cropped_image_diff = align_images(cropped_image_main, cropped_image_diff)

    mask_height = 10
    grayA = cv2.cvtColor(cropped_image_main, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(cropped_image_diff, cv2.COLOR_BGR2GRAY)
    grayA_masked = apply_mask(grayA, mask_height)
    grayB_masked = apply_mask(grayB, mask_height)

    (score, diff) = compare_ssim(grayA_masked, grayB_masked, full=True)
    diff = (diff * 255).astype("uint8")

    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    kernel = np.ones((50, 50), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=1)
    cnts = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    for c in cnts:
        if cv2.contourArea(c) > 100:
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(cropped_image_diff_show, (x, y), (x + w, y + h), (0, 0, 255), 2)

    return cropped_image_diff_show 

def process_and_get_image_bytes(img1_path, img2_path):

    processed_image = find_differences(img1_path, img2_path)
    
    is_success, buffer = cv2.imencode(".jpg", processed_image)
    if not is_success:
        raise ValueError("Could not convert image to byte array")
    
    byte_stream = BytesIO(buffer)
    return byte_stream.getvalue()



if __name__ == "__main__":
    img1_path = "left_object.png"
    img2_path = "right_object.png"
    byte_stream = process_and_get_image_bytes(img1_path, img2_path)
    with open("output.jpg", "wb") as f:
        f.write(byte_stream)
    print("Processed image saved asoutput.jpg")