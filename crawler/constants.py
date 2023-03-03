class CategoryContainer:
    POSTULAT = "postulat"
    PROTOKOLL = "protokoll"
    BESCHLUSSANTRAG = "beschlussantrag"
    INTERPELLATION = "interpellation"
    VORLAGE = "vorlage"
    ANTRAG = "antrag"
    BESCHLUSS = "beschluss"
    KLEINE_ANFRAGE = "kleine anfrage"
    MOTION = "motion"


FORCE_OCR_PDF_IDS = set(["4235885", "4235918"])

ROOT_URL = "https://www.schlieren.ch"
ITEM_STORAGE_FOLDER = "./data/item_storage"
PDF_STORAGE_FOLDER = "./data/pdf_storage"
DATAJSON_FILE = "./data/data.json"
ASOFJSON_FILE = "./data/asof.json"
DATAJSON_FILE_FRONTEND = "./frontend/data.json"
ASOFJSON_FILE_FRONTEND = "./frontend/asof.json"
