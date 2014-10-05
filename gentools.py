import types
import opcode


def _replace_globals_and_closures(generator, **constants):
    gi_code = generator.gi_code
    new_code = list(gi_code.co_code)
    new_consts = list(gi_code.co_consts)
    locals = generator.gi_frame.f_locals
    freevars = list(gi_code.co_freevars)

    # Replace global lookups by the values defined in *constants*.
    i = 0
    while i < len(new_code):
        op_code = new_code[i]
        if op_code == opcode.opmap['LOAD_GLOBAL']:
            oparg = new_code[i + 1] + (new_code[i + 2] << 8)
            name = gi_code.co_names[oparg]
            if name in constants:
                value = constants[name]
                for pos, v in enumerate(new_consts):
                    if v is value:
                        break
                else:
                    pos = len(new_consts)
                    new_consts.append(value)
                new_code[i] = opcode.opmap['LOAD_CONST']
                new_code[i + 1] = pos & 0xFF
                new_code[i + 2] = pos >> 8
        i += 1
        if op_code >= opcode.HAVE_ARGUMENT:
            i += 2

    # Repalce closures lookups by the values defined in *constants*
    i = 0
    while i < len(new_code):
        op_code = new_code[i]
        if op_code == opcode.opmap['LOAD_DEREF']:
            oparg = new_code[i + 1] + (new_code[i + 2] << 8)
            name = freevars[oparg]
            if name in constants:
                value = constants[name]
                for pos, v in enumerate(new_consts):
                    if v is value:
                        break
                else:
                    pos = len(new_consts)
                    new_consts.append(value)
                new_code[i] = opcode.opmap['LOAD_CONST']
                new_code[i + 1] = pos & 0xFF
                new_code[i + 2] = pos >> 8
            if name in locals:
                del locals[name]
                freevars.remove(name)
        i += 1
        if op_code >= opcode.HAVE_ARGUMENT:
            i += 2

    code_str = ''.join(map(chr, new_code))
    code_object = types.CodeType(
        gi_code.co_argcount,
        gi_code.co_kwonlyargcount,
        gi_code.co_nlocals,
        gi_code.co_stacksize,
        gi_code.co_flags,
        bytes(code_str, 'utf-8'),
        tuple(new_consts),
        gi_code.co_names,
        gi_code.co_varnames,
        gi_code.co_filename,
        gi_code.co_name,
        gi_code.co_firstlineno,
        gi_code.co_lnotab,
        tuple(freevars),
        gi_code.co_cellvars)

    function = types.FunctionType(
        code_object,
        generator.gi_frame.f_globals,
        generator.__name__,
    )

    return function(**locals)


class Define:
    def __init__(self, generator):
        self.generator = generator
        self.gi_frame = self.generator.gi_frame
        self.close = self.generator.close
        self.send = self.generator.send
        self.throw = self.generator.throw

    def where(self, **kwds):
        self.generator = _replace_globals_and_closures(self.generator, **kwds)
        return self

    @property
    def gi_running(self):
        return self.generator.gi_running

    def __iter__(self):
        return self.generator

    def __next__(self):
        return next(self.generator)
