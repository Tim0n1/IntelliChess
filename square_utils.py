class Square:
    def __init__(self, A, B, C, D, square_name: tuple):
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        self.square_name = square_name

    def find_center(self):
        x1, y1 = self.A.x, self.A.y
        x2, y2 = self.C.x, self.C.y
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        return int(x), int(y)

    def square_name_str(self):
        a = str(self.square_name[0])
        b = str(self.square_name[1])
        return a + b

