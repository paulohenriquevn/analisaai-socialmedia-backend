"""
Simple script to test the task queue endpoint.
"""
import requests
import time
import json

def main():
    # Test the non-authenticated endpoint
    test_url = "http://localhost:5000/api/social-media/test"
    print(f"Testing endpoint: {test_url}")
    try:
        response = requests.get(test_url)
        print(f"Status code: {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
        
        if response.status_code == 200 and "task_id" in response.json():
            # Check the task status after a moment
            task_id = response.json()["task_id"]
            print(f"\nGot task ID: {task_id}")
            print("Waiting 3 seconds for task to complete...")
            time.sleep(3)
            
            # Check task status
            status_url = f"http://localhost:5000/api/social-media/tasks/{task_id}"
            print(f"Checking task status: {status_url}")
            try:
                status_response = requests.get(status_url)
                print(f"Status code: {status_response.status_code}")
                try:
                    print(json.dumps(status_response.json(), indent=2))
                except:
                    print(status_response.text)
            except Exception as e:
                print(f"Error checking task status: {str(e)}")
    except Exception as e:
        print(f"Error testing task queue: {str(e)}")

if __name__ == "__main__":
    main()