def get_eagletrt_email(email: str) -> str:
    username = email.split('@')[0]
    return f"{username}@eagletrt.it"
