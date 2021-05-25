User Login App:

Backend APIs:
    1. Login API
    2. Signup API
    3. Profile API
    4. Logout API

Login API
    Login with username and password.
    Make sure the session is valid only for 5 minutes. Ideally make the TTL as configurable.
Signup API
    Create a new user with username, password, email, phone number.
    Validations:
    Username is mandatory
    Username max length should be 8
    Password must contain at least one character, one number and any one of these
    (underscore, hyphen, hash)
    Password max length should be 6
    Email should have @ and . Ex. a@b.c
    Phone Number must be a valid Indian Cell phone number. Ex. 9876543210
Profile API
    Only logged in user should be able to see their profile.
Logout API
    Clear out the session, so that the user cannot view their profile