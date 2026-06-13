class Disease:
    def __init__(self, name, infection_rate, mortality_rate,
                 incubation_days, recovery_days):
        self.name = name
        self.infection_rate = infection_rate
        self.mortality_rate = mortality_rate
        self.incubation_days = incubation_days
        self.recovery_days = recovery_days