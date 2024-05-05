names = {
    "Athletico-PR": ["Athletico Paranaense"],
    "Atlético-GO": ["Atlético GO", "Atlético Goianiense"],
    "Atlético-MG": ["Atlético Mineiro", "Atletico Mineiro", "Atlético MG"],
    "Bahia": ["Bahia BA"],
    "Botafogo": ["Botafogo-RJ", "Botafogo FR RJ"],
    "Corinthians": [],
    "Criciúma": ["Criciuma"],
    "Cruzeiro": [],
    "Cuiabá": ["Cuiaba", "Cuiabá EC"],
    "Flamengo": [],
    "Fluminense": [],
    "Fortaleza": [],
    "Grêmio": ["Gremio"],
    "Internacional": [],
    "Juventude": [],
    "Palmeiras": [],
    "Bragantino": ["RB Bragantino"],
    "São Paulo": ["Sao Paulo"],
    "Vasco": ["Vasco da Gama"],
    "Vitória": ["Vitoria BA"],
}

def rename(name):
    for key, values in names.items():
        if name in values:
            return key
    return name