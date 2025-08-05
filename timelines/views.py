import os
import uuid
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings

from rest_framework import permissions, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from timelines.serializers import TimelineTypeSerializer, NewTimelineSerializer, KeyPhotoSerializer
from timelines.models import TimelineType, KeyPhoto

import boto3
from botocore.exceptions import ClientError

import os
print('AWS_ACCESS_KEY_ID:', os.environ.get('AWS_ACCESS_KEY_ID'))
print('AWS_SECRET_ACCESS_KEY:', os.environ.get('AWS_SECRET_ACCESS_KEY'))
print('HOME:', os.environ.get('HOME'))

class TimelineTypeView(generics.ListAPIView):

    queryset = TimelineType.objects.all()
    serializer_class = TimelineTypeSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get']


class NewTimelineView(APIView):
    permission_classes = [permissions.AllowAny]

    # @csrf_exempt
    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)

    def post(self, request):
        serializer = NewTimelineSerializer(
            data=request.data,
            context={'request': request}
            )
        if serializer.is_valid():
            timeline = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhotoUploadView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Загружает фотографию на сервер
        Ожидает multipart/form-data с полем 'photo'
        """
        if 'photo' not in request.FILES:
            return Response(
                {'error': 'Фотография не найдена в запросе'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        photo = request.FILES['photo']
        
        # Проверяем, что это изображение
        if not photo.content_type.startswith('image/'):
            return Response(
                {'error': 'Файл должен быть изображением'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Создаем папку media если её нет
        media_dir = settings.MEDIA_ROOT
        os.makedirs(media_dir, exist_ok=True)
        
        # Генерируем уникальное имя файла
        import uuid
        file_extension = os.path.splitext(photo.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(media_dir, unique_filename)
        
        # Сохраняем файл
        try:
            with open(file_path, 'wb+') as destination:
                for chunk in photo.chunks():
                    destination.write(chunk)
            
            # Возвращаем информацию о сохраненном файле
            return Response({
                'message': 'Фотография успешно загружена',
                'filename': unique_filename,
                'original_name': photo.name,
                'size': photo.size,
                'content_type': photo.content_type,
                'url': f"{settings.MEDIA_URL}{unique_filename}"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Ошибка при сохранении файла: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def test_upload_page(request):
    """
    Простая страница для тестирования загрузки фотографий
    """
    with open('test_upload.html', 'r', encoding='utf-8') as f:
        content = f.read()
    return HttpResponse(content)


class PhotoListView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """
        Возвращает список всех загруженных фотографий
        """
        try:
            media_dir = settings.MEDIA_ROOT
            
            # Проверяем, что папка media существует
            if not os.path.exists(media_dir):
                return Response(
                    {'message': 'Папка media не найдена', 'photos': []}, 
                    status=status.HTTP_200_OK
                )
            
            # Получаем список всех файлов в папке media
            photos = []
            for filename in os.listdir(media_dir):
                file_path = os.path.join(media_dir, filename)
                
                # Проверяем, что это файл (не папка)
                if os.path.isfile(file_path):
                    # Получаем информацию о файле
                    file_stat = os.stat(file_path)
                    
                    # Проверяем, что это изображение по расширению
                    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
                    file_extension = os.path.splitext(filename)[1].lower()
                    
                    if file_extension in image_extensions:
                        photos.append({
                            'filename': filename,
                            'url': f"{settings.MEDIA_URL}{filename}",
                            'size': file_stat.st_size,
                            'created_at': file_stat.st_ctime,
                            'modified_at': file_stat.st_mtime
                        })
            
            # Сортируем по дате создания (новые сначала)
            photos.sort(key=lambda x: x['created_at'], reverse=True)
            
            return Response({
                'message': f'Найдено {len(photos)} фотографий',
                'photos': photos,
                'total_count': len(photos)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Ошибка при получении списка фотографий: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PhotoDetailView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, filename):
        """
        Возвращает информацию о конкретной фотографии по имени файла
        """
        try:
            media_dir = settings.MEDIA_ROOT
            file_path = os.path.join(media_dir, filename)
            
            # Проверяем, что файл существует
            if not os.path.exists(file_path):
                return Response(
                    {'error': 'Фотография не найдена'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Проверяем, что это файл (не папка)
            if not os.path.isfile(file_path):
                return Response(
                    {'error': 'Указанный путь не является файлом'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Получаем информацию о файле
            file_stat = os.stat(file_path)
            
            # Проверяем, что это изображение по расширению
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
            file_extension = os.path.splitext(filename)[1].lower()
            
            if file_extension not in image_extensions:
                return Response(
                    {'error': 'Файл не является изображением'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response({
                'filename': filename,
                'url': f"{settings.MEDIA_URL}{filename}",
                'size': file_stat.st_size,
                'created_at': file_stat.st_ctime,
                'modified_at': file_stat.st_mtime,
                'content_type': f'image/{file_extension[1:]}' if file_extension != '.jpg' else 'image/jpeg'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Ошибка при получении информации о фотографии: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class KeyPhotoUploadView(APIView):
    """View для загрузки фото в S3 и создания записи KeyPhoto"""
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Загружает фотографию в S3 и создает запись KeyPhoto в БД
        
        Ожидает multipart/form-data с полями:
        - photo: файл изображения
        - photo_taken_at: дата создания фото (JSON)
        - weight_centigrams: вес в сантиграммах (опционально, JSON)
        """
        try:
            # 1. Проверяем наличие файла
            if 'photo' not in request.FILES:
                return Response(
                    {'error': 'Фотография не найдена в запросе'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            photo = request.FILES['photo']

            # Получаем размер файла через чтение (если .size не работает)
            try:
                file_size = photo.size
                if not file_size:
                    # fallback
                    file_bytes = photo.read()
                    file_size = len(file_bytes)
                    photo.seek(0)
            except Exception:
                file_bytes = photo.read()
                file_size = len(file_bytes)
                photo.seek(0)

            
            # 2. Проверяем тип файла (изображение)
            if not photo.content_type.startswith('image/'):
                return Response(
                    {'error': 'Файл должен быть изображением'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 3. Получаем данные из запроса
            photo_taken_at = request.data.get('photo_taken_at')
            weight_centigrams = request.data.get('weight_centigrams')
            
            if not photo_taken_at:
                return Response(
                    {'error': 'Поле photo_taken_at обязательно'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 4. Генерируем уникальное имя файла
            file_extension = os.path.splitext(photo.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # 5. Настройки S3
            bucket_name = 'testguru-v2'
            s3_path = f"keyphotos/{unique_filename}"
            
            # 6. Загружаем файл в S3
            s3_client = boto3.client('s3', region_name='ru-central1')
            
            try:
                s3_client.upload_fileobj(
                    photo,
                    bucket_name,
                    s3_path,
                    ExtraArgs={'ContentType': photo.content_type}
                )
                
                # 7. Генерируем временную ссылку (на 1 час)
                presigned_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': s3_path},
                    ExpiresIn=3600  # 1 час
                )
                
                # 8. Создаем запись в БД
                key_photo_data = {
                    'filename': unique_filename,
                    's3_path': s3_path,
                    's3_url': presigned_url,
                    'photo_taken_at': photo_taken_at,
                    'file_size': file_size,
                    'content_type': photo.content_type,
                }
                
                # Добавляем вес, если передан
                if weight_centigrams:
                    key_photo_data['weight_centigrams'] = int(weight_centigrams)
                
                serializer = KeyPhotoSerializer(data=key_photo_data)
                if serializer.is_valid():
                    key_photo = serializer.save()
                    
                    return Response({
                        'message': 'Фотография успешно загружена в S3',
                        'key_photo': serializer.data,
                        's3_url': presigned_url,
                        'filename': unique_filename
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        {'error': 'Ошибка валидации данных', 'details': serializer.errors}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
            except ClientError as e:
                return Response(
                    {'error': f'Ошибка загрузки в S3: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {'error': f'Неожиданная ошибка: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def test_keyphoto_upload_page(request):
    """
    Страница для тестирования загрузки KeyPhoto в S3
    """
    with open('test_keyphoto_upload.html', 'r', encoding='utf-8') as f:
        content = f.read()
    return HttpResponse(content)