from django.test import TestCase
from django.contrib.auth.models import User
from apps.tasks.models import Task


class TaskModelTest(TestCase):
    """Tests para el modelo Task"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.user = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        
    def test_create_task(self):
        """Verificar que se puede crear una tarea correctamente"""
        task = Task.objects.create(
            user=self.user,
            title='Test Task',
            description='Test Description',
            completed=False
        )
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.description, 'Test Description')
        self.assertEqual(task.user, self.user)
        self.assertFalse(task.completed)
        
    def test_task_str_representation(self):
        """Verificar representación en string del modelo"""
        task = Task.objects.create(
            user=self.user,
            title='Test Task'
        )
        self.assertEqual(str(task), 'Test Task')
        
    def test_task_default_values(self):
        """Verificar valores por defecto del modelo"""
        task = Task.objects.create(
            user=self.user,
            title='Test Task'
        )
        self.assertFalse(task.completed)
        self.assertIsNotNone(task.created_at)
        self.assertIsNotNone(task.updated_at)
        
    def test_task_updated_at_changes(self):
        """Verificar que updated_at se actualiza"""
        task = Task.objects.create(
            user=self.user,
            title='Original Title'
        )
        original_updated_at = task.updated_at
        
        task.title = 'Updated Title'
        task.save()
        
        self.assertNotEqual(task.updated_at, original_updated_at)
        
    def test_task_cascade_delete_on_user_delete(self):
        """Verificar que las tareas se eliminan cuando se elimina el usuario"""
        Task.objects.create(user=self.user, title='Task 1')
        Task.objects.create(user=self.user, title='Task 2')
        
        self.assertEqual(Task.objects.filter(user=self.user).count(), 2)
        
        self.user.delete()
        
        self.assertEqual(Task.objects.count(), 0)
