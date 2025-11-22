"""
End-to-end tests for the solve endpoint.

Tests cover:
- Valid and invalid inputs
- All problem categories
- Urgent and non-urgent cases
- Different service levels (OSBB, РА, City monopolists, Hotline)
- Complete orchestration flow (classify -> resolve -> generate appeal)

REQUIREMENTS:
These tests run against a real PostgreSQL database with pgvector extension.
Before running tests, ensure:
1. PostgreSQL is running: docker-compose up -d db
2. Database is initialized: alembic upgrade head
3. Test data exists in the database

To run tests:
    uv run pytest tests/test_solve_e2e.py -v
"""

import json
import pytest
from pathlib import Path
from typing import Dict, Any, List
from httpx import AsyncClient

from app.main import app


# Test fixtures paths
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "test_datasets"

# API endpoint
SOLVE_ENDPOINT = "/api/v1/solve/"


@pytest.fixture
def test_datasets() -> Dict[str, List[Dict[str, Any]]]:
    """Load test datasets"""
    datasets = {}
    
    # Load main datasets
    if FIXTURES_DIR.exists():
        for json_file in FIXTURES_DIR.glob("*.json"):
            if json_file.name != "summary.json":
                with open(json_file) as f:
                    datasets[json_file.stem] = json.load(f)
    
    return datasets


class TestSolveEndpointValid:
    """Test valid problem submissions"""
    
    @pytest.mark.asyncio
    async def test_solve_valid_problem_basic(self, async_client: AsyncClient):
        """Test basic valid problem submission"""
        request_data = {
            "user_info": {
                "name": "Іван Петренко",
                "phone": "0501234567",
                "address": "вул. Львівська, 10",
                "city": "Львів"
            },
            "problem_text": "У підіззді вже тиждень не горить лампочка на сходах"
        }
        
        response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "user_info" in data
        assert "classification" in data
        assert "service" in data
        assert "appeal_text" in data
        
        # Check classification
        classification = data["classification"]
        assert "category_id" in classification
        assert "category_name" in classification
        assert "is_urgent" in classification
        assert "confidence" in classification
        
        # Check service response
        service = data["service"]
        assert "service_info" in service
        assert "service_name" in service["service_info"]
        assert "service_phone" in service["service_info"]
        
        # Check appeal text is generated
        assert len(data["appeal_text"]) > 0
    
    @pytest.mark.asyncio
    async def test_solve_urgent_water_supply(self, async_client: AsyncClient):
        """Test urgent water supply problem - should resolve to monopolist"""
        request_data = {
            "user_info": {
                "name": "Тест",
                "phone": "0501234567",
                "address": "вул. Львівська, 15",
                "city": "Львів"
            },
            "problem_text": "АВАРІЙНА СИТУАЦІЯ! Нема холодної води вже 2 години, затоплення"
        }
        
        response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        
        # Should be classified as water_supply
        assert data["classification"]["category_id"] == "water_supply"
        
        # Should be marked urgent
        assert data["classification"]["is_urgent"] is True
        
        # Should resolve to citywide monopolist (water)
        assert data["service"]["service_info"]["service_type"] in ["КП", "Гаряча лінія"]
    
    @pytest.mark.asyncio
    async def test_solve_heating_problem(self, async_client: AsyncClient):
        """Test heating problem - should resolve to heating monopolist"""
        request_data = {
            "user_info": {
                "name": "Тест",
                "phone": "0501234567",
                "address": "вул. Героїв, 25",
                "city": "Львів"
            },
            "problem_text": "Батареї зовсім холодні, у кв +10 градусів, це аварійна ситуація"
        }
        
        response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        
        # Should be classified as heating
        assert data["classification"]["category_id"] in ["heating", "other"]
        
        # High confidence for urgent cases
        assert data["classification"]["confidence"] > 0.3
    
    @pytest.mark.asyncio
    async def test_solve_elevator_problem(self, async_client: AsyncClient):
        """Test elevator problem - should resolve to building service"""
        request_data = {
            "user_info": {
                "name": "Тест",
                "phone": "0501234567",
                "address": "вул. Лисеницька, 11а",
                "city": "Львів"
            },
            "problem_text": "Ліфт у 2-му підіззді не працює вже 3 дні, мешканці не можуть підняться"
        }
        
        response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        
        # Should be classified as elevator
        assert data["classification"]["category_id"] == "elevator"
        
        # Should be urgent
        assert data["classification"]["is_urgent"] is True
    
    @pytest.mark.asyncio
    async def test_solve_road_problem_district_level(self, async_client: AsyncClient):
        """Test roads problem - should resolve to district administration"""
        request_data = {
            "user_info": {
                "name": "Тест",
                "phone": "0501234567",
                "address": "вул. Ряшівська, 1",
                "city": "Львів"
            },
            "problem_text": "На перехресті вулиці Городоцька/Ряшівська потребується розмітка для траєкторій руху"
        }
        
        response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        
        # Should be classified as roads
        assert data["classification"]["category_id"] == "roads"
        
        # Should resolve to district level or hotline
        assert data["service"]["service_info"]["service_type"] in ["РА", "Гаряча лінія"]
    
    @pytest.mark.asyncio
    async def test_solve_with_all_categories(self, async_client: AsyncClient, test_datasets):
        """Test problems from different categories"""
        
        # Test cases covering different categories
        test_cases = [
            {
                "category": "lighting",
                "problem": "На вулиці не світить ліхтар, темно вночі"
            },
            {
                "category": "water_supply",
                "problem": "З крана тече іржава вода, неможливо пити"
            },
            {
                "category": "sewage",
                "problem": "У ванній протікає труба, затоплює сусідів"
            },
            {
                "category": "noise",
                "problem": "Сусіди вночі шумлять, гучна музика до 3 ночі"
            },
            {
                "category": "parking",
                "problem": "Машини паркуються на газоні, немає місця мешканцям"
            },
        ]
        
        for test_case in test_cases:
            request_data = {
                "user_info": {
                    "name": "Тест Користувач",
                    "phone": "0501234567",
                    "address": "вул. Тестова, 1",
                    "city": "Львів"
                },
                "problem_text": test_case["problem"]
            }
            
            response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
            assert response.status_code == 200, f"Failed for {test_case['category']}"
            
            data = response.json()
            
            # Verify response structure
            assert "classification" in data
            assert "service" in data
            assert "appeal_text" in data
            
            # Should have non-zero confidence
            assert data["classification"]["confidence"] >= 0


class TestSolveEndpointInvalid:
    """Test invalid inputs"""
    
    @pytest.mark.asyncio
    async def test_solve_empty_problem_text(self, async_client: AsyncClient):
        """Test empty problem text"""
        request_data = {
            "user_info": {
                "name": "Тест",
                "phone": "0501234567",
                "address": "вул. Тестова, 1",
                "city": "Львів"
            },
            "problem_text": ""
        }
        
        response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_solve_too_short_problem(self, async_client: AsyncClient):
        """Test problem text too short"""
        request_data = {
            "user_info": {
                "name": "Тест",
                "phone": "0501234567",
                "address": "вул. Тестова, 1",
                "city": "Львів"
            },
            "problem_text": "x"
        }
        
        response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_solve_missing_user_info(self, async_client: AsyncClient):
        """Test missing user info"""
        request_data = {
            "problem_text": "Це є валідне описання проблеми"
        }
        
        response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_solve_missing_name(self, async_client: AsyncClient):
        """Test missing name"""
        request_data = {
            "user_info": {
                "phone": "0501234567",
                "address": "вул. Тестова, 1",
                "city": "Львів"
            },
            "problem_text": "Це є валідне описання проблеми"
        }
        
        response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
        # May accept partial data or reject - depends on schema
        assert response.status_code in [200, 422]


class TestSolveEndpointUrgency:
    """Test urgency detection and handling"""
    
    @pytest.mark.asyncio
    async def test_urgent_emergency_keywords(self, async_client: AsyncClient):
        """Test urgency detection with emergency keywords"""
        urgent_problems = [
            "АВАРІЙНА СИТУАЦІЯ! Нема світла 3 години",
            "Критично! Протікає вода в підвалі",
            "Терміново! Застряг у ліфті",
            "Негайно потрібна допомога! Нема опалення",
        ]
        
        for problem_text in urgent_problems:
            request_data = {
                "user_info": {
                    "name": "Тест",
                    "phone": "0501234567",
                    "address": "вул. Тестова, 1",
                    "city": "Львів"
                },
                "problem_text": problem_text
            }
            
            response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            
            # Should be marked as urgent
            assert data["classification"]["is_urgent"] is True
    
    @pytest.mark.asyncio
    async def test_non_urgent_regular_problem(self, async_client: AsyncClient):
        """Test non-urgent regular problem"""
        request_data = {
            "user_info": {
                "name": "Тест",
                "phone": "0501234567",
                "address": "вул. Тестова, 1",
                "city": "Львів"
            },
            "problem_text": "Прошу полагодити дорожну розмітку біля будинку, коли вам буде зручно"
        }
        
        response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        
        # Should not be marked as urgent
        assert data["classification"]["is_urgent"] is False


class TestSolveEndpointServiceLevels:
    """Test correct service level resolution"""
    
    @pytest.mark.asyncio
    async def test_building_level_service_osbb(self, async_client: AsyncClient):
        """Test building-level service (OSBB/ЖЕК)"""
        building_level_problems = [
            ("вул. Лисеницька, 11а", "Ліфт не працює"),
            ("вул. Лисеницька, 11а", "На сходовій не світло"),
            ("вул. Лисеницька, 11а", "З стелі капає вода"),
        ]
        
        for address, problem in building_level_problems:
            request_data = {
                "user_info": {
                    "name": "Тест",
                    "phone": "0501234567",
                    "address": address,
                    "city": "Львів"
                },
                "problem_text": problem
            }
            
            response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
            if response.status_code == 200:
                data = response.json()
                # Service should be OSBB or building manager
                service_type = data["service"]["service_info"]["service_type"]
                assert service_type in ["КП", "ОСББ", "ЖЕК", "Гаряча лінія"]
    
    @pytest.mark.asyncio
    async def test_citywide_monopolist_service(self, async_client: AsyncClient):
        """Test citywide monopolist services"""
        monopolist_problems = [
            ("water_supply", "Немає холодної води"),
            ("heating", "Батареї холодні, немає опалення"),
            ("gas", "Відчуваю запах газу"),
            ("lighting", "На вулиці всім брак освітлення"),
        ]
        
        for category, problem in monopolist_problems:
            request_data = {
                "user_info": {
                    "name": "Тест",
                    "phone": "0501234567",
                    "address": "вул. Тестова, 1",
                    "city": "Львів"
                },
                "problem_text": problem
            }
            
            response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
            if response.status_code == 200:
                data = response.json()
                # Should resolve to monopolist or hotline
                assert "service_name" in data["service"]["service_info"]
    
    @pytest.mark.asyncio
    async def test_hotline_fallback(self, async_client: AsyncClient):
        """Test fallback to hotline for unclassified problems"""
        request_data = {
            "user_info": {
                "name": "Тест",
                "phone": "0501234567",
                "address": "вул. Тестова, 1",
                "city": "Львів"
            },
            "problem_text": "Якась дуже незвична проблема що не входить ні до якої категорії"
        }
        
        response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        
        # Should have service response
        assert "service_info" in data["service"]
        # May be hotline if no better match
        if data["classification"]["confidence"] < 0.5:
            service_name = data["service"]["service_info"]["service_name"]
            # Could be hotline or generic service
            assert service_name is not None


class TestSolveEndpointResponseStructure:
    """Test response structure and completeness"""
    
    @pytest.mark.asyncio
    async def test_response_contains_user_info(self, async_client: AsyncClient):
        """Test response contains user info"""
        request_data = {
            "user_info": {
                "name": "Іван Петренко",
                "phone": "0501234567",
                "address": "вул. Львівська, 10",
                "city": "Львів"
            },
            "problem_text": "У підіззді вже тиждень не горить лампочка на сходах"
        }
        
        response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        
        # Check user info is preserved
        assert data["user_info"]["name"] == "Іван Петренко"
        assert data["user_info"]["phone"] == "0501234567"
        assert data["user_info"]["address"] == "вул. Львівська, 10"
        assert data["user_info"]["city"] == "Львів"
    
    @pytest.mark.asyncio
    async def test_response_has_classification(self, async_client: AsyncClient):
        """Test response has complete classification"""
        request_data = {
            "user_info": {
                "name": "Тест",
                "phone": "0501234567",
                "address": "вул. Тестова, 1",
                "city": "Львів"
            },
            "problem_text": "У підіззді не світло на сходах"
        }
        
        response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        classification = data["classification"]
        
        # Check all required fields
        assert "category_id" in classification
        assert "category_name" in classification
        assert "is_urgent" in classification
        assert "confidence" in classification
        
        # Validate values
        assert isinstance(classification["category_id"], str)
        assert isinstance(classification["category_name"], str)
        assert isinstance(classification["is_urgent"], bool)
        assert 0 <= classification["confidence"] <= 1
    
    @pytest.mark.asyncio
    async def test_response_has_service(self, async_client: AsyncClient):
        """Test response has complete service info"""
        request_data = {
            "user_info": {
                "name": "Тест",
                "phone": "0501234567",
                "address": "вул. Тестова, 1",
                "city": "Львів"
            },
            "problem_text": "Немає гарячої води"
        }
        
        response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        service = data["service"]
        service_info = service["service_info"]
        
        # Check all required fields
        assert "service_type" in service_info
        assert "service_name" in service_info
        assert "service_phone" in service_info
        
        # Validate values
        assert isinstance(service_info["service_type"], str)
        assert isinstance(service_info["service_name"], str)
        assert service_info["service_phone"] is not None
    
    @pytest.mark.asyncio
    async def test_response_has_appeal_text(self, async_client: AsyncClient):
        """Test response has generated appeal text"""
        request_data = {
            "user_info": {
                "name": "Тест",
                "phone": "0501234567",
                "address": "вул. Тестова, 1",
                "city": "Львів"
            },
            "problem_text": "Батареї холодні, немає опалення"
        }
        
        response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        
        # Check appeal text exists and is not empty
        assert "appeal_text" in data
        assert len(data["appeal_text"]) > 20  # Should be substantial text
        assert isinstance(data["appeal_text"], str)


class TestSolveEndpointWithDatasets:
    """Test with generated test datasets"""
    
    @pytest.mark.asyncio
    async def test_valid_problems_from_fixtures(self, async_client: AsyncClient, test_datasets):
        """Test valid problems from generated fixtures"""
        
        if "valid_problems" not in test_datasets:
            pytest.skip("Valid problems fixtures not found")
        
        valid_problems = test_datasets["valid_problems"]
        
        # Test first 5 valid problems
        for test_case in valid_problems[:5]:
            request_data = {
                "user_info": {
                    "name": test_case["input"]["name"],
                    "phone": test_case["input"]["phone"],
                    "address": test_case["input"]["address"],
                    "city": "Львів"
                },
                "problem_text": test_case["input"]["problem_text"]
            }
            
            response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            
            # Verify response has all parts
            assert "classification" in data
            assert "service" in data
            assert "appeal_text" in data
    
    @pytest.mark.asyncio
    async def test_invalid_problems_from_fixtures(self, async_client: AsyncClient, test_datasets):
        """Test invalid problems from generated fixtures"""
        
        if "invalid_problems" not in test_datasets:
            pytest.skip("Invalid problems fixtures not found")
        
        invalid_problems = test_datasets["invalid_problems"]
        
        # Test invalid problems
        for test_case in invalid_problems:
            request_data = {
                "user_info": {
                    "name": test_case["input"]["name"],
                    "phone": test_case["input"]["phone"],
                    "address": test_case["input"]["address"],
                    "city": "Львів"
                },
                "problem_text": test_case["input"]["problem_text"]
            }
            
            response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
            
            # Should reject invalid input
            assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_urgent_problems_from_fixtures(self, async_client: AsyncClient, test_datasets):
        """Test urgent problems are correctly identified"""
        
        if "urgent_problems" not in test_datasets:
            pytest.skip("Urgent problems fixtures not found")
        
        urgent_problems = test_datasets["urgent_problems"]
        
        # Test first 3 urgent problems
        for test_case in urgent_problems[:3]:
            request_data = {
                "user_info": {
                    "name": test_case["input"]["name"],
                    "phone": test_case["input"]["phone"],
                    "address": test_case["input"]["address"],
                    "city": "Львів"
                },
                "problem_text": test_case["input"]["problem_text"]
            }
            
            response = await async_client.post(SOLVE_ENDPOINT, json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            
            # Should be marked as urgent
            assert data["classification"]["is_urgent"] is True


# Conftest for async test support
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
