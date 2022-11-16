from __future__ import annotations

import dataclasses
import enum
import struct

from typing import List


_MAX_PARMS = 8


def _read_struct(fmt, f):
    size = struct.calcsize(fmt)
    return struct.unpack(fmt, f.read(size))


@dataclasses.dataclass
class Function:
    progs: Progs = dataclasses.field(repr=False)
    first_statement: int
    parm_start: int
    locals_: int
    
    profile: int

    s_name: int
    s_file: int

    parm_size: List[int]

    @classmethod
    def load(cls, f):
        args = _read_struct("<LLLLLL", f)
        num_parms, = _read_struct("<L", f)
        parm_size = _read_struct("<" + "B" * _MAX_PARMS, f)
        return cls(None, *args, parm_size[:num_parms])

    @property
    def name(self):
        return self.progs.read_string(self.s_name)

    @property
    def file(self):
        return self.progs.read_string(self.s_file)


class Op(enum.IntEnum):
    DONE = 0
    MUL_F = enum.auto()
    MUL_V = enum.auto()
    MUL_FV = enum.auto()
    MUL_VF = enum.auto()
    DIV_F = enum.auto()
    ADD_F = enum.auto()
    ADD_V = enum.auto()
    SUB_F = enum.auto()
    SUB_V = enum.auto()
    EQ_F = enum.auto()
    EQ_V = enum.auto()
    EQ_S = enum.auto()
    EQ_E = enum.auto()
    EQ_FNC = enum.auto()
    NE_F = enum.auto()
    NE_V = enum.auto()
    NE_S = enum.auto()
    NE_E = enum.auto()
    NE_FNC = enum.auto()
    LE = enum.auto()
    GE = enum.auto()
    LT = enum.auto()
    GT = enum.auto()
    LOAD_F = enum.auto()
    LOAD_V = enum.auto()
    LOAD_S = enum.auto()
    LOAD_ENT = enum.auto()
    LOAD_FLD = enum.auto()
    LOAD_FNC = enum.auto()
    ADDRESS = enum.auto()
    STORE_F = enum.auto()
    STORE_V = enum.auto()
    STORE_S = enum.auto()
    STORE_ENT = enum.auto()
    STORE_FLD = enum.auto()
    STORE_FNC = enum.auto()
    STOREP_F = enum.auto()
    STOREP_V = enum.auto()
    STOREP_S = enum.auto()
    STOREP_ENT = enum.auto()
    STOREP_FLD = enum.auto()
    STOREP_FNC = enum.auto()
    RETURN = enum.auto()
    NOT_F = enum.auto()
    NOT_V = enum.auto()
    NOT_S = enum.auto()
    NOT_ENT = enum.auto()
    NOT_FNC = enum.auto()
    IF = enum.auto()
    IFNOT = enum.auto()
    CALL0 = enum.auto()
    CALL1 = enum.auto()
    CALL2 = enum.auto()
    CALL3 = enum.auto()
    CALL4 = enum.auto()
    CALL5 = enum.auto()
    CALL6 = enum.auto()
    CALL7 = enum.auto()
    CALL8 = enum.auto()
    STATE = enum.auto()
    GOTO = enum.auto()
    AND = enum.auto()
    OR = enum.auto()
    BITAND = enum.auto()
    BITOR = enum.auto()


class Type(enum.IntEnum):
    BAD = -1
    VOID = enum.auto()
    STRING = enum.auto()
    FLOAT = enum.auto()
    VECTOR = enum.auto()
    ENTITY = enum.auto()
    FIELD = enum.auto()
    FUNCTION = enum.auto()
    POINTER = enum.auto()

    def format(self):
        return self.name.lower()


_BINARY_OPS = {
    Op.ADD_F: ('+', Type.FLOAT, Type.FLOAT, Type.FLOAT),
    Op.SUB_F: ('-', Type.FLOAT, Type.FLOAT, Type.FLOAT),
    Op.MUL_F: ('*', Type.FLOAT, Type.FLOAT, Type.FLOAT),
    Op.DIV_F: ('/', Type.FLOAT, Type.FLOAT, Type.FLOAT),
    Op.ADD_V: ('+', Type.VECTOR, Type.VECTOR, Type.VECTOR),
    Op.SUB_V: ('-', Type.VECTOR, Type.VECTOR, Type.VECTOR),
    Op.MUL_V: ('*', Type.VECTOR, Type.VECTOR, Type.VECTOR),
    Op.MUL_VF: ('*vf', Type.VECTOR, Type.FLOAT, Type.VECTOR),
    Op.MUL_FV: ('*fv', Type.VECTOR, Type.VECTOR, Type.FLOAT),
    Op.BITAND: ('&', Type.FLOAT, Type.FLOAT, Type.FLOAT),
    Op.BITOR: ('|', Type.FLOAT, Type.FLOAT, Type.FLOAT),
    Op.GE: ('>=', Type.FLOAT, Type.FLOAT, Type.FLOAT),
    Op.LE: ('<=', Type.FLOAT, Type.FLOAT, Type.FLOAT),
    Op.GT: ('>', Type.FLOAT, Type.FLOAT, Type.FLOAT),
    Op.LT: ('<', Type.FLOAT, Type.FLOAT, Type.FLOAT),
    Op.AND: ('&&', Type.FLOAT, Type.FLOAT, Type.FLOAT),
    Op.OR: ('||', Type.FLOAT, Type.FLOAT, Type.FLOAT),
    Op.EQ_F: ('==', Type.FLOAT, Type.FLOAT, Type.FLOAT),
    Op.EQ_V: ('==', Type.FLOAT, Type.VECTOR, Type.VECTOR),
    Op.EQ_S: ('==', Type.FLOAT, Type.STRING, Type.STRING),
    Op.EQ_E: ('==', Type.FLOAT, Type.ENTITY, Type.ENTITY),
    Op.EQ_FNC: ('==', Type.FLOAT, Type.FUNCTION, Type.FUNCTION),
    Op.NE_F: ('!=', Type.FLOAT, Type.FLOAT, Type.FLOAT),
    Op.NE_V: ('!=', Type.FLOAT, Type.VECTOR, Type.VECTOR),
    Op.NE_S: ('!=', Type.FLOAT, Type.STRING, Type.STRING),
    Op.NE_E: ('!=', Type.FLOAT, Type.ENTITY, Type.ENTITY),
    Op.NE_FNC: ('!=', Type.FLOAT, Type.FUNCTION, Type.FUNCTION),
}


_STORE_OPS = {
    Op.STORE_F: (True, Type.FLOAT),
    Op.STORE_ENT: (True, Type.ENTITY),
    Op.STORE_FLD: (True, Type.ENTITY),
}

@dataclasses.dataclass
class Statement:
    progs: Progs
    op: Op
    a: int
    b: int
    c: int

    @classmethod
    def load(cls, f):
        op_int, *args = _read_struct("<Hhhh", f)
        return cls(None, Op(op_int), *args)

    def format(self):
        # OP_LOAD_*  :  Copy field at offset <B> from entity <A> into <C>


        if self.op in _BINARY_OPS:
            op_str, c_type, a_type, b_type = _BINARY_OPS[self.op]
            out = (f"*({c_type.format()}*){self.c} ="
                   f" *({a_type.format()}*){self.a} {op_str}"
                   f" *({b_type.format()}*){self.b}")
        else:
            out = str((self.op, self.a, self.b, self.c))
        return out


@dataclasses.dataclass
class Definition:
    progs: Progs
    type_: int
    save_global: bool
    ofs: int
    s_name: int

    @classmethod
    def load(cls, f):
        type_, ofs, s_name = _read_struct("<HHl", f)
        save_global = (type_ & (1 << 15)) != 0
        type_ &= ~(1 << 15)
        return cls(None, Type(type_), save_global, ofs, s_name)

    @property
    def name(self):
        return self.progs.read_string(self.s_name)
    

@dataclasses.dataclass
class Progs:
    version: int
    crc: int
    strings: str
    globals_: bytes
    functions: List[Function]
    statements: List[Statement]
    global_defs: List[Definition]
    field_defs: List[Definition]

    def read_string(self, i):
        out = self.strings[i:]
        if '\0' in out:
            out = out[:out.index('\0')]
        return out

    def read_global(self, num, type_: Type):
        if type_ == Type.STRING:
            out = self.read_string(
                struct.unpack('<L', self.globals_[num:num + 4])[0]
            )
        elif type_ == Type.FLOAT:
            out, = struct.unpack('<f', self.globals_[num:num + 4])
        elif type_ == Type.VECTOR:
            out = struct.unpack('<fff', self.globals_[num:num + 12])
        elif type_ == Type.ENTITY:
            out, = struct.unpack('<L', self.globals_[num:num + 4])
        elif type_ == Type.FUNCTION:
            func_idx, = struct.unpack('<L', self.globals_[num:num + 4])
            if func_idx < len(self.functions):
                out = self.functions[func_idx]
            else:
                out = f"Invalid func {func_idx}"
        else:
            out = f"Unhandled type: {type_}"

        return out

    @classmethod
    def load(cls, f):
        version, crc = _read_struct("<LL", f)

        # Load lump offsets
        offsets = {}
        for key in ['statements', 'global_defs', 'field_defs', 'functions',
                    'strings', 'globals']:
            offset, count = _read_struct("<LL", f)
            offsets[key] = {'offset': offset, 'count': count}

        # Read strings
        f.seek(offsets['strings']['offset'])
        strings = f.read(offsets['strings']['count']).decode('ascii')

        # Read globals
        f.seek(offsets['globals']['offset'])
        globals_ = f.read(offsets['globals']['count'])

        # Read functions
        f.seek(offsets['functions']['offset'])
        functions = [Function.load(f)
                     for _ in range(offsets['functions']['count'])]

        # Read statements
        f.seek(offsets['statements']['offset'])
        statements = [Statement.load(f)
                      for _ in range(offsets['statements']['count'])]

        # Read global defs
        f.seek(offsets['global_defs']['offset'])
        global_defs = [Definition.load(f)
                       for _ in range(offsets['global_defs']['count'])]

        # Read field defs
        f.seek(offsets['field_defs']['offset'])
        field_defs = [Definition.load(f)
                       for _ in range(offsets['field_defs']['count'])]

        return cls(version, crc, strings, globals_, functions, statements,
                   global_defs, field_defs)

    def __post_init__(self):
        for function in self.functions:
            function.progs = self

        for statement in self.statements:
            statement.progs = self

        for global_def in self.global_defs:
            global_def.progs = self

        for field_def in self.field_defs:
            field_def.progs = self


def dump_progs_main():
    import argparse
    import sys

    from . import pak

    parser = argparse.ArgumentParser(description='Dump a progs.dat')
    parser.add_argument('-b', '--base-dir', help='base dir containing id1/ etc')
    parser.add_argument('-g', '--game', help='sub-dir within game dir',
                        default=None)
    parsed = parser.parse_args(sys.argv[1:])

    fs = pak.Filesystem(parsed.base_dir, parsed.game)
    with fs.open('progs.dat') as f:
        pr = Progs.load(f)
        for func in pr.functions:
            print(func.name, func.file)

        statement_funcs = {
            func.first_statement: func for func in pr.functions
        }

        for num, statement in enumerate(pr.statements):
            if num in statement_funcs:
                func = statement_funcs[num]
                print("//", func.file, ':', func.name)
            print(statement.format())

        for d in pr.global_defs: 
            print((d.type_, d.name, d.ofs, pr.read_global(d.ofs, d.type_)))