#!/usr/bin/env python3
"""
Load Test Script for FastAPI Log Ingestion System

This script performs a load test on the FastAPI log ingestion system by:
1. Creating multiple log entries using concurrent POST requests
2. Retrieving logs using concurrent GET requests
3. Measuring response times and reporting performance metrics
"""

import asyncio
import time
import random
import statistics
from datetime import datetime, timedelta
import aiohttp
import argparse


async def post_log(session, url, service_name, message):
    """Send a POST request to create a log entry"""
    start_time = time.time()
    payload = {
        "service_name": service_name,
        "message": message
    }
    
    async with session.post(url, json=payload) as response:
        await response.json()
        end_time = time.time()
        return end_time - start_time


async def get_logs(session, url, params=None):
    """Send a GET request to retrieve logs with optional parameters"""
    start_time = time.time()
    
    async with session.get(url, params=params) as response:
        await response.json()
        end_time = time.time()
        return end_time - start_time


async def run_load_test(base_url, num_requests, concurrency):
    """Run the load test with specified parameters"""
    post_url = f"{base_url}/log"
    get_url = f"{base_url}/log"
    
    # List of service names to use in the test
    services = ["auth-service", "user-service", "payment-service", 
                "notification-service", "data-service"]
    
    # List of sample log messages
    messages = [
        "User login successful",
        "Failed login attempt",
        "Payment processed",
        "User profile updated",
        "Data sync completed",
        "Password reset requested",
        "New user registered",
        "Session expired",
        "API rate limit exceeded",
        "Database backup completed"
    ]
    
    # Results storage
    post_times = []
    get_times = []
    
    # Create a limited number of connections to be reused
    connector = aiohttp.TCPConnector(limit=concurrency)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        print(f"Starting load test with {num_requests} requests at concurrency level {concurrency}")
        print("-" * 80)
        
        # Phase 1: Creating logs with POST requests
        print(f"Phase 1: Sending {num_requests} POST requests...")
        post_tasks = []
        
        for _ in range(num_requests):
            service = random.choice(services)
            message = random.choice(messages)
            task = asyncio.create_task(post_log(session, post_url, service, message))
            post_tasks.append(task)
        
        # Wait for all POST tasks to complete
        post_results = await asyncio.gather(*post_tasks)
        post_times.extend(post_results)
        
        print(f"Phase 1 complete. Created {len(post_results)} log entries.")
        print("-" * 80)
        
        # Phase 2: Retrieving logs with GET requests
        print(f"Phase 2: Sending {num_requests} GET requests...")
        get_tasks = []
        
        # Create various GET requests:
        # 1. Get all logs
        # 2. Filter by service name
        # 3. Filter by time range
        
        # Some requests with no filters
        for _ in range(num_requests // 3):
            task = asyncio.create_task(get_logs(session, get_url))
            get_tasks.append(task)
        
        # Some requests filtered by service
        for _ in range(num_requests // 3):
            service = random.choice(services)
            params = {"service_name": service}
            task = asyncio.create_task(get_logs(session, get_url, params))
            get_tasks.append(task)
        
        # Some requests filtered by time range
        for _ in range(num_requests - len(get_tasks)):
            now = datetime.utcnow()
            start_time = (now - timedelta(hours=random.randint(1, 24))).isoformat()
            end_time = now.isoformat()
            params = {"start_time": start_time, "end_time": end_time}
            task = asyncio.create_task(get_logs(session, get_url, params))
            get_tasks.append(task)
        
        # Wait for all GET tasks to complete
        get_results = await asyncio.gather(*get_tasks)
        get_times.extend(get_results)
        
        print(f"Phase 2 complete. Retrieved logs with {len(get_results)} requests.")
        print("-" * 80)
    
    # Calculate and display metrics
    print("\nPerformance Metrics:")
    print("-" * 80)
    
    # POST metrics
    print("\nPOST /log Metrics:")
    print(f"Total requests: {len(post_times)}")
    print(f"Min response time: {min(post_times):.6f} seconds")
    print(f"Max response time: {max(post_times):.6f} seconds")
    print(f"Average response time: {sum(post_times) / len(post_times):.6f} seconds")
    print(f"Median response time: {statistics.median(post_times):.6f} seconds")
    print(f"Requests per second: {len(post_times) / sum(post_times):.2f}")
    
    # GET metrics
    print("\nGET /log Metrics:")
    print(f"Total requests: {len(get_times)}")
    print(f"Min response time: {min(get_times):.6f} seconds")
    print(f"Max response time: {max(get_times):.6f} seconds")
    print(f"Average response time: {sum(get_times) / len(get_times):.6f} seconds")
    print(f"Median response time: {statistics.median(get_times):.6f} seconds")
    print(f"Requests per second: {len(get_times) / sum(get_times):.2f}")
    
    # Overall metrics
    all_times = post_times + get_times
    print("\nOverall Metrics:")
    print(f"Total requests: {len(all_times)}")
    print(f"Min response time: {min(all_times):.6f} seconds")
    print(f"Max response time: {max(all_times):.6f} seconds")
    print(f"Average response time: {sum(all_times) / len(all_times):.6f} seconds")
    print(f"Median response time: {statistics.median(all_times):.6f} seconds")
    print(f"Requests per second: {len(all_times) / sum(all_times):.2f}")


def main():
    parser = argparse.ArgumentParser(description="Load test for FastAPI Log Ingestion System")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the FastAPI server")
    parser.add_argument("--requests", type=int, default=100, help="Number of requests to send")
    parser.add_argument("--concurrency", type=int, default=10, help="Number of concurrent requests")
    
    args = parser.parse_args()
    
    # Run the load test
    asyncio.run(run_load_test(args.url, args.requests, args.concurrency))


if __name__ == "__main__":
    main()
