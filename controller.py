from model import PatientModel, VALID_GENDERS
from view import PatientView

class PatientController:
    def __init__(self):
        self.model = PatientModel("patients.json")
        self.view = PatientView(VALID_GENDERS)

        self.view.on_add_click = self.handle_add
        self.view.on_edit_click = self.handle_edit
        self.view.on_delete_click = self.handle_delete
        self.view.on_stats_click = self.handle_stats

        self.refresh_view()

    def refresh_view(self) -> None:
        patients = self.model.get_all_patients()
        self.view.update_table(patients)

    def handle_add(self) -> None:
        def submit(
            last_name: str,
            first_name: str,
            middle_name: str,
            age: str,
            gender: str,
            height: str,
            weight: str,
        ) -> bool:
            try:
                self.model.add_patient(
                    last_name, first_name, middle_name, age, gender, height, weight
                )
                self.refresh_view()
                return True
            except ValueError as err:
                self.view.show_error("Ошибка валидации", str(err))
                return False

        self.view.open_patient_form("Добавить пациента", submit)

    def handle_edit(self, patient_id: str) -> None:
        try:
            patient = self.model.get_patient(patient_id).to_dict()
        except ValueError as err:
            self.view.show_error("Ошибка", str(err))
            return

        def submit(
            last_name: str,
            first_name: str,
            middle_name: str,
            age: str,
            gender: str,
            height: str,
            weight: str,
        ) -> bool:
            try:
                self.model.update_patient(
                    patient_id,
                    last_name,
                    first_name,
                    middle_name,
                    age,
                    gender,
                    height,
                    weight,
                )
                self.refresh_view()
                return True
            except ValueError as err:
                self.view.show_error("Ошибка валидации", str(err))
                return False

        self.view.open_patient_form(
            "Редактировать пациента", submit, initial_data=patient
        )

    def handle_delete(self, patient_id: str) -> None:
        try:
            patient = self.model.get_patient(patient_id)
        except ValueError as err:
            self.view.show_error("Ошибка", str(err))
            return

        if self.view.ask_confirm(
            "Подтверждение", f"Удалить пациента «{patient.fio}»?"
        ):
            try:
                self.model.delete_patient(patient_id)
                self.refresh_view()
            except ValueError as err:
                self.view.show_error("Ошибка", str(err))

    def handle_stats(self) -> None:
        patients = self.model.get_all_patients()
        if not patients:
            self.view.show_warning(
                "Нет данных", "Добавьте хотя бы одного пациента для построения графиков."
            )
            return
        self.view.open_stats_window(patients)

    def run(self) -> None:
        self.view.run()

if __name__ == "__main__":
    app = PatientController()
    app.run()