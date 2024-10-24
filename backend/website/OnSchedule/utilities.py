from django.contrib.auth.models import User

def save_user(user_data):
    username = user_data.get('username')
    email = user_data.get('email')
    password = user_data.get('password')

    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()

