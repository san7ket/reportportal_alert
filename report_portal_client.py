import requests
import logging
from typing import Dict, List


class ReportPortalClient:
    def __init__(self, base_url, token, verify_ssl=True):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.verify_ssl = verify_ssl

    def fetch_launch_ids(self, project_name: str, filters: Dict[str, str]) -> List[str]:
        """
        Fetch launch IDs with given filters.
        """
        launches_endpoint = f"{self.base_url}/api/v1/{project_name}/launch"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        response = requests.get(
            launches_endpoint, headers=headers, params=filters, verify=self.verify_ssl
        )
        response.raise_for_status()

        # Process the response content
        launches = response.json().get("content", [])
        return [launch["id"] for launch in launches if "id" in launch]

    def fetch_suites(self, project_name: str, launch_id: str) -> List[Dict]:
        suites_endpoint = f"{self.base_url}/api/v1/{project_name}/item"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        params = {
            "filter.eq.launchId": launch_id,
            "filter.eq.type": "SUITE",
            "page.size": 100,
        }
        logging.info(f"Fetching suites with params: {params}")
        response = requests.get(
            suites_endpoint, headers=headers, params=params, verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json().get("content", [])

    def fetch_tests(
        self,
        project_name: str,
        launch_id: str,
        suite_id: str,
        test_name_filter: str = None,
    ) -> List[Dict]:
        tests_endpoint = f"{self.base_url}/api/v1/{project_name}/item"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        params = {
            "filter.eq.launchId": launch_id,
            "filter.eq.parentId": suite_id,
            "filter.in.status": "FAILED",
            "page.size": 100,
        }
        logging.info(f"Fetching tests with params: {params}")
        response = requests.get(
            tests_endpoint, headers=headers, params=params, verify=self.verify_ssl
        )
        response.raise_for_status()
        tests = response.json().get("content", [])
        if test_name_filter:
            tests = [
                test
                for test in tests
                if test_name_filter.lower() in test.get("name", "").lower()
            ]
        return tests
