from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Airplane
import math
from .serializers import AirplaneSerializer
from rest_framework.exceptions import ValidationError


class AirplaneTestCase(TestCase):
    def setUp(self):

        Airplane.objects.all().delete()
        self.client = APIClient()
        self.airplane1 = Airplane.objects.create(id=1, passengers=50)
        self.airplane2 = Airplane.objects.create(id=2, passengers=100)

    def test_fuel_tank_capacity(self):
        """Test fuel tank capacity calculation."""
        self.assertEqual(self.airplane1.fuel_tank_capacity, 200)
        self.assertEqual(self.airplane2.fuel_tank_capacity, 400)

    def test_base_fuel_consumption(self):
        """Test base fuel consumption calculation."""
        self.assertAlmostEqual(self.airplane1.base_fuel_consumption, math.log(1) * 0.80, places=5)
        self.assertAlmostEqual(self.airplane2.base_fuel_consumption, math.log(2) * 0.80, places=5)

    def test_total_fuel_consumption(self):
        """Test total fuel consumption calculation."""
        self.assertAlmostEqual(
            self.airplane1.total_fuel_consumption,
            self.airplane1.base_fuel_consumption + (50 * 0.002),
            places=5
        )
        self.assertAlmostEqual(
            self.airplane2.total_fuel_consumption,
            self.airplane2.base_fuel_consumption + (100 * 0.002),
            places=5
        )

    def test_max_flight_minutes(self):
        """Test maximum flight duration calculation."""
        self.assertAlmostEqual(
            self.airplane1.max_flight_minutes,
            self.airplane1.fuel_tank_capacity / self.airplane1.total_fuel_consumption,
            places=2
        )
        self.assertAlmostEqual(
            self.airplane2.max_flight_minutes,
            self.airplane2.fuel_tank_capacity / self.airplane2.total_fuel_consumption,
            places=2
        )

    def test_edge_case_airplane_id_1(self):
        """Test calculations for airplane with ID 1 (minimum valid ID)."""
        airplane = Airplane.objects.get(id=1)
        self.assertEqual(airplane.fuel_tank_capacity, 200)
        self.assertAlmostEqual(airplane.base_fuel_consumption, 0.0, places=5)
        self.assertAlmostEqual(airplane.total_fuel_consumption, 50 * 0.002, places=5)
        self.assertAlmostEqual(airplane.max_flight_minutes, 200 / (50 * 0.002), places=2)

    def test_edge_case_high_passenger_count(self):
        """Test calculations for airplane with a high passenger count."""
        airplane = Airplane.objects.create(id=5, passengers=10000)
        self.assertAlmostEqual(
            airplane.total_fuel_consumption,
            airplane.base_fuel_consumption + (10000 * 0.002),
            places=5
        )
        self.assertGreater(airplane.total_fuel_consumption, 20.0)

    def test_edge_case_large_airplane_id(self):
        """Test calculations for airplane with a very large ID."""
        airplane = Airplane.objects.create(id=1000000, passengers=10)
        self.assertEqual(airplane.fuel_tank_capacity, 200 * 1000000)
        self.assertAlmostEqual(airplane.base_fuel_consumption, math.log(1000000) * 0.80, places=5)
        self.assertGreater(airplane.max_flight_minutes, 1000.0)

    def test_edge_case_zero_passengers(self):
        """Test calculations for airplane with zero passengers."""
        airplane = Airplane.objects.create(id=10, passengers=0)
        self.assertAlmostEqual(airplane.total_fuel_consumption, airplane.base_fuel_consumption, places=5)
        self.assertGreater(airplane.max_flight_minutes, 0.0)

    def test_invalid_airplane_id(self):
        """Test airplane creation with invalid ID."""
        with self.assertRaises(Exception):
            Airplane.objects.create(id=-1, passengers=10)

    def test_api_create_airplane(self):
        """Test creating an airplane via API."""
        response = self.client.post(
            '/api/airplanes/',
            {"id": 3, "passengers": 75},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['id'], 3)
        self.assertEqual(response.data['passengers'], 75)

        # Recalculate expected values
        base_consumption = math.log(3) * 0.80
        additional_consumption = 75 * 0.002
        total_consumption = base_consumption + additional_consumption
        max_minutes = (200 * 3) / total_consumption

        self.assertEqual(response.data['total_fuel_consumption_per_minute'], f"{total_consumption:.3f} liters")
        self.assertEqual(response.data['max_flight_minutes'], f"{max_minutes:.2f} minutes")

    def test_api_list_airplanes(self):
        """Test listing airplanes via API."""
        response = self.client.get('/api/airplanes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate airplane1
        airplane1 = response.data[0]
        base_consumption1 = math.log(1) * 0.80
        additional_consumption1 = 50 * 0.002
        total_consumption1 = base_consumption1 + additional_consumption1
        max_minutes1 = (200 * 1) / total_consumption1
        self.assertEqual(airplane1['id'], 1)
        self.assertEqual(airplane1['total_fuel_consumption_per_minute'], f"{total_consumption1:.3f} liters")
        self.assertEqual(airplane1['max_flight_minutes'], f"{max_minutes1:.2f} minutes")

        # Validate airplane2
        airplane2 = response.data[1]
        base_consumption2 = math.log(2) * 0.80
        additional_consumption2 = 100 * 0.002
        total_consumption2 = base_consumption2 + additional_consumption2
        max_minutes2 = (200 * 2) / total_consumption2
        self.assertEqual(airplane2['id'], 2)
        self.assertEqual(airplane2['total_fuel_consumption_per_minute'], f"{total_consumption2:.3f} liters")
        self.assertEqual(airplane2['max_flight_minutes'], f"{max_minutes2:.2f} minutes")

    def test_api_high_volume_airplanes(self):
        """Test creating a high number of airplanes."""
        for i in range(3, 10):
            response = self.client.post(
                '/api/airplanes/',
                {"id": i, "passengers": i * 10},
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get('/api/airplanes/')
        self.assertEqual(len(response.data), 9)

    def test_api_create_invalid_airplane_id(self):
        """Test creating an airplane with an invalid ID."""
        response = self.client.post('/api/airplanes/', {"id": -1, "passengers": 50}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Airplane ID must be a positive integer.", response.data['id'])

    def test_api_create_negative_passengers(self):
        """Test creating an airplane with negative passengers."""
        response = self.client.post('/api/airplanes/', {"id": 5, "passengers": -10}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Passenger count cannot be negative.", response.data['passengers'])

    def test_api_list_no_airplanes(self):
        """Test listing airplanes when no airplanes exist."""
        Airplane.objects.all().delete()
        response = self.client.get('/api/airplanes/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("No airplanes found.", response.data['message'])

    def test_validate_id_positive(self):
        """Test validation for a valid airplane ID."""
        serializer = AirplaneSerializer()
        valid_id = serializer.validate_id(3)
        self.assertEqual(valid_id, 3)

    def test_validate_id_negative(self):
        """Test validation for an invalid airplane ID (negative value)."""
        serializer = AirplaneSerializer()
        with self.assertRaises(ValidationError) as context:
            serializer.validate_id(-1)
        self.assertEqual(str(context.exception.detail[0]), "Airplane ID must be a positive integer.")

    def test_validate_id_zero(self):
        """Test validation for an invalid airplane ID (zero)."""
        serializer = AirplaneSerializer()
        with self.assertRaises(ValidationError) as context:
            serializer.validate_id(0)
        self.assertEqual(str(context.exception.detail[0]), "Airplane ID must be a positive integer.")

    def test_validate_passengers_positive(self):
        """Test validation for a valid passenger count."""
        serializer = AirplaneSerializer()
        valid_passengers = serializer.validate_passengers(50)
        self.assertEqual(valid_passengers, 50)

    def test_validate_passengers_negative(self):
        """Test validation for an invalid passenger count (negative value)."""
        serializer = AirplaneSerializer()
        with self.assertRaises(ValidationError) as context:
            serializer.validate_passengers(-10)
        self.assertEqual(str(context.exception.detail[0]), "Passenger count cannot be negative.")
