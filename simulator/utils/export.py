import pandas as pd
import json
import csv

class ExportadorResultados:
    @staticmethod
    def a_csv(results_df, filename="resultados.csv"):
        """Exporta resultados a CSV"""
        results_df.to_csv(filename, index=False)
        return filename
    
    @staticmethod
    def a_json(results_df, filename="resultados.json"):
        """Exporta resultados a JSON"""
        results_df.to_json(filename, orient='records', indent=2)
        return filename
    
    @staticmethod
    def a_excel(results_df, filename="resultados.xlsx"):
        """Exporta resultados a Excel con múltiples hojas"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Hoja principal
            results_df.to_excel(writer, sheet_name='Resultados', index=False)
            
            # Resumen por día
            resumen_dia = results_df.groupby('day').agg({
                'infected': 'sum',
                'recovered': 'sum',
                'dead': 'sum'
            }).reset_index()
            resumen_dia.to_excel(writer, sheet_name='Resumen Diario', index=False)
            
            # Top países
            ultimo_dia = results_df[results_df['day'] == results_df['day'].max()]
            top_paises = ultimo_dia.nlargest(10, 'infected')[['region_id', 'infected', 'recovered', 'dead']]
            top_paises.to_excel(writer, sheet_name='Top Países', index=False)
        
        return filename
    
    @staticmethod
    def a_markdown(results_df, filename="resultados.md"):
        """Exporta resultados a Markdown para documentación"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Resultados de Simulación Epidemiológica\n\n")
            
            f.write("## Resumen Global\n")
            f.write(f"- Total días simulados: {results_df['day'].max()}\n")
            f.write(f"- Total infectados: {results_df[results_df['day'] == results_df['day'].max()]['infected'].sum():,}\n")
            f.write(f"- Total muertos: {results_df[results_df['day'] == results_df['day'].max()]['dead'].sum():,}\n\n")
            
            f.write("## Evolución Diaria\n")
            f.write("| Día | Infectados | Recuperados | Muertos |\n")
            f.write("|-----|------------|-------------|---------|\n")
            
            for dia in sorted(results_df['day'].unique()):
                datos = results_df[results_df['day'] == dia]
                f.write(f"| {dia} | {datos['infected'].sum():,} | {datos['recovered'].sum():,} | {datos['dead'].sum():,} |\n")
        
        return filename