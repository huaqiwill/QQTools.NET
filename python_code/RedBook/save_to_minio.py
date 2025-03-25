import json
import os
import uuid

import requests
from minio import Minio
def save_minio(img_url):
    # 获取Minio的登录信息
    with open("E:\Software\minio\credentials.json", "rb") as file:
        loginData = file.read()
        loginData = loginData.decode("utf-8")
        loginData = json.loads(loginData)
        access_key = loginData["accessKey"]
        secret_key = loginData["secretKey"]
    # 初始化客户端
    client = Minio(
        "localhost:9000",
        access_key=access_key,
        secret_key = secret_key,
        secure=False
    )

    bucket_name = "red-book-images"
    image_name = str(uuid.uuid4())
    # 保存到Minio
    client.fput_object(bucket_name, image_name+".jpg", img_url)
    os.remove(img_url)
    return image_name


def download_image(url):
    response = requests.get(url,headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    file_url = os.path.join("tempImages","images.jpg")
    with open(file_url, "wb") as f:
        f.write(response.content)
    return file_url

def save_image_to_minio(url):
    return save_minio(download_image(url))
