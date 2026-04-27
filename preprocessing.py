import cv2
import numpy as np

def preprocess_image(image_path):
    """Load image and apply all preprocessing steps."""
    
    # Load image
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Remove noise
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    
    # Fix contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    
    # Deskew (fix rotation)
    deskewed = deskew_image(enhanced)
    
    # Binarize (black and white)
    _, binary = cv2.threshold(
        deskewed, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    
    return binary


def deskew_image(image):
    """Fix rotated/tilted receipts."""
    try:
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = image.shape
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        return rotated
    except Exception:
        return image  # return original if deskew fails