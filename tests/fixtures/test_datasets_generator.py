"""
Script to generate comprehensive test datasets for E2E testing.
Creates input/output test cases from full_dataset.json covering:
- Valid and invalid problems
- All categories
- Urgent and non-urgent cases
- Different service levels (OSBB, РА, City monopolists, Hotline)
- Different districts
"""

import json
import random
from pathlib import Path
from typing import Any, Dict, List
from collections import defaultdict


class TestDatasetGenerator:
    """Generates comprehensive test datasets for E2E testing"""
    
    # Service level mappings based on categories
    CITYWIDE_MONOPOLISTS = {
        "water_supply": "Львівводоканал",
        "heating": "Львівтеплоенерго",
        "gas": "Львівгаз",
        "lighting": "Львівсвітло",
    }
    
    DISTRICT_LEVEL = {
        "roads": "РА",
        "trees": "РА",
        "yard": "РА",
        "cleaning": "РА",
    }
    
    BUILDING_LEVEL = {
        "elevator": "ОСББ/ЖЕК",
        "entrance_doors": "ОСББ/ЖЕК",
        "roof": "ОСББ/ЖЕК",
    }
    
    HOTLINE_DEFAULT = "Гаряча лінія 1580"
    
    def __init__(self, full_dataset_path: str, output_dir: str):
        """
        Initialize generator
        
        Args:
            full_dataset_path: Path to full_dataset.json
            output_dir: Directory to save generated test datasets
        """
        self.full_dataset_path = full_dataset_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Sample data from full dataset
        with open(full_dataset_path) as f:
            self.full_data = json.load(f)
    
    def _get_service_level(self, category_id: str) -> str:
        """Determine service level for category"""
        if category_id in self.CITYWIDE_MONOPOLISTS:
            return "citywide_monopolist"
        elif category_id in self.DISTRICT_LEVEL:
            return "district_administration"
        elif category_id in self.BUILDING_LEVEL:
            return "osbb_building"
        else:
            return "hotline"
    
    def _extract_category_from_data(self, item: Dict) -> str:
        """Extract category ID from dataset item"""
        # Map known categories
        category_map = {
            "water": "water_supply",
            "heating": "heating",
            "gas": "gas",
            "lighting": "lighting",
            "elevator": "elevator",
            "roof": "roof",
            "roads": "roads",
            "trees": "trees",
            "yard": "yard",
            "cleaning": "cleaning",
            "sewage": "sewage",
            "sewage_overflow": "sewage",
            "parking": "parking",
            "noise": "noise",
        }
        
        item_id = item.get("id", "")
        item_name = item.get("name", "").lower() if item.get("name") else ""
        item_desc = item.get("description", "").lower()
        
        # Try to match by ID first
        for key, value in category_map.items():
            if key in item_id.lower():
                return value
        
        # Try to match by name
        for key, value in category_map.items():
            if key in item_name:
                return value
        
        # Try to match by description
        for key, value in category_map.items():
            if key in item_desc:
                return value
        
        # Default to "other" if no match
        return "other"
    
    def _is_urgent(self, text: str, category_id: str) -> bool:
        """Determine if problem is urgent based on keywords"""
        urgent_keywords = [
            "аварійн",
            "критичн",
            "термінов",
            "негайн",
            "без світла",
            "без води",
            "протік",
            "витік",
            "затоплення",
            "пожежа",
            "небезпеч",
            "ляс не працю",
            "не працю",
        ]
        
        text_lower = text.lower()
        is_urgent = any(keyword in text_lower for keyword in urgent_keywords)
        
        # Some categories are inherently urgent
        inherently_urgent = ["elevator", "sewage", "gas", "heating"]
        if category_id in inherently_urgent:
            is_urgent = is_urgent or random.random() < 0.3  # 30% chance
        
        return is_urgent
    
    def _parse_address(self, address_text: str) -> tuple[str, str, str]:
        """
        Parse address from raw data
        
        Returns:
            (street_name, building_number, district)
        """
        if not address_text:
            return ("вул. Невідома", "1", "Невідомий район")
        
        # Expected format: "вул. Назва, #, Район"
        parts = [p.strip() for p in address_text.split(",")]
        
        street = parts[0] if len(parts) > 0 else "вул. Невідома"
        building = parts[1] if len(parts) > 1 else "1"
        district = parts[2] if len(parts) > 2 else "Невідомий район"
        
        # Extract only digits from building if it has text
        building_num = ''.join(c for c in building.split()[0] if c.isdigit()) if building else "1"
        
        return (street, building_num or "1", district)
    
    def generate_test_cases(self, 
                           samples_per_category: int = 2,
                           valid_count: int = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate test cases from full dataset
        
        Args:
            samples_per_category: Number of samples per category
            valid_count: Total number of valid test cases (None for auto-calculate)
            
        Returns:
            Dict with categories of test cases
        """
        test_cases = {
            "valid_problems": [],
            "invalid_problems": [],
            "urgent_problems": [],
            "non_urgent_problems": [],
            "by_service_level": defaultdict(list),
            "by_category": defaultdict(list),
        }
        
        # Group by category
        by_category = defaultdict(list)
        for item in self.full_data:
            if not item.get("empty"):
                category = self._extract_category_from_data(item)
                by_category[category].append(item)
        
        # Generate valid test cases
        for category_id, items in by_category.items():
            samples = random.sample(
                items,
                min(samples_per_category, len(items))
            )
            
            for item in samples:
                problem_text = item.get("text", "")
                if len(problem_text) < 5:
                    problem_text = item.get("description", problem_text)
                
                raw_data = item.get("rawData") or {}
                address_text = raw_data.get("caseAddress", "") if isinstance(raw_data, dict) else ""
                street, building, district = self._parse_address(address_text)
                
                is_urgent = self._is_urgent(problem_text, category_id)
                service_level = self._get_service_level(category_id)
                
                test_case = {
                    "input": {
                        "name": "Тестовий користувач",
                        "phone": "0501234567",
                        "address": f"{street}, {building}",
                        "problem_text": problem_text,
                    },
                    "expected_output": {
                        "category_id": category_id,
                        "category_name": item.get("name", ""),
                        "is_urgent": is_urgent,
                        "service_level": service_level,
                        "district": district,
                        "confidence_min": 0.5,  # Minimum confidence threshold
                    },
                    "metadata": {
                        "source": "full_dataset",
                        "original_id": item.get("id"),
                        "description": item.get("description", ""),
                    }
                }
                
                test_cases["valid_problems"].append(test_case)
                test_cases["by_category"][category_id].append(test_case)
                test_cases["by_service_level"][service_level].append(test_case)
                
                if is_urgent:
                    test_cases["urgent_problems"].append(test_case)
                else:
                    test_cases["non_urgent_problems"].append(test_case)
        
        # Generate invalid test cases
        invalid_test_cases = [
            {
                "input": {
                    "name": "Test",
                    "phone": "invalid",
                    "address": "",
                    "problem_text": "x",  # Too short
                },
                "expected_error": "validation_error",
                "description": "Problem text too short"
            },
            {
                "input": {
                    "name": "",
                    "phone": "0501234567",
                    "address": "вул. Невідома, 1",
                    "problem_text": "",  # Empty
                },
                "expected_error": "validation_error",
                "description": "Empty problem text"
            },
            {
                "input": {
                    "name": "Test",
                    "phone": "invalid_phone",
                    "address": "вул. Невідома, 1",
                    "problem_text": "This is a valid problem description",
                },
                "expected_error": "validation_error",
                "description": "Invalid phone format"
            },
        ]
        
        test_cases["invalid_problems"] = invalid_test_cases
        
        return test_cases
    
    def save_test_datasets(self, test_cases: Dict[str, Any]) -> None:
        """Save test cases to JSON files"""
        
        # Save main datasets
        with open(self.output_dir / "valid_problems.json", "w", encoding="utf-8") as f:
            json.dump(test_cases["valid_problems"], f, ensure_ascii=False, indent=2)
        
        with open(self.output_dir / "invalid_problems.json", "w", encoding="utf-8") as f:
            json.dump(test_cases["invalid_problems"], f, ensure_ascii=False, indent=2)
        
        with open(self.output_dir / "urgent_problems.json", "w", encoding="utf-8") as f:
            json.dump(test_cases["urgent_problems"], f, ensure_ascii=False, indent=2)
        
        with open(self.output_dir / "non_urgent_problems.json", "w", encoding="utf-8") as f:
            json.dump(test_cases["non_urgent_problems"], f, ensure_ascii=False, indent=2)
        
        # Save by service level
        for service_level, cases in test_cases["by_service_level"].items():
            filename = f"service_level_{service_level}.json"
            with open(self.output_dir / filename, "w", encoding="utf-8") as f:
                json.dump(cases, f, ensure_ascii=False, indent=2)
        
        # Save by category
        for category_id, cases in test_cases["by_category"].items():
            filename = f"category_{category_id}.json"
            with open(self.output_dir / filename, "w", encoding="utf-8") as f:
                json.dump(cases, f, ensure_ascii=False, indent=2)
        
        # Save summary
        summary = {
            "total_valid_cases": len(test_cases["valid_problems"]),
            "total_invalid_cases": len(test_cases["invalid_problems"]),
            "total_urgent_cases": len(test_cases["urgent_problems"]),
            "total_non_urgent_cases": len(test_cases["non_urgent_problems"]),
            "categories_covered": list(test_cases["by_category"].keys()),
            "service_levels_covered": list(test_cases["by_service_level"].keys()),
        }
        
        with open(self.output_dir / "summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Test datasets generated successfully!")
        print(f"   Output directory: {self.output_dir}")
        print(f"   Summary:\n{json.dumps(summary, ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    
    full_dataset = "app/data/full_dataset.json"
    output_dir = "tests/fixtures/test_datasets"
    
    generator = TestDatasetGenerator(full_dataset, output_dir)
    test_cases = generator.generate_test_cases(samples_per_category=3)
    generator.save_test_datasets(test_cases)
