import os
from django.core.exceptions import ValidationError
from PIL import Image


def validate_image_file(image):
    """
    Validates uploaded images:
    - Maximum file size: 2 MB
    - Allowed extensions: .jpg, .jpeg, .png, .webp
    - Verified image format via Pillow
    """
    if not image:
        return

    max_size_mb = 2
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Image file size must not exceed {max_size_mb} MB.")

    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    ext = os.path.splitext(image.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(f"Unsupported image format ({ext}). Allowed formats: JPG, PNG, WEBP.")

    # Reset file pointer and verify using Pillow
    try:
        if hasattr(image, 'seek'):
            image.seek(0)
        img = Image.open(image)
        img.verify()
        if img.format.lower() not in ['jpeg', 'png', 'webp']:
            raise ValidationError("Unsupported image file format. Only JPG, PNG, and WEBP images are permitted.")
        if hasattr(image, 'seek'):
            image.seek(0)
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError("Uploaded file is not a valid or readable image.")

