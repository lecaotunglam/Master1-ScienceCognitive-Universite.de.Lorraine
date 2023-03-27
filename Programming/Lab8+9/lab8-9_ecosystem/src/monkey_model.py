import utils
class Monkey:
    """A monkey."""

    def __init__(self, fur_color: str, size, weight, species=''):
        self.species = species
        if not utils.check_hexacolor(fur_color):
            raise ValueError
        else:
            self.fur_color = fur_color
        self.size = size
        self.weight = weight

    def __str__(self):
        result = str(self.species) + ' ' + str(self.fur_color) + ' ' + str(self.size) + ' ' + str(self.weight)
        return result

    def __repr__(self):
        result = str(self.species) + str(self.fur_color) + str(self.size) + str(self.weight)
        return result

    def compute_bmi(self):
        bmi = self.weight / (self.size * self.size)
        return bmi
