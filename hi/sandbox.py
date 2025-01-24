class Snowmobile:
    def __init__(self, make, model, track_size, paddle_length):
        self.make = make
        self.model = model
        self.track_size = track_size
        self.paddle_length = paddle_length

tyson = Snowmobile("Ski-Doo", "Lynx", 164, 3)
ryan = Snowmobile("Polaris", "Khaos", 155, 2.75)

print(tyson, ryan)