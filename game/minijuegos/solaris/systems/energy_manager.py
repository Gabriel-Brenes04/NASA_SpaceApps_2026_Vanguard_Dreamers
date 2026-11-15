from .. import settings as S


class EnergyManager:
    def __init__(self):
        self.battery = S.STARTING_BATTERY
        self.production = 0.0
        self.consumption = S.BASE_CONSUMPTION_KW
        self.total_generated = 0.0
        self.blackout = False

    def update(self, dt, production_kw):
        self.production = production_kw
        self.total_generated += production_kw * dt / 3600.0
        net = (production_kw - self.consumption) * dt / S.ENERGY_SCALE
        self.battery = max(0.0, min(S.BATTERY_CAPACITY, self.battery + net))
        self.blackout = self.battery <= 0.0
        return self.battery
