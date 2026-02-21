from django.contrib.auth.models import User
from django.test import TestCase
from apps.tasks.models import Task
from apps.tasks.serializers import TaskSerializer


class TaskSerializerTest(TestCase):
    """Tests para el serializer de Task"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.user = User.objects.create_user(
            username='testuser1',
            email='test@example.com',
            password='testpass123'
        )
        self.task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'completed': False
        }
        
    def test_task_serializer_with_valid_data(self):
        """Verificar serialización con datos válidos"""
        serializer = TaskSerializer(data=self.task_data)
        self.assertTrue(serializer.is_valid())
        
    def test_task_serializer_missing_title(self):
        """Verificar que title es requerido"""
        data = {
            'description': 'Test Description',
            'completed': False
        }
        serializer = TaskSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
        
    def test_task_serializer_with_empty_title(self):
        """Verificar que title no puede estar vacío"""
        data = {
            'title': '',
            'description': 'Test Description'
        }
        serializer = TaskSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        
    def test_task_serializer_optional_description(self):
        """Verificar que description es opcional"""
        data = {
            'title': 'Test Task'
        }
        serializer = TaskSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
    def test_task_serializer_contains_expected_fields(self):
        """Verificar que el serializer contiene los campos esperados"""
        task = Task.objects.create(user=self.user, **self.task_data)
        serializer = TaskSerializer(task)
        
        expected_fields = {'id', 'title', 'description', 'completed', 'created_at', 'updated_at'}
        self.assertEqual(set(serializer.data.keys()), expected_fields)
        
    def test_task_serializer_read_only_fields(self):
        """Verificar que created_at y updated_at son read-only"""
        task = Task.objects.create(user=self.user, **self.task_data)
        serializer = TaskSerializer(task)
        
        self.assertIn('created_at', serializer.data)
        self.assertIn('updated_at', serializer.data)
