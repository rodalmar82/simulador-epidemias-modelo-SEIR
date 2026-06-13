# models/metrics.py
#
# CAMBIO: R0 renombrado a Rt (número de reproducción efectivo).
# R0 es una constante de la enfermedad al inicio de la epidemia.
# Lo que calculamos aquí varía cada día según el estado de la población,
# por eso se llama correctamente Rt (R en el tiempo t).

import numpy as np
import pandas as pd


class EpidemicMetrics:

    @staticmethod
    def calculate_rt(results_df):
        """
        Calcula el número de reproducción efectivo Rt.

        Rt = nuevos infecciosos en el día t / expuestos del día anterior
        Un Rt > 1 significa que la epidemia crece; Rt < 1 que decrece.
        """
        resultados = results_df.copy()

        # Nuevos infecciosos = incremento de infected + dead + recovered
        # (todos salieron algún día del compartimento Infected)
        # Aproximación práctica: diff de (infected + recovered + dead)
        resultados["total_cases"] = (
            resultados["infected"] + resultados["recovered"] + resultados["dead"]
        )
        resultados["new_infectious"] = (
            resultados.groupby("region_id")["total_cases"]
            .diff()
            .fillna(0)
            .clip(lower=0)
        )

        rt_por_dia = []
        for dia in range(1, resultados["day"].max() + 1):
            datos_dia      = resultados[resultados["day"] == dia]
            datos_dia_ant  = resultados[resultados["day"] == dia - 1]

            nuevos       = datos_dia["new_infectious"].sum()
            expuestos_ant = datos_dia_ant["exposed"].sum() if "exposed" in datos_dia_ant.columns else 0

            if expuestos_ant > 0:
                rt_por_dia.append(nuevos / expuestos_ant)
            elif datos_dia_ant["infected"].sum() > 0:
                # Fallback para compatibilidad con resultados SIR sin columna exposed
                rt_por_dia.append(nuevos / datos_dia_ant["infected"].sum())

        if not rt_por_dia:
            return {
                "rt_promedio":   0,
                "rt_max":        0,
                "rt_min":        0,
                "rt_ultimo_dia": 0,
                "interpretacion": "Sin datos suficientes",
                "color": "gray",
            }

        rt_promedio = np.mean(rt_por_dia)

        if rt_promedio < 0.5:
            interpretacion = "🟢 Epidemia en fuerte declive"
            color = "green"
        elif rt_promedio < 0.8:
            interpretacion = "🟢 Epidemia en declive"
            color = "lightgreen"
        elif rt_promedio < 1.0:
            interpretacion = "🟡 Cerca de la estabilidad"
            color = "yellow"
        elif rt_promedio < 1.2:
            interpretacion = "🟠 Propagación leve"
            color = "orange"
        elif rt_promedio < 1.5:
            interpretacion = "🔴 Propagación moderada"
            color = "darkorange"
        elif rt_promedio < 2.0:
            interpretacion = "🔴 Propagación alta"
            color = "red"
        elif rt_promedio < 3.0:
            interpretacion = "⚫ Propagación muy alta"
            color = "darkred"
        else:
            interpretacion = "⚫ Propagación explosiva"
            color = "black"

        return {
            "rt_promedio":    round(rt_promedio, 2),
            "rt_max":         round(np.max(rt_por_dia), 2),
            "rt_min":         round(np.min(rt_por_dia), 2),
            "rt_ultimo_dia":  round(rt_por_dia[-1], 2),
            "interpretacion": interpretacion,
            "color":          color,
        }

    @staticmethod
    def calculate_cfr(results_df):
        """Tasa de letalidad (CFR). Sin cambios."""
        ultimo_dia = results_df[results_df["day"] == results_df["day"].max()]

        if ultimo_dia.empty:
            return {
                "cfr_global": 0, "clasificacion": "Sin datos",
                "color": "gray", "total_muertos": 0, "total_casos": 0,
            }

        total_muertos = ultimo_dia["dead"].sum()
        total_casos   = (
            ultimo_dia["infected"].sum()
            + ultimo_dia["recovered"].sum()
            + total_muertos
        )
        cfr_global = (total_muertos / max(1, total_casos)) * 100

        if cfr_global < 0.1:
            clasificacion, color = "🟢 Letalidad muy baja (<0.1%)",          "green"
        elif cfr_global < 0.5:
            clasificacion, color = "🟢 Letalidad baja (0.1-0.5%)",           "lightgreen"
        elif cfr_global < 1.0:
            clasificacion, color = "🟡 Letalidad moderada (0.5-1%)",         "yellow"
        elif cfr_global < 2.0:
            clasificacion, color = "🟠 Letalidad media (1-2%)",              "orange"
        elif cfr_global < 5.0:
            clasificacion, color = "🔴 Letalidad alta (2-5%)",               "red"
        elif cfr_global < 10.0:
            clasificacion, color = "🔴 Letalidad muy alta (5-10%)",          "darkred"
        else:
            clasificacion, color = "⚫ Letalidad extremadamente alta (>10%)", "black"

        cfr_por_pais = {}
        for _, row in ultimo_dia.nlargest(10, "dead").iterrows():
            total_pais = row["infected"] + row["recovered"] + row["dead"]
            if total_pais > 0:
                cfr_por_pais[row["region_id"]] = round(
                    (row["dead"] / total_pais) * 100, 2
                )

        return {
            "cfr_global":    round(cfr_global, 2),
            "cfr_por_pais":  cfr_por_pais,
            "clasificacion": clasificacion,
            "color":         color,
            "total_muertos": int(total_muertos),
            "total_casos":   int(total_casos),
        }

    @staticmethod
    def calculate_spread_speed(results_df):
        """Velocidad de propagación geográfica. Sin cambios."""
        afectados = results_df[results_df["infected"] > 0].copy()
        if afectados.empty:
            return {
                "paises_afectados_dia_1": 0, "paises_afectados_final": 0,
                "velocidad_paises_por_dia": 0,
                "dias_para_50_paises": "N/A", "dias_para_100_paises": "N/A",
            }

        afectados_por_dia = (
            afectados.groupby("day")
            .agg(paises_afectados=("region_id", "nunique"))
            .reset_index()
        )

        if len(afectados_por_dia) < 2:
            v = afectados_por_dia.iloc[-1]["paises_afectados"] if len(afectados_por_dia) else 0
            return {
                "paises_afectados_dia_1": int(v), "paises_afectados_final": int(v),
                "velocidad_paises_por_dia": 0,
                "dias_para_50_paises": "N/A", "dias_para_100_paises": "N/A",
            }

        paises_inicial = afectados_por_dia.iloc[0]["paises_afectados"]
        paises_final   = afectados_por_dia.iloc[-1]["paises_afectados"]
        dias_totales   = afectados_por_dia.iloc[-1]["day"] - afectados_por_dia.iloc[0]["day"]
        velocidad      = (paises_final - paises_inicial) / max(1, dias_totales)

        dias_para_50 = dias_para_100 = "N/A"
        for _, row in afectados_por_dia.iterrows():
            if row["paises_afectados"] >= 50  and dias_para_50  == "N/A":
                dias_para_50  = row["day"]
            if row["paises_afectados"] >= 100 and dias_para_100 == "N/A":
                dias_para_100 = row["day"]

        return {
            "paises_afectados_dia_1":  int(paises_inicial),
            "paises_afectados_final":  int(paises_final),
            "velocidad_paises_por_dia": round(velocidad, 2),
            "dias_para_50_paises":     dias_para_50,
            "dias_para_100_paises":    dias_para_100,
        }

    @staticmethod
    def calculate_peak_day(results_df):
        """Día pico de la epidemia. Sin cambios."""
        datos_globales = results_df.groupby("day")["infected"].sum().reset_index()
        pico = datos_globales.loc[datos_globales["infected"].idxmax()]
        return {
            "dia_pico":         int(pico["day"]),
            "infectados_pico":  int(pico["infected"]),
        }

    @staticmethod
    def get_all_metrics(results_df):
        return {
            "rt":           EpidemicMetrics.calculate_rt(results_df),
            "cfr":          EpidemicMetrics.calculate_cfr(results_df),
            "spread_speed": EpidemicMetrics.calculate_spread_speed(results_df),
            "peak":         EpidemicMetrics.calculate_peak_day(results_df),
        }
