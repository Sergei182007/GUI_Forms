import json
import os
import re
import uuid
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

VALID_GENDERS = ("мужской", "женский", "неопределенный")

# Первая буква заглавная, далее строчные; допускаются двойные части через дефис с заглавной буквы
NAME_PART_REGEX = re.compile(r"^[А-ЯЁA-Z][а-яёa-z]+(?:-[А-ЯЁA-Z][а-яёa-z]+)*$")

@dataclass
class Patient:
    id: str
    last_name: str
    first_name: str
    middle_name: str
    age: int
    gender: str
    height: float  # в сантиметрах
    weight: float  # в килограммах

    @property
    def fio(self) -> str:
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join(p for p in parts if p)

    @property
    def bmi(self) -> float:
        height_m = self.height / 100.0
        return round(self.weight / (height_m ** 2), 2)

    @property
    def bmi_status(self) -> str:
        bmi_val = self.bmi
        if bmi_val < 16.0 or bmi_val >= 30.0:
            return "danger"
        if bmi_val < 18.5 or bmi_val >= 25.0:
            return "warning"
        return "normal"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["fio"] = self.fio
        data["bmi"] = self.bmi
        data["bmi_status"] = self.bmi_status
        return data

class PatientModel:
    def __init__(self, filepath: str = "patients.json"):
        self.filepath = filepath
        self.patients: List[Patient] = []
        self.load_from_file()

    @staticmethod
    def _validate_name_part(
        value: str, field_label: str, required: bool = True
    ) -> str:
        cleaned = value.strip()
        if not cleaned:
            if not required:
                return ""
            raise ValueError(f"Поле «{field_label}» не может быть пустым.")
        if not NAME_PART_REGEX.fullmatch(cleaned):
            raise ValueError(
                f"Поле «{field_label}» должно начинаться с заглавной буквы, "
                f"содержать только буквы (без цифр и пробелов) и состоять минимум из 2 букв."
            )
        return cleaned

    @classmethod
    def validate_and_parse(
        cls,
        last_name: str,
        first_name: str,
        middle_name: str,
        age_str: str,
        gender: str,
        height_str: str,
        weight_str: str,
    ) -> Dict[str, Any]:
        # Валидация Фамилии, Имени (обязательные) и Отчества (необязательное)
        last_clean = cls._validate_name_part(last_name, "Фамилия", required=True)
        first_clean = cls._validate_name_part(first_name, "Имя", required=True)
        middle_clean = cls._validate_name_part(middle_name, "Отчество", required=False)

        # Валидация возраста
        age_clean = age_str.strip()
        if not age_clean:
            raise ValueError("Поле «Возраст» не может быть пустым.")
        try:
            age = int(age_clean)
        except ValueError:
            raise ValueError("Возраст должен быть целым числом.")
        if age < 0:
            raise ValueError("Возраст не может быть отрицательным.")
        if age == 0 or age > 125:
            raise ValueError("Возраст должен быть в диапазоне от 1 до 125 лет.")

        # Валидация пола
        gender_clean = gender.strip().lower()
        if gender_clean not in VALID_GENDERS:
            raise ValueError(
                f"Пол должен быть одним из значений: {', '.join(VALID_GENDERS)}."
            )

        # Валидация роста (см)
        height_clean = height_str.strip().replace(",", ".")
        if not height_clean:
            raise ValueError("Поле «Рост (см)» не может быть пустым.")
        try:
            height = float(height_clean)
        except ValueError:
            raise ValueError("Рост должен быть числом (в см).")
        if height <= 0:
            raise ValueError("Рост должен быть положительным числом.")
        if not (40 <= height <= 250):
            raise ValueError("Рост должен быть в диапазоне от 40 до 250 см.")

        # Валидация веса (кг)
        weight_clean = weight_str.strip().replace(",", ".")
        if not weight_clean:
            raise ValueError("Поле «Вес (кг)» не может быть пустым.")
        try:
            weight = float(weight_clean)
        except ValueError:
            raise ValueError("Вес должен быть числом (в кг).")
        if weight <= 0:
            raise ValueError("Вес должен быть положительным числом.")
        if not (2 <= weight <= 400):
            raise ValueError("Вес должен быть в диапазоне от 2 до 400 кг.")

        return {
            "last_name": last_clean,
            "first_name": first_clean,
            "middle_name": middle_clean,
            "age": age,
            "gender": gender_clean,
            "height": round(height, 1),
            "weight": round(weight, 1),
        }

    def add_patient(
        self,
        last_name: str,
        first_name: str,
        middle_name: str,
        age_str: str,
        gender: str,
        height_str: str,
        weight_str: str,
    ) -> Patient:
        data = self.validate_and_parse(
            last_name, first_name, middle_name, age_str, gender, height_str, weight_str
        )
        patient = Patient(id=uuid.uuid4().hex, **data)
        self.patients.append(patient)
        self.save_to_file()
        return patient

    def update_patient(
        self,
        patient_id: str,
        last_name: str,
        first_name: str,
        middle_name: str,
        age_str: str,
        gender: str,
        height_str: str,
        weight_str: str,
    ) -> Patient:
        data = self.validate_and_parse(
            last_name, first_name, middle_name, age_str, gender, height_str, weight_str
        )
        for idx, p in enumerate(self.patients):
            if p.id == patient_id:
                updated = Patient(id=patient_id, **data)
                self.patients[idx] = updated
                self.save_to_file()
                return updated
        raise ValueError("Пациент не найден.")

    def delete_patient(self, patient_id: str) -> None:
        initial_len = len(self.patients)
        self.patients = [p for p in self.patients if p.id != patient_id]
        if len(self.patients) == initial_len:
            raise ValueError("Пациент не найден.")
        self.save_to_file()

    def get_patient(self, patient_id: str) -> Patient:
        for p in self.patients:
            if p.id == patient_id:
                return p
        raise ValueError("Пациент не найден.")

    def get_all_patients(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self.patients]

    def save_to_file(self) -> None:
        raw_data = [
            {
                "id": p.id,
                "last_name": p.last_name,
                "first_name": p.first_name,
                "middle_name": p.middle_name,
                "age": p.age,
                "gender": p.gender,
                "height": p.height,
                "weight": p.weight,
            }
            for p in self.patients
        ]
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=4)

    def load_from_file(self) -> None:
        if not os.path.exists(self.filepath):
            self.patients = []
            return
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            loaded: List[Patient] = []
            for item in raw_data:
                if "last_name" in item:
                    last_name = str(item["last_name"])
                    first_name = str(item["first_name"])
                    middle_name = str(item.get("middle_name", ""))
                else:
                    parts = str(item.get("fio", "")).split()
                    last_name = parts[0] if len(parts) > 0 else ""
                    first_name = parts[1] if len(parts) > 1 else ""
                    middle_name = parts[2] if len(parts) > 2 else ""

                loaded.append(
                    Patient(
                        id=item.get("id", uuid.uuid4().hex),
                        last_name=last_name,
                        first_name=first_name,
                        middle_name=middle_name,
                        age=int(item["age"]),
                        gender=str(item["gender"]),
                        height=float(item["height"]),
                        weight=float(item["weight"]),
                    )
                )
            self.patients = loaded
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            self.patients = []