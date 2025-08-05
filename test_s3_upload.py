import boto3
import os
from botocore.exceptions import ClientError

def test_s3_upload():
    """Тестирует загрузку файла в S3"""
    try:
        # Создаем клиент S3
        s3_client = boto3.client('s3', region_name='ru-central1')
        
        # Проверяем доступ к бакету
        bucket_name = 'testguru-v2'
        print(f"Проверяем доступ к бакету {bucket_name}...")
        
        # Пробуем загрузить тестовый файл
        test_file_path = 'media/photo-01.jpg'
        if os.path.exists(test_file_path):
            print(f"Найден файл: {test_file_path}")
            
            # Генерируем уникальное имя для теста
            import uuid
            test_key = f"test-upload-{uuid.uuid4()}.jpg"
            
            print(f"Загружаем файл как {test_key}...")
            
            # Загружаем файл
            with open(test_file_path, 'rb') as file:
                s3_client.upload_fileobj(
                    file,
                    bucket_name,
                    test_key,
                    ExtraArgs={'ContentType': 'image/jpeg'}
                )
            
            print(f"✅ Файл успешно загружен в S3!")
            print(f"Путь в S3: s3://{bucket_name}/{test_key}")
            
            # Генерируем временную ссылку
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': test_key},
                ExpiresIn=3600
            )
            print(f"Временная ссылка: {presigned_url}")
            
            return True
            
        else:
            print(f"❌ Файл {test_file_path} не найден")
            return False
            
    except ClientError as e:
        print(f"❌ Ошибка S3: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

if __name__ == "__main__":
    test_s3_upload() 