"""
Test script for task queue endpoints.
"""
import requests
import json
import sys
import os

BASE_URL = "http://localhost:5000/api"

def login(username, password):
    """Login to get an access token."""
    login_url = f"{BASE_URL}/auth/login"
    response = requests.post(
        login_url,
        json={"username": username, "password": password}
    )
    
    if response.status_code != 200:
        print(f"Login failed with status {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    return data["tokens"]["access_token"]

def test_queue_info(token):
    """Test the queue info endpoint."""
    url = f"{BASE_URL}/social_media/tasks/tasks/queue-info"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    
    print(f"Queue Info: Status Code {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print(response.text)
    
    return response.status_code == 200

def test_tasks_list(token):
    """Test the tasks list endpoint."""
    url = f"{BASE_URL}/social_media/tasks/tasks"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    
    print(f"Tasks List: Status Code {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print(response.text)
    
    return response.status_code == 200

def test_async_sync(token, influencer_id=1):
    """Test the async sync endpoint."""
    url = f"{BASE_URL}/social_media/tasks/async/sync-influencer/{influencer_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(url, headers=headers)
    
    print(f"Async Sync: Status Code {response.status_code}")
    if response.status_code in [200, 202]:
        data = response.json()
        print(json.dumps(data, indent=2))
        return data.get("task_id")
    else:
        print(response.text)
    
    return None

def test_task_status(token, task_id):
    """Test the task status endpoint."""
    url = f"{BASE_URL}/social_media/tasks/tasks/{task_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    
    print(f"Task Status: Status Code {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print(response.text)
    
    return response.status_code == 200

def main():
    if len(sys.argv) < 3:
        print("Usage: python test_queue_endpoints.py <username> <password>")
        return
        
    username = sys.argv[1]
    password = sys.argv[2]
    
    token = login(username, password)
    if not token:
        print("Login failed. Exiting.")
        return
    
    print("Testing task queue endpoints...")
    test_queue_info(token)
    test_tasks_list(token)
    
    task_id = test_async_sync(token)
    if task_id:
        print(f"Created task with ID: {task_id}")
        test_task_status(token, task_id)
    
    print("Testing complete.")

if __name__ == "__main__":
    main()