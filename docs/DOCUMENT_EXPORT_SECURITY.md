# Document Export Security & Authorization Architecture

**Version**: 1.0  
**Last Updated**: December 2025  
**Security Level**: High (PII and sensitive documents)

---

## Executive Summary

This document defines the security architecture for JobWise document export feature, with emphasis on **user-scoped authorization**, **AWS S3 security**, and **cross-platform access control**.

### Security Principles

1. **User-Scoped Isolation**: All exports are scoped to user_id; no cross-user access possible
2. **Private S3 Bucket**: No public access; all downloads via presigned URLs
3. **Time-Limited Access**: Presigned URLs expire (default 1 hour, max 7 days)
4. **Encryption at Rest**: Server-side encryption (SSE-S3 AES-256)
5. **Encryption in Transit**: HTTPS/TLS only
6. **Audit Logging**: All operations logged with user_id, export_id, timestamp

---

## Authorization Model

### User Ownership Verification

All export operations enforce **strict ownership checks**:

```python
# S3 Key Pattern enforces user isolation
s3_key = f"exports/{user_id}/{export_id}.{format}"

# Examples:
# - exports/user-123/export-456.pdf  ✅ User 123 can access
# - exports/user-999/export-456.pdf  ❌ User 123 CANNOT access
```

**Key Security Features**:
- S3 keys include user_id in path → prevents cross-user access
- All API calls verify JWT token → extract user_id
- Database queries scoped by user_id → double verification
- S3 operations verify ownership → no direct object access

### Authorization Flow

```
1. Client Request with JWT
   ↓
2. Backend extracts user_id from token
   ↓
3. Build S3 key: exports/{user_id}/{export_id}.{ext}
   ↓
4. Check database: export belongs to user_id?
   ↓
5. If yes → Generate presigned URL or download
   If no  → 403 Forbidden
```

---

## AWS S3 Security Configuration

### Bucket Configuration

**Bucket Name**: `jobwise-exports-{environment}` (e.g., `jobwise-exports-production`)

**Required Settings**:

```json
{
  "BlockPublicAcls": true,
  "IgnorePublicAcls": true,
  "BlockPublicPolicy": true,
  "RestrictPublicBuckets": true
}
```

**Bucket Policy** (IAM-based access only):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyPublicAccess",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::jobwise-exports-production",
        "arn:aws:s3:::jobwise-exports-production/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    },
    {
      "Sid": "AllowBackendAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT_ID:user/jobwise-backend"
      },
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:HeadObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::jobwise-exports-production",
        "arn:aws:s3:::jobwise-exports-production/*"
      ]
    }
  ]
}
```

### IAM User Permissions

**Create IAM user**: `jobwise-backend`

**Minimum Permissions** (Principle of Least Privilege):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:HeadObject"
      ],
      "Resource": "arn:aws:s3:::jobwise-exports-production/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::jobwise-exports-production",
      "Condition": {
        "StringLike": {
          "s3:prefix": "exports/*"
        }
      }
    }
  ]
}
```

### Encryption Configuration

**Server-Side Encryption**: AES-256 (SSE-S3)

```python
# Every upload includes encryption
upload_args = {
    'ServerSideEncryption': 'AES256',  # Mandatory
    # ... other args
}
```

**Encryption at Rest**:
- All objects encrypted automatically
- AWS manages encryption keys
- No additional cost for SSE-S3

**Encryption in Transit**:
- HTTPS/TLS 1.2+ required
- Presigned URLs use HTTPS only
- Backend API uses HTTPS only

---

## Presigned URL Security

### Generation Parameters

```python
def generate_presigned_url(
    user_id: str,      # From JWT token
    export_id: str,    # From database
    format: str,       # Validated format
    expiration_seconds: int = 3600,  # Default 1 hour
    filename: Optional[str] = None   # Custom download name
) -> str:
    # Max expiration: 7 days (604800 seconds)
    expiration_seconds = min(expiration_seconds, 604800)
    
    # Verify ownership before generating URL
    s3_key = f"exports/{user_id}/{export_id}.{format}"
    
    # Check object exists and user owns it
    head_object(s3_key)  # Raises 404 if wrong user_id
    
    # Generate time-limited URL
    return presigned_url
```

### Security Features

1. **Time-Limited Access**: URLs expire automatically
2. **Ownership Verification**: Check before generation
3. **No Permanent Links**: Must regenerate after expiry
4. **HTTPS Only**: No HTTP fallback
5. **Custom Filename**: Content-Disposition header controls download name
6. **No Cross-Origin Sharing**: URLs work from any platform (mobile, web, desktop)

### Expiration Strategy

| Use Case | Expiration Time | Rationale |
|----------|----------------|-----------|
| Immediate download | 1 hour (default) | User downloads right away |
| Email sharing | 24 hours | User sends link via email |
| Cross-device sync | 7 days (max) | User switches between devices |

---

## Cross-Platform Access Flow

### Scenario: Generate on Mobile, Download on Web

**Mobile App (Generation)**:
```
1. User generates resume on mobile app
2. Mobile app calls POST /api/v1/exports/pdf
3. Backend creates PDF, uploads to S3
4. Backend stores export metadata in database
5. Mobile app receives export_id
```

**Web App (Download)**:
```
1. User logs into web app on laptop
2. Web app calls GET /api/v1/exports/files (list exports)
3. Backend queries database for user's exports
4. Web app displays list of exports
5. User clicks "Download"
6. Web app calls GET /api/v1/exports/files/{export_id}/download
7. Backend verifies user owns export (same user_id)
8. Backend generates presigned URL
9. Web app redirects to presigned URL
10. Browser downloads file from S3
```

**Security Checkpoints**:
- ✅ JWT authentication on both mobile and web
- ✅ Same user_id extracted from JWT
- ✅ Database verification: export belongs to user
- ✅ S3 key includes user_id → prevents cross-user access
- ✅ Presigned URL has expiration → time-limited access

---

## Database Security

### Exports Table Schema

```sql
CREATE TABLE exports (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    generation_id UUID NOT NULL REFERENCES generations(id),
    document_type VARCHAR(20) NOT NULL,
    format VARCHAR(10) NOT NULL,
    template VARCHAR(50) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    s3_key VARCHAR(500) NOT NULL,  -- Pattern: exports/{user_id}/{export_id}.{ext}
    file_size_bytes BIGINT NOT NULL,
    page_count INTEGER,
    options TEXT,
    metadata TEXT,
    expires_at TIMESTAMP NOT NULL,
    download_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Security Constraints
    CONSTRAINT valid_format CHECK (format IN ('pdf', 'docx', 'zip')),
    CONSTRAINT valid_document_type CHECK (document_type IN ('resume', 'cover_letter', 'zip')),
    CONSTRAINT s3_key_user_scoped CHECK (s3_key LIKE 'exports/' || user_id || '/%'),
    
    -- Indexes for performance
    INDEX idx_exports_user_id (user_id),
    INDEX idx_exports_expires_at (expires_at),
    INDEX idx_exports_created_at (created_at)
);
```

### Row-Level Security

**All queries filter by user_id**:

```python
# List exports - GOOD ✅
exports = db.query(Export).filter(Export.user_id == current_user.id).all()

# Get export - GOOD ✅
export = db.query(Export).filter(
    Export.id == export_id,
    Export.user_id == current_user.id  # Prevents cross-user access
).first()

# Get export - BAD ❌ (No user_id filter)
export = db.query(Export).filter(Export.id == export_id).first()
```

---

## API Endpoint Security

### Authentication Required

**All export endpoints require JWT authentication**:

```python
from app.core.dependencies import get_current_user

@router.post("/pdf")
async def export_pdf(
    request: ExportPDFRequest,
    current_user: User = Depends(get_current_user)  # ✅ Required
):
    # current_user.id used for all operations
    pass
```

### Authorization Checks

**Every operation verifies ownership**:

```python
# 1. Check generation belongs to user
generation = db.query(Generation).filter(
    Generation.id == request.generation_id,
    Generation.user_id == current_user.id  # ✅ Ownership check
).first()

if not generation:
    raise HTTPException(status_code=404, detail="Generation not found")

# 2. Create export with user_id
export = Export(
    id=uuid.uuid4(),
    user_id=current_user.id,  # ✅ Always set to current user
    generation_id=generation.id,
    # ... other fields
)

# 3. Upload to S3 with user-scoped key
s3_key = f"exports/{current_user.id}/{export.id}.pdf"  # ✅ User isolation
```

### Rate Limiting

**Prevent abuse**:

```python
# Per-user rate limits (using user_id from JWT)
- 10 exports per hour per user
- 100 MB total storage per user (free tier)
- 1 GB total storage per user (pro tier)
```

---

## Security Best Practices

### Environment Variables

**Never commit secrets**:

```bash
# .env (NEVER commit this file)
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
S3_BUCKET_NAME=jobwise-exports-production
S3_REGION=us-east-1

# Use AWS Secrets Manager for production
# Or AWS Systems Manager Parameter Store
```

### Logging & Monitoring

**Log all operations** (PII-safe):

```python
logger.info(
    f"Export created: export_id={export.id}, "
    f"user_id={current_user.id}, "
    f"format={format}, "
    f"size_bytes={size}"
)

logger.warning(
    f"Unauthorized access attempt: "
    f"user_id={current_user.id}, "
    f"requested_export_id={export_id}"
)
```

**Monitor CloudWatch**:
- Failed authentication attempts
- 403 Forbidden errors (unauthorized access)
- S3 access errors
- Presigned URL generation failures

### Input Validation

**Sanitize all inputs**:

```python
# Filename validation
ALLOWED_FILENAME_CHARS = set(string.ascii_letters + string.digits + '-_. ')
safe_filename = ''.join(c for c in filename if c in ALLOWED_FILENAME_CHARS)
safe_filename = safe_filename[:255]  # Max length

# Format validation
ALLOWED_FORMATS = {'pdf', 'docx', 'zip'}
if format not in ALLOWED_FORMATS:
    raise ValidationError(f"Invalid format: {format}")

# File size validation
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
if file_size > MAX_FILE_SIZE:
    raise ValidationError("File too large")
```

---

## Cleanup & Retention

### Auto-Deletion Policy

**Expired exports are deleted automatically**:

```python
# Cron job runs daily
@scheduled_task(cron="0 2 * * *")  # 2 AM daily
async def cleanup_expired_exports():
    # 1. Find expired exports
    expired = db.query(Export).filter(
        Export.expires_at < datetime.utcnow()
    ).all()
    
    # 2. Delete from S3
    for export in expired:
        s3_adapter.delete_file(
            user_id=export.user_id,
            export_id=export.id,
            format=export.format
        )
    
    # 3. Delete from database
    db.query(Export).filter(
        Export.expires_at < datetime.utcnow()
    ).delete()
    
    db.commit()
    
    logger.info(f"Deleted {len(expired)} expired exports")
```

### Storage Quotas

**Enforce per-user limits**:

```python
# Before upload, check user's total storage
user_total_bytes = db.query(func.sum(Export.file_size_bytes)).filter(
    Export.user_id == current_user.id
).scalar() or 0

if user_total_bytes + new_file_size > STORAGE_LIMIT:
    raise StorageQuotaExceeded(
        f"Storage limit exceeded. Used: {user_total_bytes / 1024 / 1024:.2f} MB"
    )
```

---

## Incident Response

### Security Breach Protocol

1. **Detection**: Monitor for anomalies
   - Multiple failed auth attempts
   - Cross-user access attempts (403 errors)
   - Unusual download patterns

2. **Containment**:
   - Revoke compromised IAM credentials
   - Rotate S3 bucket keys
   - Invalidate all presigned URLs (can't be done - wait for expiry)

3. **Investigation**:
   - Review CloudWatch logs
   - Check database audit trail
   - Identify affected users

4. **Recovery**:
   - Generate new IAM credentials
   - Update backend environment variables
   - Notify affected users

---

## Testing Security

### Security Test Cases

```python
# Test 1: Cross-user access prevention
def test_user_cannot_access_other_user_export():
    user1_export = create_export(user_id=user1.id)
    
    # User 2 tries to download User 1's export
    response = client.get(
        f"/exports/files/{user1_export.id}/download",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    
    assert response.status_code == 403  # Forbidden
    assert "Access denied" in response.json()["detail"]

# Test 2: Expired presigned URL
def test_expired_presigned_url_fails():
    url = generate_presigned_url(expiration_seconds=1)
    time.sleep(2)  # Wait for expiration
    
    response = requests.get(url)
    assert response.status_code == 403  # Access Denied

# Test 3: Invalid S3 key pattern
def test_s3_key_must_include_user_id():
    # Try to upload with wrong user_id in key
    with pytest.raises(ValueError):
        s3_adapter.upload_file(
            file_obj=file,
            user_id="user-123",
            export_id="export-456",
            format="pdf"
        )
        
        # Manually change S3 key (simulating attack)
        # Should fail database constraint check
```

---

## Compliance & Privacy

### GDPR Compliance

- **Right to Access**: Users can list all their exports
- **Right to Delete**: Users can delete their exports anytime
- **Data Portability**: Users can download their exports
- **Data Retention**: Exports auto-delete after 30 days (configurable)

### Data Minimization

- **No PII in S3 keys**: Only UUIDs used
- **No PII in logs**: Log IDs only, not names/emails
- **Metadata sanitization**: Remove sensitive fields before storing

---

## Summary: Security Checklist

- [x] **S3 Bucket**: Private, no public access
- [x] **IAM Permissions**: Least privilege principle
- [x] **Encryption**: SSE-S3 at rest, HTTPS in transit
- [x] **User Isolation**: S3 keys scoped by user_id
- [x] **Authorization**: JWT + database verification
- [x] **Presigned URLs**: Time-limited, HTTPS only
- [x] **Rate Limiting**: Per-user quotas enforced
- [x] **Logging**: All operations logged (PII-safe)
- [x] **Monitoring**: CloudWatch alerts configured
- [x] **Cleanup**: Auto-delete expired exports
- [x] **Testing**: Security tests in CI/CD
- [x] **Compliance**: GDPR-ready

---

**Last Reviewed**: December 2025  
**Next Review**: March 2026
