import requests
import json
import csv
from io import StringIO
from django.utils import timezone
from .models import Country, HappinessData, WorldBankData, Indicator

class DataFetchingService:
    """Service class for fetching data from external APIs"""
    
    @staticmethod
    def fetch_happiness_data_from_csv():
        """
        Fetch happiness data from World Happiness Report CSV files
        This is a more reliable method than hardcoded data
        """
        # These are publicly available World Happiness Report datasets
        happiness_urls = {
            2023: 'https://raw.githubusercontent.com/worldhappiness/worldhappiness.github.io/master/data/2023.csv',
            2022: 'https://raw.githubusercontent.com/worldhappiness/worldhappiness.github.io/master/data/2022.csv',
            2021: 'https://raw.githubusercontent.com/worldhappiness/worldhappiness.github.io/master/data/2021.csv',
        }
        
        # Country name mapping to handle variations
        country_name_to_code = {
            'United States': 'US',
            'United Kingdom': 'GB',
            'South Korea': 'KR',
            'Russia': 'RU',
            'Czech Republic': 'CZ',
            'Slovakia': 'SK',
            'Taiwan': 'TW',
            'Hong Kong': 'HK',
        }
        
        fetched_data = []
        
        for year, url in happiness_urls.items():
            try:
                print(f"Fetching happiness data for {year}...")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    # Parse CSV data
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    
                    for row in reader:
                        # Extract country name (handle different column names)
                        country_name = row.get('Country', row.get('Country name', ''))
                        
                        # Try to match with our country codes
                        country_code = country_name_to_code.get(country_name)
                        
                        if not country_code:
                            # Try direct lookup in our database
                            try:
                                country = Country.objects.get(name__iexact=country_name)
                                country_code = country.code
                            except Country.DoesNotExist:
                                continue
                        
                        # Extract happiness score (handle different column names)
                        happiness_score = None
                        for col in ['Happiness Score', 'Life Ladder', 'Score']:
                            if col in row and row[col]:
                                try:
                                    happiness_score = float(row[col])
                                    break
                                except ValueError:
                                    continue
                        
                        if happiness_score and country_code:
                            fetched_data.append({
                                'country_code': country_code,
                                'year': year,
                                'happiness_score': happiness_score,
                                'gdp_per_capita': DataFetchingService._safe_float(row.get('GDP per capita', row.get('Log GDP per capita', ''))),
                                'social_support': DataFetchingService._safe_float(row.get('Social support', '')),
                                'healthy_life_expectancy': DataFetchingService._safe_float(row.get('Healthy life expectancy', '')),
                                'freedom_to_make_life_choices': DataFetchingService._safe_float(row.get('Freedom to make life choices', '')),
                                'generosity': DataFetchingService._safe_float(row.get('Generosity', '')),
                                'perceptions_of_corruption': DataFetchingService._safe_float(row.get('Perceptions of corruption', '')),
                            })
                            
            except Exception as e:
                print(f"Error fetching happiness data for {year}: {e}")
                continue
        
        return fetched_data
    
    @staticmethod
    def _safe_float(value):
        """Safely convert string to float, return None if conversion fails"""
        try:
            return float(value) if value else None
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def fetch_worldbank_data(country_code, indicator_code, start_year=2015, end_year=2023):
        """
        Fetch World Bank data for a specific country and indicator
        """
        try:
            url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}"
            params = {
                'format': 'json',
                'date': f'{start_year}:{end_year}',
                'per_page': 100
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if len(data) > 1 and data[1]:
                    # Get or create country and indicator
                    country = Country.objects.get(code=country_code)
                    indicator = Indicator.objects.get(code=indicator_code)
                    
                    fetched_records = []
                    for item in data[1]:
                        if item['value'] is not None:
                            wb_data, created = WorldBankData.objects.update_or_create(
                                country=country,
                                indicator=indicator,
                                year=int(item['date']),
                                defaults={'value': float(item['value'])}
                            )
                            fetched_records.append(wb_data)
                    
                    return fetched_records
                    
        except Exception as e:
            print(f"Error fetching World Bank data for {country_code}-{indicator_code}: {e}")
            return []
    
    @staticmethod
    def get_available_countries_from_worldbank():
        """
        Fetch list of countries from World Bank API
        """
        try:
            url = "https://api.worldbank.org/v2/country"
            params = {
                'format': 'json',
                'per_page': 300
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if len(data) > 1:
                    countries = []
                    for item in data[1]:
                        if item['capitalCity']:  # Filter out regions, only get actual countries
                            countries.append({
                                'code': item['id'],
                                'name': item['name'],
                                'region': item['region']['value'] if item['region']['value'] != 'Aggregates' else None,
                                'income_group': item['incomeLevel']['value'] if item['incomeLevel']['value'] != 'Aggregates' else None
                            })
                    
                    return countries
                    
        except Exception as e:
            print(f"Error fetching countries from World Bank: {e}")
            return []
    
    @staticmethod
    def get_available_indicators_from_worldbank():
        """
        Fetch list of indicators from World Bank API
        """
        try:
            url = "https://api.worldbank.org/v2/indicator"
            params = {
                'format': 'json',
                'per_page': 1000
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if len(data) > 1:
                    indicators = []
                    for item in data[1]:
                        indicators.append({
                            'code': item['id'],
                            'name': item['name'],
                            'unit': item.get('unit', ''),
                            'description': item.get('sourceNote', ''),
                            'source': item.get('source', {}).get('value', 'World Bank'),
                            'topic': item.get('topics', [{}])[0].get('value', '') if item.get('topics') else ''
                        })
                    
                    return indicators
                    
        except Exception as e:
            print(f"Error fetching indicators from World Bank: {e}")
            return []

class HappinessDataService:
    """Service for handling happiness data operations"""
    
    @staticmethod
    def get_happiness_data(country_code, year=None):
        """Get happiness data for a country, fetch from API if not available"""
        try:
            country = Country.objects.get(code=country_code)
            
            if year:
                happiness_data = HappinessData.objects.filter(
                    country=country,
                    year=year
                ).first()
                
                if not happiness_data or happiness_data.happiness_score is None:
                    # Try to fetch from external source
                    HappinessDataService.fetch_and_store_happiness_data(country_code, year)
                    happiness_data = HappinessData.objects.filter(
                        country=country,
                        year=year
                    ).first()
                
                return happiness_data
            else:
                # Return all available data for country
                return HappinessData.objects.filter(country=country).exclude(happiness_score__isnull=True)
                
        except Country.DoesNotExist:
            return None
    
    @staticmethod
    def fetch_and_store_happiness_data(country_code, year):
        """Fetch happiness data from external source and store in database"""
        try:
            # In a real implementation, this would fetch from World Happiness Report API
            # For now, we'll create a placeholder that can be extended
            
            country = Country.objects.get(code=country_code)
            
            # Create placeholder happiness data entry
            happiness_data, created = HappinessData.objects.get_or_create(
                country=country,
                year=year,
                defaults={
                    'happiness_score': None,  # Will be populated by external API
                    'gdp_per_capita': None,
                    'social_support': None,
                    'healthy_life_expectancy': None,
                    'freedom_to_make_life_choices': None,
                    'generosity': None,
                    'perceptions_of_corruption': None,
                }
            )
            
            return happiness_data
            
        except Exception as e:
            print(f"Error fetching happiness data for {country_code}-{year}: {e}")
            return None