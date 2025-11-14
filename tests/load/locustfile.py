"""
Configuration file for load testing with Locust
"""
from locust import HttpUser, task, between


class FastAPIUser(HttpUser):
    """Simulated user for load testing"""
    wait_time = between(1, 3)  # Wait between 1 and 3 seconds between requests
    
    @task
    def hello_world(self):
        """Test root endpoint"""
        self.client.get("/")
    
    @task(2)
    def health_check(self):
        """Test health check endpoint (more frequent)"""
        self.client.get("/health")

