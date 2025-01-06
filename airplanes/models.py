import math
from django.db import models


class Airplane(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    passengers = models.PositiveIntegerField(default=0)

    @property
    def fuel_tank_capacity(self) -> float:
        return 200 * self.id

    @property
    def base_fuel_consumption(self) -> float:
        return math.log(self.id) * 0.80

    @property
    def total_fuel_consumption(self) -> float:
        return self.base_fuel_consumption + (self.passengers * 0.002)

    @property
    def max_flight_minutes(self) -> float:
        return self.fuel_tank_capacity / self.total_fuel_consumption
