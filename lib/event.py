class event():
   def __init__(self):
      print(f"Konstruktur in {__file__}")

   def run(self):
      print(f"default run() handler {__file__}")

   def __del__(self):
      print(f"DeKonst in {__file__}")

