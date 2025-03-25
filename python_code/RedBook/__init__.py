import warnings
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient
from selenium import webdriver
from time import sleep
from selenium.common import StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json
from selenium.webdriver.support import expected_conditions as EC
import re
from selenium.webdriver.support.wait import WebDriverWait
from RedBook.save_to_minio import save_image_to_minio

inputData = "发型"
# -----------------------------------------------
# 插入数据库操作
def insert_data(data):
    # MongoDB 连接配置
    client = MongoClient('mongodb://localhost:27017/')
    db = client['redBookData']
    collection = db['RedBook']

    try:
        # 检查是否已存在相同 title 和 author 的记录
        existing = collection.find_one({
            "title": data["title"],
            "author": data["author"]
        })

        if existing:
            print("重复数据")
            return False
        else:
            # 插入新数据
            result = collection.insert_one(data)
            print(f"插入成功，文档ID: {result.inserted_id}")
            return True

    except DuplicateKeyError as e:
        print(f"键重复错误: {e}")
        return False

# 获取数据
def extract_all_span_text(html_text):
    # ---------------------------------------------------------------------------------------------
    # 获取全部封面图片
    container_pattern = r'<div.*?class="img-container".*?>(.*?)</div>'
    container_matches = re.findall(container_pattern, html_text, re.DOTALL)

    temp_links = []
    all_links = []
    for container_content in container_matches:
        # 从每个 img-container 内容中提取所有 src 链接
        src_pattern = r'src="(https?://[^\"]+)"'
        links = re.findall(src_pattern, container_content)
        temp_links.extend(links)
    # 将图片保存到minio
    for image_url in list(set(temp_links)):
        images_uuid = save_image_to_minio(image_url)
        all_links.append(images_uuid)

    # ---------------------------------------------------------------------------------------------
    # 获取标题路径
    title_name = "未识别到标题"
    pattern = r'<div.*?id="detail-title" class="title">(.*?)</div>'
    math = re.search(pattern, html_text)
    if math:
        title_name = math.group(1)

    # --------------------------------------------------------------------------------------
    # 点赞数据
    if 'interact-container' in html_text:
        part = html_text.split('interact-container', 1)[1].strip()
    else:
        print("未找到 'interact-container' 字符串")

    pattern = r'<span.*?class="count"[^>]*>\s*([\d.]+万?)\s*</span>'
    numbers = re.findall(pattern, part)
    temp = []
    # 初始化存储数据的列表，假设每次查询有三个数据（点赞、评论、收藏）
    for i in range(0, len(numbers), 3):
        # 取出当前三个数据，如果不足三个则用 null 补齐
        current_numbers = numbers[i:i + 3]
        while len(current_numbers) < 3:
            current_numbers.append('无')
        # 创建键值对
        data_dict = {
            "likes": current_numbers[0],
            "Comments": current_numbers[1],
            "bookmarks": current_numbers[2]
        }
        temp.append(data_dict)
    save_interaction = []

    if  temp != []:
        for data in temp:
            save_interaction.append(data['likes'])
            save_interaction.append(data['Comments'])
            save_interaction.append(data['bookmarks'])
            break
    else:
        save_interaction.append('无')
        save_interaction.append('无')
        save_interaction.append('无')

    # ---------------------------------------------------------------------------------------
    # 获取评论
    user_content = []
    # 查找所有 note - text 的位置
    note_text_indices = [m.start() for m in re.finditer('note-text', html_text)]
    for index in note_text_indices:
        # 从 note - text 之后的位置开始查找 <span> 标签
        remaining_text = html_text[index:]
        pattern = r'<span>(.*?)</span>'
        match = re.search(pattern, remaining_text)
        if match:
            user_content.append(match.group(1))
    # 评论的数据
    user_content = [item for item in user_content if item and str(item).strip()]

    # -------------------------------------------------------------------------------------
    # 获取作者信息
    pattern = r'<span[^>]*class="username"[^>]*>(.*?)</span>'
    match = re.search(pattern, html_text)
    author = "无"
    if match:
        author = match.group(1)

    # ---------------------------------------------------------------------------------------
    # 整合数据
    data = {
        "key" : inputData,
        "title" : title_name,
        "author" : author,
        "all_links": all_links,
        "likes": save_interaction[0],
        "Comments": save_interaction[1],
        "bookmarks": save_interaction[2],
        "user_content": user_content
    }
    return data

# 页面数据获取
def ElementsData(driver, elements):
    # 获取额外数据
    elements_list = driver.find_elements(*elements)
    previous_count = len(elements_list)
    # 模拟滚动操作获取数据
    while True:
        # 第一次为开启刷新
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(0.5)
        # 重新获取元素
        elements_list = driver.find_elements(*elements)
        current_count = len(elements_list)

        # 检查元素数量是否增加
        if current_count == previous_count:
            break
        else:
            previous_count = current_count
    return elements_list


def initialize_driver():
    # 无头模式
    warnings.simplefilter('ignore', ResourceWarning)
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    # 正常模式
    # driver = webdriver.Chrome()
    driver.get("https://www.xiaohongshu.com/explore")
    driver.maximize_window()

    # 加载cookies
    try:
        with open('cookies.json', 'r', encoding='utf-8') as f:
            cookies = json.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        driver.refresh()
    except FileNotFoundError:
        print("未找到cookies文件，将在30秒内手动登录")
        sleep(30)
        # 保存新的cookies
        with open('cookies.json', 'w') as f:
            json.dump(driver.get_cookies(), f)
    return driver


def main():
    # 驱动对象
    driver = initialize_driver()
    try:
        # 搜索输入
        input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="search-input"]'))
        )
        input_element.send_keys(inputData)
        input_element.send_keys(Keys.ENTER)
        sleep(1)
        while True:  # 无限循环
            try:
                # 获取页面所有元素
                container = ElementsData(driver, (By.CLASS_NAME, 'mask'))
                total_elements = len(container)

                for index in range(total_elements):
                    try:
                        element = container[index]
                        # 滚动并点击
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'nearest'});",
                                              element)
                        sleep(0.5)  # 模拟人类操作间隔
                        driver.execute_script("arguments[0].click();", element)

                        # 获取更多数据功能
                        sleep(1)
                        data = extract_all_span_text(driver.page_source)

                        # 保存到数据库
                        insert_data(data)

                        # 返回列表页
                        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                        sleep(0.5)
                    except StaleElementReferenceException:
                        continue
                    except ElementClickInterceptedException:
                        print(f"点击被拦截，跳过索引: {index}")
                        continue
                    except Exception as e:
                        print(f"处理元素时出错: {str(e)}")
                        continue
                sleep(1)  # 等待新内容加载

                # 翻到底了
                pattern = re.compile(
                    r'class\s*=\s*"end-container"\s*>\s*-\s*THE\s+END\s+-',
                    flags=re.IGNORECASE
                )
                if pattern.search(driver.page_source):
                    print("THE END！所有数据获取完毕")
                    break

            except Exception as e:
                print(f"循环处理时出错: {str(e)}")
                sleep(5)  # 出错后等待重试

    except Exception as e:
        print(f"初始化时出错: {str(e)}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
