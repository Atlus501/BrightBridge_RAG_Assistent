import requests

endpoints = ["/rag/respond", "/context/store", "/context/retrieve"]
payloads = [
    {
        "past_conv": [],
        "prompt" : "What are some good relationship therapy options?"
    },

    {
        "session_id" : None,
        "password": "soidfjskfdkwortiwurtxkvj",
        "actor_id": "test-user",
        "conv_to_be_saved": [],
    }
]

def test_server_endpoint(api_endpoint, payload):
  try:
    host_ip = "127.0.0.1"
    host_port = 8080
    r = requests.post(f"http://{host_ip}:{host_port}{api_endpoint}", json=payload)
    print(r.json())
    return r
  except Exception as e:
    print(e)
    return {"error" : str(e)}

#the part that tests the response endpoint
r = test_server_endpoint(endpoints[0], payloads[0])

#adjusting the nodes to save the response
payloads[1]['conv_to_be_saved'] = ["User: What are some good relationship therapy options?\n Assistant: Based on the context provided, here are some good relationship therapy options:  *   **Emotionally-Focused-Couple-\n"]

r = test_server_endpoint(endpoints[1], payloads[1])

#adjusting the nodes to retrieve the resposne
payloads[1]['session_id'] = r.json()['session_id']

r = test_server_endpoint(endpoints[2], payloads[1])