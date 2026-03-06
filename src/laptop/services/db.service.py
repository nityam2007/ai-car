class DbService:
  def __init__(self):
    self.client = MongoClient(os.getenv("MONGO_URI"))

  def get_collection(self, collection_name):
    