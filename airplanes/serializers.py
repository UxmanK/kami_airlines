from rest_framework import serializers
from .models import Airplane


class AirplaneSerializer(serializers.ModelSerializer):
    total_fuel_consumption_per_minute = serializers.SerializerMethodField()
    max_flight_minutes = serializers.SerializerMethodField()

    class Meta:
        model = Airplane
        fields = ['id', 'passengers', 'total_fuel_consumption_per_minute', 'max_flight_minutes']

    def get_total_fuel_consumption_per_minute(self, obj):
        return f"{obj.total_fuel_consumption:.3f} liters"

    def get_max_flight_minutes(self, obj):
        return f"{obj.max_flight_minutes:.2f} minutes"

    def validate_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("Airplane ID must be a positive integer.")
        return value

    def validate_passengers(self, value):
        if value < 0:
            raise serializers.ValidationError("Passenger count cannot be negative.")
        return value
