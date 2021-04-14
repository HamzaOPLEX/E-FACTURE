from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings
settings.configure(AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
])
username = input('Enter Username :')
passwd = input('Enter Password :')
password = make_password(passwd)
print(password)