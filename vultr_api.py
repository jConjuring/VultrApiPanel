import requests

DEFAULT_TIMEOUT = 15

class VultrAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.vultr.com/v2"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _request(self, method, path, **kwargs):
        try:
            return self.session.request(
                method,
                f"{self.base_url}{path}",
                timeout=DEFAULT_TIMEOUT,
                **kwargs
            )
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def get_plans(self):
        """Fetch plans with monthly cost <= 5 USD."""
        response = self._request("GET", "/plans")
        if not response or response.status_code != 200:
            return []

        def parse_cost(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        all_plans = response.json().get("plans", [])
        affordable_plans = []
        for plan in all_plans:
            cost = parse_cost(plan.get("monthly_cost"))
            if cost is not None and cost <= 5.0:
                affordable_plans.append(plan)

        return sorted(
            affordable_plans,
            key=lambda p: (parse_cost(p.get("monthly_cost")) or 0, p.get("id", ""))
        )

    def get_os_list(self):
        """Fetch OS images."""
        response = self._request("GET", "/os")
        if not response or response.status_code != 200:
            return []
        return response.json().get("os", [])

    def create_instance(self, region, plan, os_id):
        """Create a server instance."""
        data = {
            "region": region,
            "plan": plan,
            "os_id": os_id,
            "enable_ipv6": False,
            "backups": "disabled",
            "ddos_protection": False,
            "activation_email": False
        }

        response = self._request("POST", "/instances", json=data)
        if response and response.status_code == 202:
            return response.json().get("instance", {})
        return None

    def get_instances(self):
        """Fetch all server instances."""
        response = self._request("GET", "/instances")
        if response and response.status_code == 200:
            return response.json().get("instances", [])
        return []

    def get_instance_detail(self, instance_id):
        """Fetch detailed instance info (including password)."""
        response = self._request("GET", f"/instances/{instance_id}")
        if response and response.status_code == 200:
            return response.json().get("instance", {})
        return None

    def reinstall_instance(self, instance_id, os_id=None):
        """Reinstall OS for the instance."""
        if os_id:
            response = self._request(
                "POST",
                f"/instances/{instance_id}/reinstall",
                json={"os_id": os_id}
            )
        else:
            response = self._request("POST", f"/instances/{instance_id}/reinstall")

        if not response:
            return False

        if response.status_code != 204:
            print(f"Reinstall status: {response.status_code}")
            print(f"Reinstall response: {response.text}")
        return response.status_code == 204

    def delete_instance(self, instance_id):
        """Delete a server instance."""
        response = self._request("DELETE", f"/instances/{instance_id}")
        return bool(response and response.status_code == 204)

    def get_regions(self):
        """Fetch available regions."""
        response = self._request("GET", "/regions")
        if not response or response.status_code != 200:
            return []
        regions = response.json().get("regions", [])
        return sorted(regions, key=lambda r: (r.get("city", ""), r.get("id", "")))
