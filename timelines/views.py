import os
import uuid
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, FileResponse, Http404
from django.conf import settings
import mimetypes


from rest_framework import permissions, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

from timelines.serializers import TimelineTypeSerializer, NewTimelineSerializer, KeyPhotoSerializer
from timelines.models import TimelineType, KeyPhoto, Timeline

import boto3
from botocore.exceptions import ClientError

# print('AWS_ACCESS_KEY_ID:', os.environ.get('AWS_ACCESS_KEY_ID'))
# print('AWS_SECRET_ACCESS_KEY:', os.environ.get('AWS_SECRET_ACCESS_KEY'))
# print('HOME:', os.environ.get('HOME'))

class TimelineTypeView(generics.ListAPIView):

    queryset = TimelineType.objects.all()
    serializer_class = TimelineTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']


class NewTimelineView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Uploads a photo to the server
        Expects multipart/form-data with a 'photo' field
        """
        if 'photo' not in request.FILES:
            return Response(
                {'error': 'Photo not found in request'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        photo = request.FILES['photo']
        
        # Check if it's an image
        if not photo.content_type.startswith('image/'):
            return Response(
                {'error': 'File must be an image'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create media folder if it doesn't exist
        media_dir = settings.MEDIA_ROOT
        os.makedirs(media_dir, exist_ok=True)
        
        # Generate a unique filename
        import uuid
        file_extension = os.path.splitext(photo.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(media_dir, unique_filename)
        
        # Save the file
        try:
            with open(file_path, 'wb+') as destination:
                for chunk in photo.chunks():
                    destination.write(chunk)
            
            # Return information about the saved file
            return Response({
                'message': 'Photo uploaded successfully',
                'filename': unique_filename,
                'original_name': photo.name,
                'size': photo.size,
                'content_type': photo.content_type,
                'url': f"{settings.MEDIA_URL}{unique_filename}"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Error saving file: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class KeyPhotoUploadView(APIView):
    """View for uploading photo to S3 and creating a KeyPhoto record"""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Uploads a photo to S3 and creates a KeyPhoto record in the database
        
        Expects multipart/form-data with fields:
        - photo: file image
        - photo_taken_at: date of photo creation (JSON)
        - weight_centigrams: weight in centigrams (optional, JSON)
        """
        try:
            # 1. Check if the file exists
            if 'photo' not in request.FILES:
                return Response(
                    {'error': 'No photo in request'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            photo = request.FILES['photo']

            # Get the file size by reading (if .size doesn't work)
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

            
            # 2. Check if the file is an image
            if not photo.content_type.startswith('image/'):
                return Response(
                    {'error': 'File must be an image'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 3. Get data from the request
            photo_taken_at = request.data.get('photo_taken_at')
            weight_centigrams = request.data.get('weight_centigrams')
            
            if not photo_taken_at:
                return Response(
                    {'error': 'photo_taken_at is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 4. Generate a unique filename
            file_extension = os.path.splitext(photo.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # 5. S3 settings with user-specific folder structure
            bucket_name = 'testguru-v2'
            user_id = request.user.id
            username = request.user.username
            s3_path = f"users/{username}/keyphotos/{unique_filename}"
            
            # 6. Upload the file to S3
            s3_client = boto3.client('s3', region_name=settings.AWS_REGION)
            
            try:
                s3_client.upload_fileobj(
                    photo,
                    bucket_name,
                    s3_path,
                    ExtraArgs={'ContentType': photo.content_type}
                )
                
                # 7. Generate a temporary link (for 1 hour)
                presigned_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': s3_path},
                    ExpiresIn=3600  # 1 hour
                )
                
                # 8. Create a record in the database
                key_photo_data = {
                    'filename': unique_filename,
                    's3_path': s3_path,
                    'presigned_url': presigned_url,
                    'photo_taken_at': photo_taken_at,
                    'file_size': file_size,
                }
                
                # Add weight if provided
                if weight_centigrams:
                    key_photo_data['weight_centigrams'] = int(weight_centigrams)
                
                serializer = KeyPhotoSerializer(data=key_photo_data, context={'request': request})
                if serializer.is_valid():
                    key_photo = serializer.save()
                    
                    return Response({
                        'message': 'Photo uploaded to S3 and saved to database',
                        'key_photo': serializer.data,
                        'presigned_url': presigned_url,
                        'filename': unique_filename
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        {'error': 'Validation error', 'details': serializer.errors}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
            except ClientError as e:
                return Response(
                    {'error': f'Error uploading to S3 or saving to database: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {'error': f'Unexpected error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class KeyPhotoDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, pk):
        """
        Get all fields of KeyPhoto by id (only if owned by current user)
        """
        try:
            obj = KeyPhoto.objects.get(pk=pk, user=request.user)
            from .serializers import KeyPhotoSerializer
            serializer = KeyPhotoSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except KeyPhoto.DoesNotExist:
            return Response({'error': f'KeyPhoto with id={pk} not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        """
        Soft delete: is_deleted=True (only if owned by current user)
        """
        try:
            obj = KeyPhoto.objects.get(pk=pk, user=request.user)
            obj.is_deleted = True
            obj.save()
            return Response({'message': f'KeyPhoto with id={pk} marked as deleted'}, status=status.HTTP_200_OK)
        except KeyPhoto.DoesNotExist:
            return Response({'error': f'KeyPhoto with id={pk} not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        """
        Hard delete: deletes the record from the database (only if owned by current user)
        """
        try:
            obj = KeyPhoto.objects.get(pk=pk, user=request.user)
            obj.delete()
            return Response({'message': f'KeyPhoto with id={pk} deleted from database'}, status=status.HTTP_200_OK)
        except KeyPhoto.DoesNotExist:
            return Response({'error': f'KeyPhoto with id={pk} not found'}, status=status.HTTP_404_NOT_FOUND)

class KeyPhotoDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, pk):
        try:
            obj = KeyPhoto.objects.get(pk=pk, user=request.user)
            if obj.is_deleted:
                return Response({'error': 'Photo deleted'}, status=410)
            s3 = boto3.client('s3', region_name='ru-central1')
            s3_response = s3.get_object(Bucket='testguru-v2', Key=obj.s3_path)
            fileobj = s3_response['Body']
            # Determine content_type by file extension
            content_type, _ = mimetypes.guess_type(obj.filename)
            if not content_type:
                content_type = 'application/octet-stream'
            return FileResponse(fileobj, content_type=content_type, filename=obj.filename)
        except KeyPhoto.DoesNotExist:
            raise Http404()
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class UserKeyPhotosView(APIView):
    """View for getting all KeyPhotos for the current user"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get all KeyPhotos for the current user"""
        try:
            key_photos = KeyPhoto.objects.filter(user=request.user, is_deleted=False).order_by('-created')
            serializer = KeyPhotoSerializer(key_photos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class UserTimelinesView(APIView):
    """View for getting all Timelines for the current user"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get all Timelines for the current user"""
        try:
            timelines = Timeline.objects.filter(user=request.user, is_deleted=False).order_by('-created')
            serializer = NewTimelineSerializer(timelines, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=500)