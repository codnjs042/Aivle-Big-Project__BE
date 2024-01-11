from django.core.exceptions import ValidationError
import os

def AudioFileValidator(value):
    ext = os.path.splitext(value.name)[1]  # 파일 확장자 가져오기
    valid_extensions = ['.webm', '.wav']
    if not ext.lower() in valid_extensions:  # 소문자로 비교
        raise ValidationError('올바른 음성 파일 형식이 아닙니다.')