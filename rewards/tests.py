from django.test import TestCase, Client
from django.urls import reverse
from .models import Reward, Rewarded


class RewardModelTest(TestCase):
    def setUp(self):
        self.reward = Reward.objects.create(
            name='Test Reward',
            description='Test Description',
            points_required=100,
            is_active=True
        )

    def test_reward_creation(self):
        self.assertEqual(self.reward.name, 'Test Reward')
        self.assertEqual(self.reward.points_required, 100)
        self.assertTrue(self.reward.is_active)

    def test_reward_str(self):
        self.assertEqual(str(self.reward), 'Test Reward')


class RewardedModelTest(TestCase):
    def setUp(self):
        self.reward = Reward.objects.create(
            name='Test Reward',
            points_required=100
        )
        self.rewarded = Rewarded.objects.create(
            reward=self.reward,
            user_name='Test User',
            user_email='test@example.com',
            points_used=100,
            status='pending'
        )

    def test_rewarded_creation(self):
        self.assertEqual(self.rewarded.user_name, 'Test User')
        self.assertEqual(self.rewarded.points_used, 100)
        self.assertEqual(self.rewarded.status, 'pending')

    def test_rewarded_str(self):
        expected = f"{self.rewarded.user_name} - {self.reward.name}"
        self.assertEqual(str(self.rewarded), expected)


class RewardViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.reward = Reward.objects.create(
            name='Test Reward',
            points_required=100
        )

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rewarded/index.html')

    def test_add_reward_view(self):
        response = self.client.get(reverse('add_reward'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rewarded/add_reward.html')
