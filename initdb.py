# -*- coding: UTF-8 -*-
import os
import sys
import django
# https://www.cnblogs.com/duking1991/p/6121300.html
import random
import datetime


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myAPP.settings")
    django.setup()
    #print('===='+os.getcwd()) #当前目录
    from django.contrib.auth.models import User
    
    user = User.objects.create_superuser('admin', 'admin@test.com',
                                         '1234qazx')
    user.save()
    user = User.objects.create_user('wcl6005', 'wcl6005@test.com',
                                        '1234qazx')
    user.save()
    user = User.objects.create_user('test', 'wcl6005@test.com',
                                        '1234qazx')
    user.save()
    
    