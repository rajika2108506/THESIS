# field_config.py

RAG_FIELDS = [
    "ID_PARTE_OFFESA",
    "ID_INDAGATO",
    "SESSO_INDAGATO",
    "FASCIA_ETA_INDAGATO",
    "FASCIA_ETA_PARTE_OFFESA",
    "TIPO_RAPPORTO_AUTORE_VITTIMA",
    "TIPO_RUOLO_AUTORE_VITTIMA",
    "LUOGO_COMMESSO_REATO",
    "PROVINCIA_COMMESSO_REATO",
    "TIPO_ARMA",
    "REATO",
    "DESCRIZIONE_RICHIESTA",
    "DESCRIZIONE_ESITO"
]

METADATA_FIELDS = [
    "DISTRETTO",
    "ID_PROCED",
    "TIPOLOGIA_PROCEDIMENTI",
    "TIPOLOGIA_UFFICIO",
    "DATA_PRIMA_ISCRIZIONE",
    "DATA_ISCRIZIONE",
    "DATA_DEFINIZIONE",
    "STATO_NASCITA_INDAGATO",
    "PROVINCIA_NASCITA_INDAGATO"
]


FIELD_SECTION_MAP = {
    "ID_PARTE_OFFESA": "FATTO",
    "ID_INDAGATO": "FATTO",
    "SESSO_INDAGATO": "FATTO",
    "FASCIA_ETA_INDAGATO": "FATTO",
    "FASCIA_ETA_PARTE_OFFESA": "FATTO",
    "TIPO_RAPPORTO_AUTORE_VITTIMA": "FATTO",
    "TIPO_RUOLO_AUTORE_VITTIMA": "FATTO",
    "LUOGO_COMMESSO_REATO": "FATTO",
    "PROVINCIA_COMMESSO_REATO": "FATTO",
    "TIPO_ARMA": "FATTO",

    "REATO": "DIRITTO",
    "DESCRIZIONE_RICHIESTA": "DIRITTO",

    "DESCRIZIONE_ESITO": "PQM",
    "DATA_DEFINIZIONE": "PQM"
}

FIELD_QUERIES = {
    "ID_PARTE_OFFESA": "Who is the victim or injured party in this case?",
    "ID_INDAGATO": "Who is the accused or defendant?",
    "SESSO_INDAGATO": "What is the gender of the accused?",
    "FASCIA_ETA_INDAGATO": "What is the age range of the accused?",
    "FASCIA_ETA_PARTE_OFFESA": "What is the age range of the victim?",
    "TIPO_RAPPORTO_AUTORE_VITTIMA": "What is the relationship between the offender and the victim?",
    "TIPO_RUOLO_AUTORE_VITTIMA": "What role does the offender have with respect to the victim?",
    "LUOGO_COMMESSO_REATO": "Where did the crime take place?",
    "PROVINCIA_COMMESSO_REATO": "In which province did the crime occur?",
    "TIPO_ARMA": "Was a weapon used in the crime?",
    "REATO": "What crime is being judged?",
    "DESCRIZIONE_RICHIESTA": "What request was made by the prosecution or defense?",
    "DESCRIZIONE_ESITO": "What was the final outcome of the case?"
}

