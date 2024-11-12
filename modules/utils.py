def get_eagletrt_email(email: str) -> str:
    username = email.split('@')[0].lower()
    return f"{username}@eagletrt.it"


def orelab_entrata() -> str:
    return """
    <html>
    <head>
        <title>Entrata Laboratorio</title>
    </head>
    <body>
        <h1>Benvenuto/a :)</h1>
        <p>La tua entrata è stata registrata correttamente.</p>
    </body>
    </html>
    """


def orelab_uscita(ore: int) -> str:
    return f"""
    <html>
    <head>
        <title>Uscita Laboratorio</title>
    </head>
    <body>
        <h1>Ciao :(</h1>
        <p>La tua uscita è stata registrata correttamente.</p>
        <p>Sei rimasto/a in laboratorio per {ore} ore.</p>
    </body>
    </html>
    """
