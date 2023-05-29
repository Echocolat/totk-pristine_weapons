import struct
import json
import matplotlib.pyplot as plt
import byml

with open('statues.json') as json_file:
    statues = json.loads(json_file.read())

def _get_unpack_endian_char(be: bool):
    return '>' if be else '<'

class Beco:
    MAGIC = b'\x00\x11\x22\x33'
    HEADER_SIZE = 0x10

    def __init__(self, data: bytearray) -> None:
        magic = data[0:4]
        self._be = False
        if magic == Beco.MAGIC:
            self._be = True
        elif magic == bytes(reversed(Beco.MAGIC)):
            self._be = False
        else:
            raise ValueError('Unknown magic')

        self._d = data
        self._num_rows = self._u32(4)
        self._divisor = self._u32(8)

    def get_raw_data(self) -> bytearray:
        return self._d

    def get_num_rows(self) -> int:
        return self._num_rows
    def get_divisor(self) -> int:
        return self._divisor

    def get_row_offset(self, z: float) -> int:
        row = int(z + 4000.0)
        if row > self._num_rows - 2:
            row = self._num_rows - 2
        return self._get_row_offset(row)

    def _get_row_offset(self, row: int) -> int:
        return Beco.HEADER_SIZE + 4*self._num_rows + 2*self._u32(Beco.HEADER_SIZE + row * 4)

    def get_data(self, x: float, z: float) -> int:
        x_ = int(x + 5000.0)
        row_offset = self.get_row_offset(z)
        end_row_offset = self.get_row_offset(z + 1)

        offset = row_offset
        length = 0
        while offset < end_row_offset:
            segment_data = self._u16(offset)
            segment_length = self._u16(offset + 2)
            length += segment_length
            if x_ < length:
                return segment_data
            offset += 4

        return -1

    def replace_data(self, old_data: int, new_data: int) -> None:
        for i in range(self._num_rows - 2):
            row_offset = self._get_row_offset(i)
            end_row_offset = self._get_row_offset(i + 1)

            offset = row_offset
            while offset < end_row_offset:
                segment_data = self._u16(offset)
                if segment_data == old_data:
                    self._write_u16(offset, new_data)
                offset += 4

    def _write_u16(self, offset: int, v: int) -> None:
        struct.pack_into(_get_unpack_endian_char(self._be) + 'H', self._d, offset, v)
    def _u16(self, offset: int) -> int:
        return struct.unpack_from(_get_unpack_endian_char(self._be) + 'H', self._d, offset)[0]
    def _u32(self, offset: int) -> int:
        return struct.unpack_from(_get_unpack_endian_char(self._be) + 'I', self._d, offset)[0]
    

def get_coordinate_couples(weapon_name):

    area_list = []

    with open('MinusField.ecocat.byml', 'rb') as map_file:
        parser = byml.Byml(bytes(map_file.read()))
        ecosystem_data = parser.parse()

    for area in ecosystem_data:                 # c'est des dicos
        if weapon_name in [area['NotDecayedLargeSwordList'][i]['name'] for i in range(len(area['NotDecayedLargeSwordList']))] or weapon_name in [area['NotDecayedSmallSwordList'][i]['name'] for i in range(len(area['NotDecayedSmallSwordList']))] or weapon_name in [area['NotDecayedSpearList'][i]['name'] for i in range(len(area['NotDecayedSpearList']))]:
            area_list.append(area['AreaNumber'])

    with open('MinusField.beco', 'rb') as file:
        beco = Beco(file.read())

    with open('statues.json') as json_file:
        statues = json.loads(json_file.read())

    coordinate_list = []

    for statue in statues:
        if beco.get_data(statue['Translate'][0], statue['Translate'][2]) in area_list:
            coordinate_list.append([statue['Translate'][0], statue['Translate'][2]])

    coordinate_list = list(set(tuple(i) for i in coordinate_list))

    x_values = [stuff[0] for stuff in coordinate_list]
    z_values = [-1*stuff[1] for stuff in coordinate_list]
    colors = ['#000000' for _ in range(len(x_values))]
    sizes = [8 for _ in range(len(x_values))]
    plt.figure(dpi=1800)
    plt.axis('off')
    plt.xlim([-5001, 5001])
    plt.ylim([-4001, 4001])
    plt.scatter(x_values, z_values, c=colors, s=sizes, linewidths=0)
    plt.savefig(weapon_name + '.png', bbox_inches = 'tight', pad_inches = 0, transparent=True)

def all_maps():

    for weapon in ["Weapon_Sword_001", "Weapon_Sword_002", "Weapon_Sword_003", "Weapon_Sword_024", "Weapon_Sword_025", "Weapon_Sword_027", "Weapon_Sword_029", "Weapon_Sword_031", "Weapon_Sword_041", "Weapon_Sword_047", "Weapon_Sword_051", "Weapon_Lsword_001", "Weapon_Lsword_002", "Weapon_Lsword_002", "Weapon_Lsword_003", "Weapon_Lsword_024", "Weapon_Lsword_027", "Weapon_Lsword_029", "Weapon_Lsword_036", "Weapon_Lsword_041", "Weapon_Lsword_047", "Weapon_Lsword_051", "Weapon_Spear_001", "Weapon_Spear_002", "Weapon_Spear_003", "Weapon_Spear_024", "Weapon_Spear_025", "Weapon_Spear_027", "Weapon_Spear_029", "Weapon_Spear_030", "Weapon_Spear_032", "Weapon_Spear_047"]:
        get_coordinate_couples(weapon)
        print(f'Done {weapon}')

#all_maps()

get_coordinate_couples('Weapon_Spear_047')