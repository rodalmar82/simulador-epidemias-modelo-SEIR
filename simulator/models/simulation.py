# models/simulation.py  —  Modelo SEIR (antes SIR)
#
# CAMBIO PRINCIPAL: se añade el compartimento E (Expuesto).
# Una persona susceptible que se infecta pasa primero a Expuesta
# durante `incubation_days` días antes de volverse Infectada contagiosa.
# Esto usa el campo `incubation_days` de Disease que antes se ignoraba.

import pandas as pd
import numpy as np


class Simulation:
    def __init__(self, disease, population_df, mobility_df):
        self.disease = disease
        self.population_df = population_df
        self.mobility_df = mobility_df
        self.results = pd.DataFrame()

    def run(self, days=60, initial_region="MAD", initial_infected=10):
        regions = {}
        for _, row in self.population_df.iterrows():
            rid = str(row["region_id"])
            pop = row["population"]
            if rid == str(initial_region):
                regions[rid] = {
                    "susceptible": pop - initial_infected,
                    "exposed":     initial_infected,   # <-- nuevo compartimento
                    "infected":    0,
                    "recovered":   0,
                    "dead":        0,
                }
            else:
                regions[rid] = {
                    "susceptible": pop,
                    "exposed":     0,
                    "infected":    0,
                    "recovered":   0,
                    "dead":        0,
                }

        self.save_day(regions, 0)

        for day in range(1, days + 1):
            regions = self.step(regions, day)
            self.save_day(regions, day)

    def step(self, regions, day):
        new_regions = {rid: data.copy() for rid, data in regions.items()}

        # 1. Movilidad — igual que antes, pero también movemos Expuestos
        for _, row in self.mobility_df.iterrows():
            from_r = str(row["from_region"])
            to_r   = str(row["to_region"])
            rate   = row["mobility_rate"]

            if from_r in new_regions and to_r in new_regions:
                moving_infected = int(new_regions[from_r]["infected"] * rate)
                if moving_infected > 0:
                    new_regions[from_r]["infected"] -= moving_infected
                    new_regions[to_r]["infected"]   += moving_infected

                # Los expuestos también viajan
                moving_exposed = int(new_regions[from_r]["exposed"] * rate)
                if moving_exposed > 0:
                    new_regions[from_r]["exposed"] -= moving_exposed
                    new_regions[to_r]["exposed"]   += moving_exposed

        # 2. Proceso epidemiológico SEIR
        beta  = self.disease.infection_rate
        # sigma: tasa de paso de Expuesto a Infectado (1 / período de incubación)
        sigma = 1.0 / max(1, self.disease.incubation_days)
        # gamma: tasa de recuperación (1 / días de recuperación)
        gamma = 1.0 / max(1, self.disease.recovery_days)

        for rid, data in new_regions.items():
            pop_row = self.population_df[self.population_df["region_id"] == rid]
            if pop_row.empty:
                continue

            N = pop_row.iloc[0]["population"]
            S = data["susceptible"]
            E = data["exposed"]
            I = data["infected"]

            # S → E: nuevas exposiciones (depende de S e I, igual que antes)
            new_exposed   = int(beta * I * S / max(1, N))
            new_exposed   = min(new_exposed, int(S))

            # E → I: expuestos que se vuelven infecciosos tras incubación
            new_infectious = int(sigma * E)
            new_infectious = min(new_infectious, int(E))

            # I → R o D
            new_deaths     = int(I * self.disease.mortality_rate)
            new_recoveries = int((I - new_deaths) * gamma)
            new_deaths     = min(new_deaths,     int(I))
            new_recoveries = min(new_recoveries, max(0, int(I) - new_deaths))

            data["susceptible"] -= new_exposed
            data["exposed"]     += new_exposed  - new_infectious
            data["infected"]    += new_infectious - new_recoveries - new_deaths
            data["recovered"]   += new_recoveries
            data["dead"]        += new_deaths

            for key in ["susceptible", "exposed", "infected", "recovered", "dead"]:
                data[key] = max(0, data[key])

        return new_regions

    def save_day(self, regions, day):
        day_data = []
        for rid, data in regions.items():
            day_data.append({
                "day":         day,
                "region_id":   rid,
                "susceptible": int(data["susceptible"]),
                "exposed":     int(data["exposed"]),    # <-- nuevo campo en resultados
                "infected":    int(data["infected"]),
                "recovered":   int(data["recovered"]),
                "dead":        int(data["dead"]),
            })

        day_df = pd.DataFrame(day_data)
        self.results = pd.concat([self.results, day_df], ignore_index=True)
