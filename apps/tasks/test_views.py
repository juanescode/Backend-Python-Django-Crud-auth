from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.tasks.models import Task


class TaskAPITest(APITestCase):
    """Tests para los endpoints de la API de Tasks"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
    def get_auth_token(self, username='testuser1', password='testpass123'):
        """Helper para obtener token JWT"""
        response = self.client.post('/api/auth/login/', {
            'username': username,
            'password': password
        })
        return response.data['access']
    
    def test_list_tasks_requires_authentication(self):
        """Verificar que listar tareas requiere autenticación"""
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_create_task_requires_authentication(self):
        """Verificar que crear tarea requiere autenticación"""
        response = self.client.post('/api/tasks/', {
            'title': 'Test Task',
            'description': 'Test Description'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_create_task_authenticated(self):
        """Verificar creación de tarea con autenticación"""
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.post('/api/tasks/', {
            'title': 'New Task',
            'description': 'Task Description',
            'completed': False
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Task')
        self.assertEqual(response.data['description'], 'Task Description')
        self.assertEqual(Task.objects.count(), 1)
        
    def test_create_task_without_description(self):
        """Verificar que se puede crear tarea sin descripción"""
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.post('/api/tasks/', {
            'title': 'Task without description'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # description puede ser None o vacío, ambos son válidos
        self.assertIn(response.data['description'], [None, ''])
        
    def test_list_tasks_only_user_tasks(self):
        """Verificar que solo se listan tareas del usuario autenticado"""
        Task.objects.create(user=self.user, title='User Task')
        Task.objects.create(user=self.other_user, title='Other User Task')
        
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.get('/api/tasks/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'User Task')
        
    def test_retrieve_task_detail(self):
        """Verificar obtención de detalle de tarea"""
        task = Task.objects.create(
            user=self.user,
            title='Test Task',
            description='Test Description'
        )
        
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.get(f'/api/tasks/{task.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Task')
        
    def test_update_task_partial(self):
        """Verificar actualización parcial de tarea (PATCH)"""
        task = Task.objects.create(
            user=self.user,
            title='Original Title',
            description='Original Description',
            completed=False
        )
        
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.patch(f'/api/tasks/{task.id}/', {
            'completed': True
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['completed'])
        self.assertEqual(response.data['title'], 'Original Title')
        
    def test_update_task_complete(self):
        """Verificar actualización completa de tarea (PUT)"""
        task = Task.objects.create(
            user=self.user,
            title='Original Title',
            completed=False
        )
        
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.put(f'/api/tasks/{task.id}/', {
            'title': 'Updated Title',
            'description': 'Updated Description',
            'completed': True
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')
        self.assertTrue(response.data['completed'])
        
    def test_cannot_update_other_user_task(self):
        """Verificar que no se puede actualizar tarea de otro usuario"""
        task = Task.objects.create(
            user=self.other_user,
            title='Other User Task'
        )
        
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.patch(f'/api/tasks/{task.id}/', {
            'title': 'Hacked Title'
        })
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_delete_task(self):
        """Verificar eliminación de tarea propia"""
        task = Task.objects.create(user=self.user, title='To Delete')
        
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.delete(f'/api/tasks/{task.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)
        
    def test_cannot_delete_other_user_task(self):
        """Verificar que no se puede eliminar tarea de otro usuario"""
        task = Task.objects.create(user=self.other_user, title='Protected Task')
        
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.delete(f'/api/tasks/{task.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Task.objects.count(), 1)
        
    def test_task_title_required(self):
        """Verificar que el título es requerido"""
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.post('/api/tasks/', {
            'description': 'Description without title'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
