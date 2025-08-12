from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Timeline, KeyPhoto, TimelineType
from datetime import datetime
import tempfile
import os

User = get_user_model()


class UserIsolationTestCase(APITestCase):
    """Test case for ensuring user data isolation"""
    
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
        
        # Create timeline types
        self.timeline_type = TimelineType.objects.create(name='Weight Tracking')
        
        # Create test data for user1
        self.timeline1 = Timeline.objects.create(
            user=self.user1,
            name='My Weight Journey'
        )
        
        self.keyphoto1 = KeyPhoto.objects.create(
            user=self.user1,
            filename='test_photo1.jpg',
            s3_path='users/1/user1/keyphotos/test_photo1.jpg',
            presigned_url='http://example.com/photo1.jpg',
            photo_taken_at=datetime.now(),
            weight_centigrams=750
        )
        
        # Create test data for user2
        self.timeline2 = Timeline.objects.create(
            user=self.user2,
            name='My Weight Journey'
        )
        
        self.keyphoto2 = KeyPhoto.objects.create(
            user=self.user2,
            filename='test_photo2.jpg',
            s3_path='users/2/user2/keyphotos/test_photo2.jpg',
            presigned_url='http://example.com/photo2.jpg',
            photo_taken_at=datetime.now(),
            weight_centigrams=800
        )
    
    def test_user_can_only_see_own_timelines(self):
        """Test that users can only see their own timelines"""
        # Login as user1
        self.client.force_authenticate(user=self.user1)
        
        # Get user1's timelines
        response = self.client.get(reverse('user-timelines'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only see user1's timeline
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'My Weight Journey')
        self.assertEqual(response.data[0]['user'], self.user1.id)
    
    def test_user_can_only_see_own_keyphotos(self):
        """Test that users can only see their own keyphotos"""
        # Login as user1
        self.client.force_authenticate(user=self.user1)
        
        # Get user1's keyphotos
        response = self.client.get(reverse('user-keyphotos'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only see user1's keyphoto
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['filename'], 'test_photo1.jpg')
        self.assertEqual(response.data[0]['user'], self.user1.id)
    
    def test_user_cannot_access_other_user_timeline(self):
        """Test that users cannot access other users' timelines"""
        # Login as user1
        self.client.force_authenticate(user=self.user1)
        
        # Try to access user2's timeline (should fail)
        response = self.client.get(f'/timelines/timeline/{self.timeline2.id}/')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_cannot_access_other_user_keyphoto(self):
        """Test that users cannot access other users' keyphotos"""
        # Login as user1
        self.client.force_authenticate(user=self.user1)
        
        # Try to access user2's keyphoto (should fail)
        response = self.client.get(f'/timelines/keyphoto/{self.keyphoto2.id}/')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_cannot_modify_other_user_data(self):
        """Test that users cannot modify other users' data"""
        # Login as user1
        self.client.force_authenticate(user=self.user1)
        
        # Try to delete user2's keyphoto (should fail)
        response = self.client.delete(f'/timelines/keyphoto/{self.keyphoto2.id}/')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the keyphoto still exists
        self.assertTrue(KeyPhoto.objects.filter(id=self.keyphoto2.id).exists())
    
    def test_new_timeline_gets_correct_user(self):
        """Test that new timelines are created with the correct user"""
        # Login as user1
        self.client.force_authenticate(user=self.user1)
        
        # Create new timeline
        data = {'name': 'New Test Timeline'}
        response = self.client.post(reverse('new-timeline'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify the timeline was created with user1
        timeline = Timeline.objects.get(name='New Test Timeline')
        self.assertEqual(timeline.user, self.user1)
    
    def test_unique_constraints(self):
        """Test that unique constraints work correctly"""
        # Try to create another timeline with the same name for user1
        with self.assertRaises(Exception):
            Timeline.objects.create(
                user=self.user1,
                name='My Weight Journey'  # Same name as existing
            )
        
        # But user2 can have a timeline with the same name
        timeline3 = Timeline.objects.create(
            user=self.user2,
            name='My Weight Journey'  # Same name, different user
        )
        self.assertIsNotNone(timeline3)
        
        # Try to create another keyphoto with the same filename for user1
        with self.assertRaises(Exception):
            KeyPhoto.objects.create(
                user=self.user1,
                filename='test_photo1.jpg',  # Same filename as existing
                s3_path='users/1/user1/keyphotos/test_photo1_duplicate.jpg',
                presigned_url='http://example.com/photo1_duplicate.jpg',
                photo_taken_at=datetime.now(),
                weight_centigrams=750
            )
        
        # But user2 can have a keyphoto with the same filename
        keyphoto3 = KeyPhoto.objects.create(
            user=self.user2,
            filename='test_photo1.jpg',  # Same filename, different user
            s3_path='users/2/user2/keyphotos/test_photo1.jpg',
            presigned_url='http://example.com/photo1_user2.jpg',
            photo_taken_at=datetime.now(),
            weight_centigrams=750
        )
        self.assertIsNotNone(keyphoto3)


class ModelTestCase(TestCase):
    """Test case for model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_timeline_str_representation(self):
        """Test Timeline string representation"""
        timeline = Timeline.objects.create(
            user=self.user,
            name='Test Timeline'
        )
        expected = f"{self.user.username} - Test Timeline"
        self.assertEqual(str(timeline), expected)
    
    def test_keyphoto_str_representation(self):
        """Test KeyPhoto string representation"""
        keyphoto = KeyPhoto.objects.create(
            user=self.user,
            filename='test.jpg',
            s3_path='users/1/testuser/keyphotos/test.jpg',
            presigned_url='http://example.com/test.jpg',
            photo_taken_at=datetime.now(),
            weight_centigrams=750
        )
        expected_start = f"{self.user.username} - KeyPhoto test.jpg"
        self.assertTrue(str(keyphoto).startswith(expected_start))
    
    def test_keyphoto_weight_properties(self):
        """Test KeyPhoto weight calculation properties"""
        keyphoto = KeyPhoto.objects.create(
            user=self.user,
            filename='test.jpg',
            s3_path='users/1/testuser/keyphotos/test.jpg',
            presigned_url='http://example.com/test.jpg',
            photo_taken_at=datetime.now(),
            weight_centigrams=750
        )
        
        self.assertEqual(keyphoto.weight_grams, 75.0)
        self.assertEqual(keyphoto.weight_kg, 0.75)
    
    def test_keyphoto_random_weight_generation(self):
        """Test KeyPhoto random weight generation"""
        weight = KeyPhoto.generate_random_weight()
        self.assertGreaterEqual(weight, 700)
        self.assertLessEqual(weight, 850)
