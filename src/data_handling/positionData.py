from baseDataHandling import BaseDataHandling

class PositionDataFactory:
    @staticmethod
    def create(position):
        return PositionData(position)

class PositionData(BaseDataHandling):
    def __init__(self, position):
        super().__init__()
        self.position = position

    def process_data(self):
        # Implement the specific data processing for position data
        pass