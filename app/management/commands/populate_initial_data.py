from django.core.management.base import BaseCommand
from django.db import transaction
from app.models import Country, Indicator, WorldBankData, HappinessData
import requests
import json
import time

class Command(BaseCommand):
    help = 'Populate initial data for countries, indicators, and sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting initial data population...'))
        
        # Populate countries
        self.populate_countries()
        
        # Populate indicators
        self.populate_indicators()
        
        # Populate sample data
        self.populate_sample_data()
        
        self.stdout.write(self.style.SUCCESS('Initial data population completed!'))

    def populate_countries(self):
        """Populate countries with World Bank data"""
        self.stdout.write('Populating countries...')
        
        countries_data = [
            # Major economies and diverse regions
            {'code': 'US', 'name': 'United States', 'region': 'North America', 'income_group': 'High income'},
            {'code': 'CN', 'name': 'China', 'region': 'East Asia & Pacific', 'income_group': 'Upper middle income'},
            {'code': 'IN', 'name': 'India', 'region': 'South Asia', 'income_group': 'Lower middle income'},
            {'code': 'DE', 'name': 'Germany', 'region': 'Europe & Central Asia', 'income_group': 'High income'},
            {'code': 'JP', 'name': 'Japan', 'region': 'East Asia & Pacific', 'income_group': 'High income'},
            {'code': 'GB', 'name': 'United Kingdom', 'region': 'Europe & Central Asia', 'income_group': 'High income'},
            {'code': 'FR', 'name': 'France', 'region': 'Europe & Central Asia', 'income_group': 'High income'},
            {'code': 'BR', 'name': 'Brazil', 'region': 'Latin America & Caribbean', 'income_group': 'Upper middle income'},
            {'code': 'CA', 'name': 'Canada', 'region': 'North America', 'income_group': 'High income'},
            {'code': 'AU', 'name': 'Australia', 'region': 'East Asia & Pacific', 'income_group': 'High income'},
            {'code': 'RU', 'name': 'Russian Federation', 'region': 'Europe & Central Asia', 'income_group': 'Upper middle income'},
            {'code': 'KR', 'name': 'Korea, Rep.', 'region': 'East Asia & Pacific', 'income_group': 'High income'},
            {'code': 'MX', 'name': 'Mexico', 'region': 'Latin America & Caribbean', 'income_group': 'Upper middle income'},
            {'code': 'ID', 'name': 'Indonesia', 'region': 'East Asia & Pacific', 'income_group': 'Lower middle income'},
            {'code': 'TR', 'name': 'Turkey', 'region': 'Europe & Central Asia', 'income_group': 'Upper middle income'},
            {'code': 'SA', 'name': 'Saudi Arabia', 'region': 'Middle East & North Africa', 'income_group': 'High income'},
            {'code': 'AR', 'name': 'Argentina', 'region': 'Latin America & Caribbean', 'income_group': 'Upper middle income'},
            {'code': 'ZA', 'name': 'South Africa', 'region': 'Sub-Saharan Africa', 'income_group': 'Upper middle income'},
            {'code': 'EG', 'name': 'Egypt, Arab Rep.', 'region': 'Middle East & North Africa', 'income_group': 'Lower middle income'},
            {'code': 'NG', 'name': 'Nigeria', 'region': 'Sub-Saharan Africa', 'income_group': 'Lower middle income'},
            {'code': 'PK', 'name': 'Pakistan', 'region': 'South Asia', 'income_group': 'Lower middle income'},
            {'code': 'BD', 'name': 'Bangladesh', 'region': 'South Asia', 'income_group': 'Lower middle income'},
            {'code': 'VN', 'name': 'Vietnam', 'region': 'East Asia & Pacific', 'income_group': 'Lower middle income'},
            {'code': 'PH', 'name': 'Philippines', 'region': 'East Asia & Pacific', 'income_group': 'Lower middle income'},
            {'code': 'MY', 'name': 'Malaysia', 'region': 'East Asia & Pacific', 'income_group': 'Upper middle income'},
            {'code': 'TH', 'name': 'Thailand', 'region': 'East Asia & Pacific', 'income_group': 'Upper middle income'},
            {'code': 'SG', 'name': 'Singapore', 'region': 'East Asia & Pacific', 'income_group': 'High income'},
            {'code': 'AE', 'name': 'United Arab Emirates', 'region': 'Middle East & North Africa', 'income_group': 'High income'},
            {'code': 'IL', 'name': 'Israel', 'region': 'Middle East & North Africa', 'income_group': 'High income'},
            {'code': 'NO', 'name': 'Norway', 'region': 'Europe & Central Asia', 'income_group': 'High income'},
            {'code': 'SE', 'name': 'Sweden', 'region': 'Europe & Central Asia', 'income_group': 'High income'},
            {'code': 'DK', 'name': 'Denmark', 'region': 'Europe & Central Asia', 'income_group': 'High income'},
            {'code': 'FI', 'name': 'Finland', 'region': 'Europe & Central Asia', 'income_group': 'High income'},
            {'code': 'CH', 'name': 'Switzerland', 'region': 'Europe & Central Asia', 'income_group': 'High income'},
            {'code': 'AT', 'name': 'Austria', 'region': 'Europe & Central Asia', 'income_group': 'High income'},
            {'code': 'BE', 'name': 'Belgium', 'region': 'Europe & Central Asia', 'income_group': 'High income'},
            {'code': 'NL', 'name': 'Netherlands', 'region': 'Europe & Central Asia', 'income_group': 'High income'},
            {'code': 'IE', 'name': 'Ireland', 'region': 'Europe & Central Asia', 'income_group': 'High income'},
            {'code': 'NZ', 'name': 'New Zealand', 'region': 'East Asia & Pacific', 'income_group': 'High income'},
            {'code': 'CL', 'name': 'Chile', 'region': 'Latin America & Caribbean', 'income_group': 'High income'},
        ]
        
        for country_data in countries_data:
            country, created = Country.objects.get_or_create(
                code=country_data['code'],
                defaults=country_data
            )
            if created:
                self.stdout.write(f'Created country: {country.name}')
            else:
                # Update existing country
                for key, value in country_data.items():
                    setattr(country, key, value)
                country.save()
                self.stdout.write(f'Updated country: {country.name}')

    def populate_indicators(self):
        """Populate key indicators"""
        self.stdout.write('Populating indicators...')
        
        indicators_data = [
            {
                'code': 'NY.GDP.PCAP.CD',
                'name': 'GDP per capita (current US$)',
                'unit': 'US$',
                'description': 'GDP per capita is gross domestic product divided by midyear population.',
                'source': 'World Bank',
                'topic': 'Economy & Growth'
            },
            {
                'code': 'SI.POV.DDAY',
                'name': 'Poverty headcount ratio at $1.90 a day (2011 PPP) (% of population)',
                'unit': '% of population',
                'description': 'Poverty headcount ratio at $1.90 a day is the percentage of the population living on less than $1.90 a day.',
                'source': 'World Bank',
                'topic': 'Poverty'
            },
            {
                'code': 'SP.POP.TOTL',
                'name': 'Population, total',
                'unit': 'persons',
                'description': 'Total population is based on the de facto definition of population.',
                'source': 'World Bank',
                'topic': 'Population'
            },
            {
                'code': 'SL.UEM.TOTL.ZS',
                'name': 'Unemployment, total (% of total labor force)',
                'unit': '% of labor force',
                'description': 'Unemployment refers to the share of the labor force that is without work but available for and seeking employment.',
                'source': 'World Bank',
                'topic': 'Labor & Social Protection'
            },
            {
                'code': 'SE.PRM.NENR',
                'name': 'School enrollment, primary (% net)',
                'unit': '%',
                'description': 'Net enrollment rate is the ratio of children of official school age who are enrolled in school to the population of the corresponding official school age.',
                'source': 'World Bank',
                'topic': 'Education'
            },
            {
                'code': 'SH.DYN.MORT',
                'name': 'Mortality rate, under-5 (per 1,000 live births)',
                'unit': 'per 1,000 live births',
                'description': 'Under-five mortality rate is the probability per 1,000 that a newborn baby will die before reaching age five.',
                'source': 'World Bank',
                'topic': 'Health'
            },
            {
                'code': 'SH.XPD.CHEX.GD.ZS',
                'name': 'Current health expenditure (% of GDP)',
                'unit': '% of GDP',
                'description': 'Level of current health expenditure expressed as a percentage of GDP.',
                'source': 'World Bank',
                'topic': 'Health'
            },
            {
                'code': 'EG.USE.ELEC.KH.PC',
                'name': 'Electric power consumption (kWh per capita)',
                'unit': 'kWh per capita',
                'description': 'Electric power consumption measures the production of power plants and combined heat and power plants.',
                'source': 'World Bank',
                'topic': 'Energy'
            },
            {
                'code': 'EN.ATM.CO2E.PC',
                'name': 'CO2 emissions (metric tons per capita)',
                'unit': 'metric tons per capita',
                'description': 'Carbon dioxide emissions are those stemming from the burning of fossil fuels.',
                'source': 'World Bank',
                'topic': 'Environment'
            },
            {
                'code': 'IT.NET.USER.ZS',
                'name': 'Individuals using the Internet (% of population)',
                'unit': '% of population',
                'description': 'Internet users are individuals who have used the Internet in the last 3 months.',
                'source': 'World Bank',
                'topic': 'Infrastructure'
            }
        ]
        
        for indicator_data in indicators_data:
            indicator, created = Indicator.objects.get_or_create(
                code=indicator_data['code'],
                defaults=indicator_data
            )
            if created:
                self.stdout.write(f'Created indicator: {indicator.name}')
            else:
                # Update existing indicator
                for key, value in indicator_data.items():
                    setattr(indicator, key, value)
                indicator.save()
                self.stdout.write(f'Updated indicator: {indicator.name}')

    def populate_sample_data(self):
        """Populate sample happiness data"""
        self.stdout.write('Populating sample happiness data...')
        
        # Sample happiness data for key countries
        sample_happiness_data = [
            # United States
            {'country': 'US', 'year': 2020, 'happiness_score': 6.94, 'gdp_per_capita': 1.398, 'social_support': 1.471, 'healthy_life_expectancy': 0.879},
            {'country': 'US', 'year': 2021, 'happiness_score': 6.95, 'gdp_per_capita': 1.414, 'social_support': 1.459, 'healthy_life_expectancy': 0.884},
            {'country': 'US', 'year': 2022, 'happiness_score': 6.92, 'gdp_per_capita': 1.446, 'social_support': 1.454, 'healthy_life_expectancy': 0.879},
            {'country': 'US', 'year': 2023, 'happiness_score': 6.89, 'gdp_per_capita': 1.456, 'social_support': 1.448, 'healthy_life_expectancy': 0.877},
            
            # India
            {'country': 'IN', 'year': 2020, 'happiness_score': 3.82, 'gdp_per_capita': 0.745, 'social_support': 0.765, 'healthy_life_expectancy': 0.588},
            {'country': 'IN', 'year': 2021, 'happiness_score': 3.78, 'gdp_per_capita': 0.751, 'social_support': 0.761, 'healthy_life_expectancy': 0.594},
            {'country': 'IN', 'year': 2022, 'happiness_score': 3.85, 'gdp_per_capita': 0.774, 'social_support': 0.771, 'healthy_life_expectancy': 0.601},
            {'country': 'IN', 'year': 2023, 'happiness_score': 4.04, 'gdp_per_capita': 0.789, 'social_support': 0.782, 'healthy_life_expectancy': 0.606},
            
            # Germany
            {'country': 'DE', 'year': 2020, 'happiness_score': 7.04, 'gdp_per_capita': 1.373, 'social_support': 1.454, 'healthy_life_expectancy': 0.861},
            {'country': 'DE', 'year': 2021, 'happiness_score': 7.16, 'gdp_per_capita': 1.385, 'social_support': 1.467, 'healthy_life_expectancy': 0.867},
            {'country': 'DE', 'year': 2022, 'happiness_score': 7.18, 'gdp_per_capita': 1.395, 'social_support': 1.471, 'healthy_life_expectancy': 0.873},
            {'country': 'DE', 'year': 2023, 'happiness_score': 7.22, 'gdp_per_capita': 1.402, 'social_support': 1.475, 'healthy_life_expectancy': 0.878},
            
            # Japan
            {'country': 'JP', 'year': 2020, 'happiness_score': 5.94, 'gdp_per_capita': 1.302, 'social_support': 1.317, 'healthy_life_expectancy': 0.986},
            {'country': 'JP', 'year': 2021, 'happiness_score': 5.91, 'gdp_per_capita': 1.298, 'social_support': 1.315, 'healthy_life_expectancy': 0.988},
            {'country': 'JP', 'year': 2022, 'happiness_score': 5.95, 'gdp_per_capita': 1.305, 'social_support': 1.319, 'healthy_life_expectancy': 0.991},
            {'country': 'JP', 'year': 2023, 'happiness_score': 5.97, 'gdp_per_capita': 1.312, 'social_support': 1.322, 'healthy_life_expectancy': 0.994},
            
            # Brazil
            {'country': 'BR', 'year': 2020, 'happiness_score': 6.11, 'gdp_per_capita': 0.986, 'social_support': 1.415, 'healthy_life_expectancy': 0.776},
            {'country': 'BR', 'year': 2021, 'happiness_score': 6.08, 'gdp_per_capita': 0.981, 'social_support': 1.411, 'healthy_life_expectancy': 0.773},
            {'country': 'BR', 'year': 2022, 'happiness_score': 6.13, 'gdp_per_capita': 0.994, 'social_support': 1.418, 'healthy_life_expectancy': 0.778},
            {'country': 'BR', 'year': 2023, 'happiness_score': 6.16, 'gdp_per_capita': 1.001, 'social_support': 1.422, 'healthy_life_expectancy': 0.781},
            
            # Norway
            {'country': 'NO', 'year': 2020, 'happiness_score': 7.49, 'gdp_per_capita': 1.566, 'social_support': 1.533, 'healthy_life_expectancy': 0.863},
            {'country': 'NO', 'year': 2021, 'happiness_score': 7.39, 'gdp_per_capita': 1.554, 'social_support': 1.526, 'healthy_life_expectancy': 0.866},
            {'country': 'NO', 'year': 2022, 'happiness_score': 7.42, 'gdp_per_capita': 1.561, 'social_support': 1.529, 'healthy_life_expectancy': 0.869},
            {'country': 'NO', 'year': 2023, 'happiness_score': 7.43, 'gdp_per_capita': 1.564, 'social_support': 1.531, 'healthy_life_expectancy': 0.872},
        ]
        
        for data in sample_happiness_data:
            try:
                country = Country.objects.get(code=data['country'])
                happiness_data, created = HappinessData.objects.get_or_create(
                    country=country,
                    year=data['year'],
                    defaults={
                        'happiness_score': data['happiness_score'],
                        'gdp_per_capita': data.get('gdp_per_capita'),
                        'social_support': data.get('social_support'),
                        'healthy_life_expectancy': data.get('healthy_life_expectancy'),
                        'freedom_to_make_life_choices': data.get('freedom_to_make_life_choices'),
                        'generosity': data.get('generosity'),
                        'perceptions_of_corruption': data.get('perceptions_of_corruption'),
                    }
                )
                if created:
                    self.stdout.write(f'Created happiness data: {country.name} ({data["year"]})')
                else:
                    self.stdout.write(f'Happiness data already exists: {country.name} ({data["year"]})')
            except Country.DoesNotExist:
                self.stdout.write(f'Country {data["country"]} not found')
        
        self.stdout.write(self.style.SUCCESS(f'Sample data population completed!'))

    def fetch_worldbank_data_for_country(self, country_code, indicator_code, start_year=2015, end_year=2023):
        """Fetch World Bank data for a specific country and indicator"""
        try:
            url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}"
            params = {
                'format': 'json',
                'date': f'{start_year}:{end_year}',
                'per_page': 100
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1:
                    country = Country.objects.get(code=country_code)
                    indicator = Indicator.objects.get(code=indicator_code)
                    
                    for item in data[1]:
                        if item['value'] is not None:
                            WorldBankData.objects.update_or_create(
                                country=country,
                                indicator=indicator,
                                year=item['date'],
                                defaults={'value': item['value']}
                            )
                    
                    self.stdout.write(f'Fetched data for {country.name} - {indicator.name}')
                    time.sleep(0.1)  # Rate limiting
                    
        except Exception as e:
            self.stdout.write(f'Error fetching data for {country_code} - {indicator_code}: {e}')