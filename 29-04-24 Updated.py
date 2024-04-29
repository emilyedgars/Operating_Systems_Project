from __future__ import annotations
import concurrent.futures
import threading
import time
import random
import queue
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Optional, List
import mysql.connector
from faker import Faker

# Previous code
class Handler(ABC):
    @abstractmethod
    def set_next(self, handler: Handler) -> Handler:
        pass

    @abstractmethod
    def handle(self, request) -> Optional[str]:
        pass

class AbstractHandler(Handler):
    _next_handler: Optional[Handler] = None

    def set_next(self, handler: Handler) -> Handler:
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, customer: Customer) -> Optional[str]:
        if self._next_handler:
            return self._next_handler.handle(customer)
        return None

class Customer:
    id_counter = 0  # Static variable to track the last assigned ID

    def __init__(self, customer_id):
        Customer.id_counter += 1
        self.id = Customer.id_counter
        self.priority_queue = False if random.random() < 0.7 else True  # 70% chance to be a normal customer
        self.spending_money = random.randint(5, 20)  # Random spending money for the shop


class Attraction(AbstractHandler):
    def __init__(self, capacity: int, duration: int):
        self.capacity = capacity
        self.current_capacity = 0
        self.lock = threading.Lock()
        self.duration = duration
        self.normal_price = 10
        self.entry_time = 0
        self.exit_time = 0
        self.priority_price = 25
        self.visits_count = 0  # Count of visits to this attraction
        self.priority_queue = queue.Queue()
        self.normal_queue = queue.Queue()

    def process_customer(self, customer: Customer):
        customer_type = "Priority" if customer.priority_queue else "Normal"
        ticket_price = self.priority_price if customer.priority_queue else self.normal_price
        with self.lock:
            if self.current_capacity < self.capacity:
                self.current_capacity += 1
                self.visits_count += 1
            else:
                print(f"{self.__class__.__name__} is full. Please wait until the session is over...")
                return "Capacity full"

        self.entry_time = time.time()
        entry_time_str = datetime.fromtimestamp(self.entry_time).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{customer_type} customer {customer.id} entered the {self.__class__.__name__} at {entry_time_str}")

        time.sleep(self.duration)  # Simulate the customer's visit

        self.exit_time = time.time()
        exit_time_str = datetime.fromtimestamp(self.exit_time).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{customer_type} customer {customer.id} left the {self.__class__.__name__} at {exit_time_str}")

        visit_duration = self.exit_time - self.entry_time
        print(f"Customer {customer.id} spent {visit_duration:.2f} seconds at the {self.__class__.__name__}")

    def handle(self, customer: Customer) -> str:
        queue_used = self.priority_queue if customer.priority_queue else self.normal_queue
        queue_used.put(customer)

        # Check if there are priority customers waiting
        if not self.priority_queue.empty():
            while not self.priority_queue.empty():
                priority_customer = self.priority_queue.get()
                self.process_customer(priority_customer)
        else:
            # If no priority customers waiting, process normal customers
            while not self.normal_queue.empty():
                normal_customer = self.normal_queue.get()
                self.process_customer(normal_customer)

        return super().handle(customer)

class WaterPark(Attraction):
    def __init__(self):
        super().__init__(capacity=10, duration=6)
        self.name = "WaterPark"

class RollerCoaster(Attraction):
    def __init__(self):
        super().__init__(capacity=3, duration=3)
        self.name = "RollerCoaster"

class Shop(Attraction):
    def __init__(self):
        super().__init__(capacity=8, duration=7)
        self.total_sales = 0  # To track additional spending in the shop
        self.name = "Shop"

    def process_customer(self, customer: Customer):
        super().process_customer(customer)
        additional_spending = customer.spending_money
        with self.lock:
            self.total_sales += additional_spending
        print(f"Customer {customer.id} spent an additional ${additional_spending:.2f} in the shop.")

class FoodTruck(Attraction):
    def __init__(self):
        super().__init__(capacity=5, duration=2)
        self.food_price = 5  # Flat rate for simplicity
        self.name = "FoodTruck"

    def process_customer(self, customer: Customer):
        super().process_customer(customer)
        with self.lock:
            self.total_normal_profit += self.food_price
            self.total_normal_clients += 1
        print(f"Customer {customer.id} bought food for ${self.food_price:.2f}.")

class FerrisWheel(Attraction):
    def __init__(self):
        super().__init__(capacity=6, duration= 8)
        self.name = "FerrisWheel"

class ArcadeGames(Attraction):
    def __init__(self):
        super().__init__(capacity=4, duration=5)
        self.name = "ArcadeGames"

class CircusShow(Attraction):
    def __init__(self):
        super().__init__(capacity=15, duration=10)
        self.name = "CircusShow"

# New code
class CustomerDatabase:
    def __init__(self):
        self.fake = Faker()

    def generate_customers(self, num_customers: int) -> list[Customer]:
        customers = []
        for _ in range(num_customers):
            customer_id = self.fake.uuid4().split('-')[0]  # Using first part of UUID as ID
            customers.append(Customer(customer_id))
        return customers

def simulate_park_visit(attractions: List[Attraction], customer: Customer):
    # Determine how many attractions the customer will visit
    num_attractions_to_visit = random.randint(1, len(attractions))

    # Randomly select attractions for the customer to visit
    attractions_to_visit = random.sample(attractions, num_attractions_to_visit)

    # Add customer to the appropriate queue
    for attraction in attractions_to_visit:
        if customer.priority_queue:  # This condition should check if the customer is a priority customer
            attraction.priority_queue.put(customer)
        else:
            attraction.normal_queue.put(customer)

    # Visit each selected attraction
    for attraction in attractions_to_visit:
        attraction.handle(customer)

if __name__ == "__main__":
    num_customers = 20

    # Create attractions and customers
    attractions = [WaterPark(), RollerCoaster(), Shop(), FerrisWheel(), ArcadeGames(), CircusShow(), FoodTruck()]
    customer_db = CustomerDatabase()
    customers = customer_db.generate_customers(num_customers)

    # Simulate park visits
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for customer in customers:
            executor.submit(simulate_park_visit, attractions, customer)

    # Wait for all threads to complete
    executor.shutdown()

    # Calculate and print summary statistics
    total_normal_clients = sum(len(attraction.normal_queue.queue) for attraction in attractions)
    total_priority_clients = sum(len(attraction.priority_queue.queue) for attraction in attractions)
    total_normal_profit = total_normal_clients * 10
    total_priority_profit = total_priority_clients * 25
    shop_sales = next((attr.total_sales for attr in attractions if isinstance(attr, Shop)), 0)
    total_park_profit = total_normal_profit + total_priority_profit + shop_sales


    print("\nSummary:::")
    print(f"Total normal clients: {total_normal_clients}")
    print(f"Total priority clients: {total_priority_clients}")
    print(f"Total normal profit: ${total_normal_profit:.2f}")
    print(f"Total priority profit: ${total_priority_profit:.2f}")
    print(f"Total shop sales: ${shop_sales:.2f}")
    print(f"Total park profit: ${total_park_profit:.2f}")

    # Determine the most visited attraction
    print("\nCalculating most visited attraction")
    most_visited = max(attractions, key=lambda x: x.visits_count, default=None)
    if most_visited:
        print(f"{most_visited.__class__.__name__} is the most visited attraction with {most_visited.visits_count} visits.")