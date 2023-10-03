import json

from faker import Faker
from locust import TaskSet, task, HttpUser, between

from service.contracts import OrderEncoder, OrderForm

fake = Faker()


class UserBehavior(TaskSet):
    def __init__(self, parent):
        super(UserBehavior, self).__init__(parent)

        self.token = ""
        self.email = ""
        self.password = ""

    def on_start(self):
        self.email = fake.email()
        self.password = fake.password()
        name = fake.name()
        params = {"email": self.email, "password": self.password, "name": name}
        response = self.client.post("/register", json=params)
        self.token = response.json().get("access_token")

    @task(1)
    def login(self):
        params = {"username": self.email, "password": self.password}
        response = self.client.post("/login", data=params)
        self.token = response.json().get("access_token")

    @task(3)
    def get_user(self):
        self.client.get("/me", headers={"Authorization": f"Bearer {self.token}"})

    @task(1)
    def create_order(self):
        order_form = [OrderForm(menu_position_id=2, count=2), OrderForm(menu_position_id=5, count=3)]
        self.client.post("/order", headers={"Authorization": f"Bearer {self.token}"},
                         data=json.dumps(order_form, cls=OrderEncoder))

    @task(2)
    def get_orders(self):
        self.client.get("/orders", headers={"Authorization": f"Bearer {self.token}"})


class WebsiteUser(HttpUser):
    wait_time = between(3, 5)
    tasks = [UserBehavior]
