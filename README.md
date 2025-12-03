# CS 179M Projects

**Authors**

[![Static Badge](https://img.shields.io/badge/Xiyuan%20Wu-path?style=for-the-badge&color=%2387CEEB)](https://github.com/XiyuanWu)
[![Static Badge](https://img.shields.io/badge/Akhilesh%20Genneri-path?style=for-the-badge&color=%2390EE90)]()
[![Static Badge](https://img.shields.io/badge/Bryan%20Duan-path?style=for-the-badge&color=%23CBC3E3)]()
[![Static Badge](https://img.shields.io/badge/Harchet%20Singh-path?style=for-the-badge&color=%23FFFF00)]()

## Project 1-2: Drone Path

### Abstract

There are 1.4 million acres of almonds in the US, creating $19.6 billion in revenue. However, there are many insects (eg, Navel Orangeworm) that are causing damage to those almonds. On average, approximately 20% of almond damage is caused by insects, every in 1% damage, resulting in a $100 million loss. 

To address this issue, we can prevent insect damage to almonds by spraying pesticides. Lucky, in the 20th century, technology has advanced to the point where we can use drones to automatically spray pesticides. 

Inside a field, there are many points where the drone needs to spray pesticides, and it must spray pesticides at every point. To enable the drone to travel the shortest distance possible, this project develops an algorithm to solve this issue. 


### Project 1: Compute Drone Path

This is a classic Traveling Salesman Problem (TSP). Given a list of points (X, Y) with no more than 256 elements, we need to develop an algorithm that starts and ends with the first point. The goal for this project is to minimize the travel distance that covers all points.

To minimize drone travel distance, as explained in the lecture, we are developing 2 algorithms to solve this:
1. Random Search
2. Nearest Neighbor with Early Abandoning

However, this algorithm does not guarantee that solutions are optimal.


### Project 2: Clustering Compute Drone Path

Build from Project 1: Instead of no more than 256 points in a particular area, there are more points given. From Project 1, we need to apply K-means, one of the popular ML algorithms, to minimize the total distance the drone travels.

## Project 3: Balance Ship Container

### Abstract
Mr.Keogh owns a single port in Long Beach. However, he does not own any ships, trucks, or containers. Instead, this port will service those ships by getting paid. 

Before a ship leaves the port, cranes need to balance the containers inside the ship. The port can only service one ship at a time. To maximize profits, the crane should make the fewest moves to balance the container as much as possible: the more ship it can balance, the more profit can be made. This project explores various algorithms to balance them.

Mr.Keogh is looking to take less time to earn more profits; however, each move takes 1 minute. That is equal to taking fewer moves for this project.

### Problem Specification

This project focuses on balancing up to 16 containers placed on an 8×12 ship grid that includes unavailable spaces and layout constraints. Containers can only be moved if no container sits above them, movement outside the grid is allowed only one row above, and unavailable spaces cannot be crossed. A crane positioned at the top center performs all moves, and the total movement distance must be calculated as containers are relocated. The goal is to develop an algorithm that redistributes containers so that the ship’s left and right sides differ in total weight by no more than 10%, while achieving this balance using the fewest moves possible.
