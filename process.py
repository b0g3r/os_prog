class PropertyError(Exception):
    def __init__(self, message):
        self.message = message

def get_setter_for_positive(var_name, name):
    def setter(inst, val):
        if val > 0:
            inst.__dict__['_'+var_name] = val
        else:
            raise PropertyError("Свойство {} должно быть больше нуля".format(name))
    return property(lambda inst: inst.__dict__.get('_'+var_name), setter)

# TODO: умные мысли: все нужные данные для формул внести в объекты (можно в какой-нибудь словарь), а формулы отдавать красиво через аксцессор (бля, лишь бы не понять эту херню)


class Substance:
    """Вещество"""

    capacity = get_setter_for_positive('capacity', 'теплоёмкость')
    density = get_setter_for_positive('capacity', 'плотность')
    molar_mass = get_setter_for_positive('capacity', 'молярная масса')

    def __init__(self, capacity: float, density: float, molar_mass: float, boil_temp: float):
        self.boil_temp = boil_temp  # температура кипения
        self.molar_mass = molar_mass  # молярная масса
        self.density = density  # плотность
        self.capacity = capacity  # теплоемкость


class Solvent(Substance):
    """Растворяемое"""
    tough = get_setter_for_positive('tough', 'вязкость')

    def __init__(self, capacity: float, density: float, molar_mass: float, boil_temp: float, tough: float):
        super().__init__(capacity, density, molar_mass, boil_temp)
        self.tough = tough  # вязкость


class Solute(Substance):
    """Растворитель"""
    solubility = get_setter_for_positive('solubility', 'растворимость')

    def __init__(self, capacity: float, density: float, molar_mass: float, boil_temp: float, solubility: float,
                 melting_temp: float):
        super().__init__(capacity, density, molar_mass, boil_temp)
        self.melting_temp = melting_temp  # температура плавления
        self.solubility = solubility  # растворимость


class Solution:
    """Раствор"""
    @property
    def start_capacity(self) -> float:
        self._start_capacity = self.solvent.capacity*(1-self.start_conc) + self.solute.capacity*self.start_conc
        return self._start_capacity

    @property
    def final_capacity(self) -> float:
        self._final_capcity = self.solvent.capacity * (1 - self.final_conc) + self.solute.capacity * self.final_conc
        return self._final_capcity

    @property
    def W(self) -> float:
        self._W = self.start_consumption*(1-(self.start_conc/self.final_conc))
        return self._W

    @property
    def Q(self) -> float:
        self._Q = 1.05 * (self.start_consumption * self.start_capacity * (self.final_temp - self.start_temp) +
                       self.W * (self.other['enthalpy'] - self.solvent.capacity * self.final_temp))
        return self._Q

    def __init__(self, solute: Solute, solvent: Solvent, start_conc: float, final_conc: float, start_temp: float,
                 final_temp: float, start_consumption: float):
        # get steam.enthalpy
        self.other = {}
        self.start_consumption = start_consumption
        self.final_temp = final_temp
        self.start_temp = start_temp
        self.final_conc = final_conc
        self.start_conc = start_conc
        self.solvent = solvent
        self.solute = solute


class Steam:
    """Пар"""
    consumption = get_setter_for_positive('consumption', 'расход')

    @property
    def enthalpy(self):
        ent = (2679, 2687, 2696, 2704, 2711, 2718, 2726, 2733, 2740, 2747, 2753, 2765, 2776, 2785, 2792, 2798)
        return ent[int((self.final_temp - 100)/10)-1]*1000

    @property
    def rgp(self) -> float:
        rgp = (2260, 2248, 2234, 2221, 2207, 2194, 2179, 2165, 2150, 2125, 2120, 2089, 2056, 2021, 1984, 1945)
        return rgp[int((self.final_temp-100)/10)-1]*1000

    @property
    def final_consumption(self) -> float:
        return self.other['Q']/(self.rgp * self.x)

    @property
    def D(self) -> float:
        return self.final_consumption / self.other['W']

    def __init__(self, start_temp: float, final_temp: float, consumption: float):
        self.other = {}
        self.final_temp = final_temp
        self.consumption = consumption  # расход
        self.start_temp = start_temp
        self.x = 0.965


class Machine:
    """Аппарат"""
    diameter_pipe = get_setter_for_positive('diameter_pipe', 'диаметр трубы')
    height = get_setter_for_positive('machine_height', 'высота аппарата')
    pipe_height = get_setter_for_positive('pipe_height', 'высота труб')

    @property
    def level(self):
        self._level = (0.26 + 0.0014 * ((self.density + 10 * (self.other['start_conc'] * 100 - 1)) - 1000)) * self.pipe_height
        return self._level

    @property
    def boil_temp(self):
        table_data = [101.1, 102.4, 104.1, 106.4, 109.5, 113.3, 118.2, 124.6, 133.4, 145.0, 160.2, 178.4, 200.2, 226.6,
                      255.5]
        self._boil_temp = table_data[int((self.other['start_conc'] * 100) / 5) - 1]
        return self._boil_temp

    @property
    def F(self):
        self._F = self.other['Q'] / (self.K * (self.other['start_temp'] - self.boil_temp))
        return self._F

    def __init__(self, pipe_height: float, height: float, pipe_diameter: float):
        self.other = {}
        self.K = 240
        self.density = 1007.4
        self.diameter_pipe = pipe_diameter
        self.height = height
        self.pipe_height = pipe_height


