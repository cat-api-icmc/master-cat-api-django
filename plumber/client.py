from plumber.base import BaseClient
from typing_extensions import Tuple


class Endpoints(object):
    HEALTH_CHECK = "hc"
    START_ASSESSEMENT = "start-assessment"
    NEXT_ITEM = "next-item"
    GET_DESIGN_DATA = "get-design-data"


class PlumberClient(object):

    def __init__(self):
        self.base = BaseClient()

    def health_check(self) -> Tuple[bool, dict]:
        try:
            response = self.base.make_request(Endpoints.HEALTH_CHECK)
            response.raise_for_status()
            return True, response.json()
        except:
            return False, {"status": "Unhealthy!"}

    def start_assesment(self, questions: list, assessment_config: dict) -> tuple:
        payload = {"questions": questions, "config": assessment_config}
        response = self.base.make_request(
            Endpoints.START_ASSESSEMENT, method="POST", body=payload
        )
        return response.status_code, response.json()

    def next_item(self, answer: bool, previous_index: int, encoded_design: str) -> tuple:
        payload = {
            "answer": answer,
            "previous_index": previous_index,
            "design": encoded_design,
        }
        response = self.base.make_request(
            Endpoints.NEXT_ITEM, method="POST", body=payload
        )
        return response.status_code, response.json()

    def get_design_data(self, encoded_design: str) -> dict:
        payload = {"design": encoded_design}
        response = self.base.make_request(
            Endpoints.GET_DESIGN_DATA, method="POST", body=payload
        )
        return response.json()
