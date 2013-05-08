def interactive_py_compile(source, filename="<interactive>"):
    c = compile(source, filename, "single")

    # we expect this at the end:
    #   PRINT_EXPR     
    #   LOAD_CONST
    #   RETURN_VALUE    
    import dis
    if ord(c.co_code[-5]) != dis.opmap["PRINT_EXPR"]:
        return c
    assert ord(c.co_code[-4]) == dis.opmap["LOAD_CONST"]
    assert ord(c.co_code[-1]) == dis.opmap["RETURN_VALUE"]

    code = c.co_code[:-5]
    code += chr(dis.opmap["RETURN_VALUE"])

    CodeArgs = [
        "argcount", "nlocals", "stacksize", "flags", "code",
        "consts", "names", "varnames", "filename", "name",
        "firstlineno", "lnotab", "freevars", "cellvars"]
    c_dict = dict([(arg, getattr(c, "co_" + arg)) for arg in CodeArgs])
    c_dict["code"] = code

    import types
    c = types.CodeType(*[c_dict[arg] for arg in CodeArgs])
    return c

print(eval(interactive_py_compile("1+1")))