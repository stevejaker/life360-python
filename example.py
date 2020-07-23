from life360 import life360

if __name__ == "__main__":
    # From what I can tell, this has not changed in 3+ years...
    # The token can be omitted if desired. If a token is NOT provided, the below token will be loaded by default.
    token = "cFJFcXVnYWJSZXRyZTRFc3RldGhlcnVmcmVQdW1hbUV4dWNyRUh1YzptM2ZydXBSZXRSZXN3ZXJFQ2hBUHJFOTZxYWtFZHI0Vg=="

    # Email address and password for your life360 account
    email    = "email@address.com"
    password = "super long password"

    # Instantiate the API
    api = life360(token=token, email=email, password=password)

    # Authenticate
    if api.authenticate():

        # Returns a list of circles in json format
        circles =  api.get_all_circles() # Returns a list of circles

        # You can make a single request for full details on a specific circle
        # You have 2 options: locate circle by the id, or by the circle name

        # Option 1 -- Get circle by id:
        id = circles[0]['id'] # For simplicity, I'm using the first circle in the list
        circle = api.get_circle_by_id(id)

        # Option 2 -- Get circle by name:
        # This is just to make it easier to select circles if you know the name, but not the id.
        # Internally, the relationship between circle name and id is stored within the life360 class.
        # This method maps the name to it's id, returning the same data as get_circle_by_id.
        # Soundex is also used to simplify selection by name.
        circle = api.get_circle_by_name(name)
        # Do whatever you want with the data :)

        # BETA: You can also constantly scan your circle repeatedly.
        #     This method is still in beta and is constantly being updated.
        api.scan_circle(id=id)

    else:
        print "Error authenticating"
