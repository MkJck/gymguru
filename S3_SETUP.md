# S3 Storage Setup

## Overview

This project uses Yandex Cloud S3-compatible storage for file uploads and media files.

## Configuration

### 1. AWS Credentials

Credentials are stored in `secrets.yml`:
```yaml
aws:
  access_key_id: "YOUR_ACCESS_KEY"
  secret_access_key: "YOUR_SECRET_KEY"
  region: "ru-central1"
```

### 2. S3 Settings

S3 configuration is in `gymguru/settings.py`:
- Bucket: `testguru-v2`
- Endpoint: `https://storage.yandexcloud.net`
- Region: `ru-central1`

### 3. Features

- **File Uploads**: Photos are uploaded directly to S3
- **Presigned URLs**: Temporary access links for uploaded files
- **User-specific folders**: Files are organized by username
- **Automatic file management**: Unique filenames with UUID

## Testing

### Test S3 Connection
```bash
make test-s3
```

### Manual Test
```bash
source venv/bin/activate
python test_s3.py
```

## File Structure

Files are stored in S3 with this structure:
```
testguru-v2/
├── users/
│   └── {username}/
│       └── keyphotos/
│           └── {uuid}.{extension}
└── static/
    └── {static_files}
```

## API Endpoints

- **POST** `/api/keyphoto/upload/` - Upload photo to S3
- **GET** `/api/keyphoto/{id}/download/` - Download photo from S3
- **GET** `/api/keyphoto/{id}/` - Get photo details
- **GET** `/api/user/keyphotos/` - List user's photos

## Troubleshooting

### Common Issues

1. **Authentication Error**: Check AWS credentials in `secrets.yml`
2. **Bucket Not Found**: Ensure bucket `testguru-v2` exists in Yandex Cloud
3. **Permission Denied**: Verify bucket permissions and IAM policies

### Debug Commands

```bash
# Check Django settings
python manage.py check

# Test S3 connection
make test-s3

# View bucket contents
python test_s3.py
```

## Dependencies

- `boto3` - AWS SDK for Python
- `django-storages` - Django storage backends
- `PyYAML` - YAML configuration parsing
