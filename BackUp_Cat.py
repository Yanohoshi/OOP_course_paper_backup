import requests
import json
import os
from datetime import datetime


class YandexDiskUploader:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://cloud-api.yandex.net/v1/disk/resources"
        self.headers = {
            "Authorization": f"OAuth {self.token}"
        }

    def create_folder(self, folder_name):
        """Создание папки на Яндекс.Диске"""
        url = self.base_url
        params = {"path": folder_name}
        response = requests.put(url, headers=self.headers, params=params)
        return response

    def get_upload_link(self, disk_file_path):
        """Получение ссылки для загрузки файла на Яндекс.Диск"""
        url = self.base_url + "/upload"
        params = {
            "path": disk_file_path,
            "overwrite": "true"
        }
        response = requests.get(url, headers=self.headers, params=params)
        return response.json().get("href")

    def upload_file(self, disk_file_path, file_content):
        """Загрузка файла на Яндекс.Диск"""
        upload_url = self.get_upload_link(disk_file_path)
        if upload_url:
            response = requests.put(upload_url, files={"file": file_content})
            return response.status_code == 201
        return False


def get_cat_image(text):
    """Получение картинки кошки с текстом с cataas.com"""
    url = f"https://cataas.com/cat/says/{text}"
    params = {
        #"size": 24,  # размер шрифта
        "width": 800, # статическая ширина картинки
        "height": 600, # статическая высота картинки
        "color": "white",  # цвет текста
        #"type": "square"  # тип изображения (квадрат) - отказался от решения, потому что картинки маленькие становились
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.content
    return None


def save_json_data(data, filename="upload_info.json"):
    """Сохранение информации о загруженных файлах в JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Информация сохранена в файл: {filename}")


def main():
    print("=== Резервное копирование картинок кошек ===")
    
    # Ввод данных пользователем
    text = input("Введите текст для картинки: ").strip()
    token = input("Введите токен Яндекс.Диска: ").strip()
    
    # Название группы (папки) - нужно изменить на ваше реальное название группы
    group_name = input("Введите название вашей группы в Негологии: ").strip()
    
    if not text or not token or not group_name:
        print("Ошибка: Все поля должны быть заполнены!")
        return
    
    # Инициализация загрузчика Яндекс.Диска
    uploader = YandexDiskUploader(token)
    
    # Создание папки на Яндекс.Диске
    print(f"Создание папки '{group_name}' на Яндекс.Диске...")
    folder_response = uploader.create_folder(group_name)
    
    if folder_response.status_code not in [201, 409]:  # 409 - если папка уже существует
        print(f"Ошибка создания папки: {folder_response.status_code}")
        print(f"Ответ: {folder_response.json()}")
        return
    
    print("Папка успешно создана или уже существует")
    
    # Получение картинки кошки
    print(f"Получение картинки с текстом '{text}'...")
    image_content = get_cat_image(text)
    
    if not image_content:
        print("Ошибка при получении картинки с cataas.com")
        return
    
    # Подготовка имени файла
    # Убираем специальные символы из текста для имени файла
    safe_filename = "".join(c for c in text if c.isalnum() or c in (' ', '_', '-')).rstrip()
    safe_filename = safe_filename.replace(' ', '_') + '.jpg'
    
    # Полный путь на Яндекс.Диске
    disk_file_path = f"{group_name}/{safe_filename}"
    
    # Загрузка на Яндекс.Диск
    print(f"Загрузка файла '{safe_filename}' на Яндекс.Диск...")
    upload_success = uploader.upload_file(disk_file_path, image_content)
    
    if upload_success:
        print("Файл успешно загружен на Яндекс.Диск!")
        
        # Сбор информации для JSON
        file_info = {
            "file_name": safe_filename,
            "original_text": text,
            "folder_name": group_name,
            "disk_path": disk_file_path,
            "file_size_bytes": len(image_content),
            "file_size_kb": len(image_content) / 1024,
            "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "cataas.com",
            "upload_status": "success"
        }
        
        # Сохранение информации в JSON файл
        save_json_data(file_info)
        
        print("\n=== Информация о загруженном файле ===")
        print(f"Название файла: {safe_filename}")
        print(f"Текст на картинке: {text}")
        print(f"Папка на Яндекс.Диске: {group_name}")
        print(f"Размер файла: {len(image_content)} байт ({len(image_content)/1024:.2f} КБ)")
        print(f"Путь на Яндекс.Диске: {disk_file_path}")
        
    else:
        print("Ошибка при загрузке файла на Яндекс.Диск")
        
        # Сохранение информации об ошибке в JSON
        error_info = {
            "file_name": safe_filename,
            "original_text": text,
            "folder_name": group_name,
            "disk_path": disk_file_path,
            "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "upload_status": "failed",
            "error": "Failed to upload to Yandex.Disk"
        }
        save_json_data(error_info, "upload_error.json")


if __name__ == "__main__":
    main()