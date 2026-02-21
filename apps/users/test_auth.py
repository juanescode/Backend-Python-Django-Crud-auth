from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status


class AuthenticationAPITest(APITestCase):
    """Tests para los endpoints de autenticación"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser1',
            'email': 'test1@example.com',
            'password': 'testpass123'
        }
        
    def test_user_registration(self):
        """Verificar registro de nuevo usuario"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post('/api/auth/register/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(User.objects.count(), 1)
        
    def test_user_registration_duplicate_username(self):
        """Verificar que no se puede registrar username duplicado"""
        User.objects.create_user(**self.user_data)
        
        data = {**self.user_data, 'password2': 'testpass123'}
        response = self.client.post('/api/auth/register/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_user_registration_duplicate_email(self):
        """Verificar que no se puede registrar email duplicado"""
        first_user = {
            'username': 'firstuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        self.client.post('/api/auth/register/', first_user)
        
        duplicate_data = {
            'username': 'newuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        
        response = self.client.post('/api/auth/register/', duplicate_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
    def test_user_registration_missing_fields(self):
        """Verificar validación de campos requeridos"""
        response = self.client.post('/api/auth/register/', {
            'username': 'testuser1'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_user_login(self):
        """Verificar login de usuario existente"""
        User.objects.create_user(**self.user_data)
        
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser1',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
    def test_user_login_wrong_password(self):
        """Verificar rechazo con contraseña incorrecta"""
        User.objects.create_user(**self.user_data)
        
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser1',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_user_login_nonexistent_user(self):
        """Verificar rechazo con usuario inexistente"""
        response = self.client.post('/api/auth/login/', {
            'username': 'nonexistent',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_jwt_token_authentication(self):
        """Verificar que el token JWT funciona para endpoints protegidos"""
        User.objects.create_user(**self.user_data)
        
        login_response = self.client.post('/api/auth/login/', {
            'username': 'testuser1',
            'password': 'testpass123'
        })
        
        token = login_response.data['access']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/tasks/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
