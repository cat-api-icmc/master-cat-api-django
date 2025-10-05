from requests.exceptions import HTTPError
from typing_extensions import Tuple
from plumber.base import BaseClient


class Endpoints(object):
    HEALTH_CHECK = "hc"
    GET_DESIGN_DATA = "get-design-data"

    IRT_START_ASSESSEMENT = "irt/start-assessment"
    IRT_NEXT_ITEM = "irt/next-item"

    CDM_START_ASSESSEMENT = "cdm/start-assessment"
    CDM_NEXT_ITEM = "cdm/next-item"


class PlumberClient(object):

    def __init__(self):
        self.base = BaseClient()

    def health_check(self) -> Tuple[bool, dict]:
        try:
            response = self.base.make_request(Endpoints.HEALTH_CHECK)
            response.raise_for_status()
            return True, response.json()
        except HTTPError:
            return False, {"status": "Unhealthy!"}

    def get_design_data(self, encoded_design: str) -> dict:
        payload = {"design": encoded_design}
        response = self.base.make_request(
            Endpoints.GET_DESIGN_DATA, method="POST", body=payload
        )
        return response.json()

    def irt_start_assesment(self, questions: list, assessment_config: dict) -> tuple:
        payload = {"questions": questions, "config": assessment_config}
        response = self.base.make_request(
            Endpoints.IRT_START_ASSESSEMENT, method="POST", body=payload
        )
        return response.status_code, response.json()

    def irt_next_item(
        self, answer: bool, previous_index: int, encoded_design: str
    ) -> tuple:
        payload = {
            "answer": answer,
            "previous_index": previous_index,
            "design": encoded_design,
        }
        response = self.base.make_request(
            Endpoints.IRT_NEXT_ITEM, method="POST", body=payload
        )
        return response.status_code, response.json()

    def cdm_start_assesment(
        self, questions: list, assessment_config: dict
    ) -> tuple:
        payload = {
            "questions": questions,
            "config": assessment_config,
        }
        response = self.base.make_request(
            Endpoints.CDM_START_ASSESSEMENT, method="POST", body=payload
        )
        return response.status_code, response.json()

    def cdm_next_item(
        self,
        answer: bool,
        previous_index: int,
        model: str,
        criteria: str,
        questions: list,
        encoded_design: str,
    ) -> tuple:
        payload = {
            "answer": answer,
            "previous_index": previous_index,
            "model": model,
            "criteria": criteria,
            "questions": questions,
            "design": encoded_design,
        }
        response = self.base.make_request(
            Endpoints.CDM_NEXT_ITEM, method="POST", body=payload
        )
        return response.status_code, response.json()
