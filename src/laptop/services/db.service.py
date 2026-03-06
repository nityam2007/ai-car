class DbService:
  def __init__(self):
    self.client = MongoClient(os.getenv("MONGO_URI"))
