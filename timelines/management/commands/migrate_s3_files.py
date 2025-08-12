from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from timelines.models import KeyPhoto
import boto3
from django.conf import settings
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Migrate existing S3 files to user-specific folders'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No files will be moved'))
        
        # Get S3 client
        s3_client = boto3.client('s3', region_name=settings.AWS_REGION)
        bucket_name = 'testguru-v2'
        
        # Get all KeyPhoto records
        key_photos = KeyPhoto.objects.all()
        
        self.stdout.write(f'Found {key_photos.count()} KeyPhoto records to process')
        
        moved_count = 0
        error_count = 0
        
        for key_photo in key_photos:
            try:
                old_s3_path = key_photo.s3_path
                
                # Check if the file is already in the new structure
                if old_s3_path.startswith('users/'):
                    self.stdout.write(f'Skipping {old_s3_path} - already in new structure')
                    continue
                
                # Generate new S3 path
                user_id = key_photo.user.id
                username = key_photo.user.username
                filename = key_photo.filename
                new_s3_path = f"users/{user_id}/{username}/keyphotos/{filename}"
                
                if dry_run:
                    self.stdout.write(f'Would move: {old_s3_path} -> {new_s3_path}')
                    continue
                
                # Check if source file exists
                try:
                    s3_client.head_object(Bucket=bucket_name, Key=old_s3_path)
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Source file not found: {old_s3_path} - {e}')
                    )
                    error_count += 1
                    continue
                
                # Copy file to new location
                copy_source = {'Bucket': bucket_name, 'Key': old_s3_path}
                s3_client.copy_object(
                    CopySource=copy_source,
                    Bucket=bucket_name,
                    Key=new_s3_path
                )
                
                # Delete old file
                s3_client.delete_object(Bucket=bucket_name, Key=old_s3_path)
                
                # Update database record
                key_photo.s3_path = new_s3_path
                key_photo.save()
                
                moved_count += 1
                self.stdout.write(f'Moved: {old_s3_path} -> {new_s3_path}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing {key_photo.id}: {e}')
                )
                error_count += 1
        
        # Summary
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'DRY RUN COMPLETE - Would move {moved_count} files')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Migration complete! Moved {moved_count} files, {error_count} errors'
                )
            )
