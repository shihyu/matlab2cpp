
def variable_lists(node):
    nodes = node.flatten(ordered=False, reverse=False, inverse=False)

    #store some variable names, in private or shared
    #private_variable = []
    #shared_variable = []
    assigned_var = []
    type_info = []

    #get iterator name
    iterator_name = node[0].name
    for n in nodes:
        if n.cls == "Assign":
            #index = n.parent.children.index(n)

            if n[0].cls == "Var":
                if n[0].name not in assigned_var:
                    assigned_var.append(n[0].name)
                    type_info.append(n[0].type)
            """
            if n[0].cls == "Set":
                var_name = n[0].name

                #subnodes to Set
                #index = n.parent.children.index(n)
                #subnodes = n.parent[index].flatten(ordered=False, reverse=False, inverse=False)
                subnodes = n[0].flatten(ordered=False, reverse=False, inverse=False)

                for subnode in subnodes[1:]:
                    if subnode.name and subnode.name == iterator_name:
                        shared_variable.append(var_name)
                        #print subnode.name
            """

        if n.cls == "Var" and n.parent.cls == "For":
            if n.name not in assigned_var:
                assigned_var.append(n.name)
                type_info.append(n.type)

    #shared_variable = list(set(shared_variable))
    #print shared_variable

    #for n in nodes:
    #    if (n.cls == "Var" or n.cls == "Get") and n.backend != "reserved" and n.name \
    #            not in [shared_variable, node[0].name]:
    #        private_variable.append(n.name)

    #private_variable = list(set(private_variable))

    #return private_variable, shared_variable, assigned_var, type_info
    return assigned_var, type_info

def omp(node, start, stop, step):
    assigned_var, type_info = variable_lists(node)

    #out = "#pragma omp parallel for\nfor (%(0)s=" + start + \
            #    "; %(0)s<=" + stop + "; %(0)s"

    temp_str = ", ".join(assigned_var)
    if temp_str:
        temp_str = "firstprivate(" + temp_str + ")"

    out = "#pragma omp parallel for " + temp_str + "\nfor (%(0)s=" + start + \
                "; %(0)s<=" + stop + "; %(0)s"

    return out

def tbb(node, start, stop, step):
    assigned_var, type_info = variable_lists(node)

    out = "{\n"

    for var, type in zip(assigned_var, type_info):
        out += "tbb::enumerable_thread_specific<" + type + "> " + "_" + var + " = " + var + " ;\n"

    out += "tbb::parallel_for(tbb::blocked_range<size_t>(" + start + ", " + stop + "+1" + \
                  "),\n" + "[&]" + "(const tbb::blocked_range<size_t>& _range) \n{\n"

    #assign to local L, x, y
    for var, type in zip(assigned_var, type_info):
        out += type + "& " + var + " = _" + var + ".local() ;\n"

    out += "\nfor (" + "%(0)s = _range.begin(); %(0)s != _range.end(); %(0)s"

    # special case for '+= 1'
    if step == "1":
        out += "++"
    else:
        out += "+=" + step

    out += ")\n{\n%(2)s\n}"
    out += "\n}\n);\n"
    out += "}"
    return out