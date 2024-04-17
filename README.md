# Attraction Park Simulation
## Overview
The Attraction Park Simulation is a Python project that simulates the experience of visitors at an amusement park. It utilizes parallel computing techniques to simulate multiple visitors concurrently, each navigating through a series of attractions within the park.

## How it Works
The simulation consists of several components:

Attractions: Each attraction is represented as a class, implementing the AbstractHandler interface. Attractions have properties such as capacity (maximum number of visitors allowed) and visit duration (time spent by each visitor at the attraction).
Customers: Visitors to the park are represented as instances of the Customer class, each with a unique identifier.
ThreadPoolExecutor: Concurrent visitors are managed using a ThreadPoolExecutor, allowing multiple customers to visit attractions simultaneously.
Simulation Logic: The simulate_park_visit function orchestrates the park visit for each customer. Customers navigate through a chain of attractions, visiting each attraction in a random order.
Concurrency and Synchronization: To ensure thread safety, the simulation employs locks and semaphores to control access to shared resources, such as the attractions' capacity limits.

## Future Improvements
The Attraction Park Simulation serves as a foundational framework for simulating visitor experiences in various amusement park scenarios. Potential improvements and extensions include:

Enhanced Realism: Incorporating more realistic visitor behavior and attraction interactions.
Dynamic Attractions: Adding the ability to dynamically add or remove attractions during the simulation.
Customizable Parameters: Allowing users to specify custom parameters for attractions, such as capacity, visit duration, and probability of visit.
