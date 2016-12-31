
def get_setter_for_positive(var_name, name):
    def setter(inst, val):
        if val > 0:
            inst.__dict__['_'+var_name] = val
        else:
            raise Exception("Свойство {} должно быть больше нуля".format(name))
    return property(lambda inst: inst.__dict__.get('_'+var_name), setter)

class Substance:
    """Вещество"""

    capacity = get_setter_for_positive('capacity', 'теплоёмкость')
    density = get_setter_for_positive('capacity', 'плотность')
    molar_mass = get_setter_for_positive('capacity', 'молярная масса')

    def __init__(self, capacity: float, density: float, molar_mass: float, temp_boil: float):
        self.temp_boil = temp_boil  # температура кипения
        self.molar_mass = molar_mass  # молярная масса
        self.density = density  # плотность
        self.capacity = capacity  # теплоемкость


class Solvent(Substance):
    """Растворяемое"""
    tough = get_setter_for_positive('tough', 'вязкость')

    def __init__(self, capacity: float, density: float, molar_mass: float, temp_boil: float, tough: float):
        super().__init__(capacity, density, molar_mass, temp_boil)
        self.tough = tough  # вязкость


class Solute(Substance):
    """Растворитель"""
    solubility = get_setter_for_positive('solubility', 'растворимость')

    def __init__(self, capacity: float, density: float, molar_mass: float, temp_boil: float, solubility: float,
                 temp_melting: float):
        super().__init__(capacity, density, molar_mass, temp_boil)
        self.temp_melting = temp_melting  # температура плавления
        self.solubility = solubility  # растворимость


class Solution:
    """Раствор"""
    @property
    def start_capacity(self) -> float:
        return self.solvent.capacity*(1-self.start_conc) + self.solute.capacity*self.start_conc

    @property
    def final_capacity(self) -> float:
        return self.solvent.capacity * (1 - self.final_conc) + self.solute.capacity * self.final_conc

    @property
    def W(self) -> float:
        return self.start_consum*(1-(self.start_conc/self.final_conc))

    def __init__(self, solute: Solute, solvent: Solvent, start_conc: float, final_conc: float, start_temp: float,
                 final_temp: float, start_consum: float):
        self.start_consum = start_consum
        self.final_temp = final_temp
        self.start_temp = start_temp
        self.final_conc = final_conc
        self.start_conc = start_conc
        self.solvent = solvent
        self.solute = solute


class Steam:
    """Пар"""
    consumption = get_setter_for_positive('consumption', 'расход')
    x = 0.965

    @property
    def enthalpy(self):
        ent = (2679, 2687, 2696, 2704, 2711, 2718, 2726, 2733, 2740, 2747, 2753, 2765, 2776, 2785, 2792, 2798)
        return ent[int((self.final_temp - 100)/10)-1]*1000

    @property
    def rgp(self):
        rgp = (2260, 2248, 2234, 2221, 2207, 2194, 2179, 2165, 2150, 2125, 2120, 2089, 2056, 2021, 1984, 1945)
        return rgp[int((self.final_temp-100)/10)-1]*1000

    def get_final_consumption(self, Q: float) -> float:
        return Q/(self.rgp * self.x)

    def get_D(self, Q: float, W: float) -> float:
        return self.get_final_consumption(Q) / W



    def __init__(self, start_temp: float, final_temp: float, consumption: float):
        self.final_temp = final_temp
        self.consumption = consumption  # расход
        self.start_temp = start_temp


class Machine:
    """Аппарат"""
    diameter_pipe = get_setter_for_positive('diameter_pipe', 'диаметр трубы')
    machine_height = get_setter_for_positive('machine_height', 'высота аппарата')
    pipe_height = get_setter_for_positive('pipe_height', 'высота труб')

    def __init__(self, pipe_height: float, machine_height: float, diameter_pipe: float):
        self.diameter_pipe = diameter_pipe
        self.machine_height = machine_height
        self.pipe_height = pipe_height


