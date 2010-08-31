"""Graphviz support for django-pki"""

try:
    import pygraphviz as pgv
except ImportError:
    raise Exception( "Failed to import pygraphviz. Disable PKI_ENABLE_GRAPHVIZ or install pygraphviz" )


def DepencyGraph(object, target, type):
    """Collect all objects in the depency tree and write Graphviz PNG"""
    
    shape = "folder"
    
    if type == "cert":
        shape = "note"
    
    if object.active:
        obj_fill = "blue"
    else:
        obj_fill = "red"
    
    obj_list = [ { 'name': object.common_name, 'state': object.active, 'fill': obj_fill, 'shape': shape }, ]
    
    G = pgv.AGraph(directed=True, layout="dot", pad=0.2)
    
    ## Find possible parents
    if object.parent != None:
        p = object.parent
        
        while p != None:
            obj_list.append( { 'name': p.common_name, 'state': p.active, 'shape': 'folder' } )
            p = p.parent
    
    obj_list.reverse()
    
    ## Add nodes
    for i in range(0, len(obj_list)):
        
        c = 'black'
        if obj_list[i]['state'] is False:
            c = 'red'
        
        if i > 0:
            if obj_list[i]['shape'] == 'note' or obj_list[i-1]['state'] is False:
                c_dummy = c
            else:
                c_dummy = 'black'
            
            G.add_node("dummy_start_%s" % obj_list[i]['name'], shape=obj_list[i]['shape'], color=c_dummy, label="...")
            G.add_node("dummy_end_%s" % obj_list[i]['name'], shape=obj_list[i]['shape'], color=c_dummy, label="...")
        
        if 'fill' in obj_list[i]:
            G.add_node(obj_list[i]['name'], shape=obj_list[i]['shape'], color="%s" % c, style="filled,bold", fillcolor=obj_list[i]['fill'], fontcolor="white")
        else:
            G.add_node(obj_list[i]['name'], shape=obj_list[i]['shape'], color="%s" % c, style="bold")
        
    ## Draw edges
    color = "black"

    for i in range(0, len(obj_list)-1):
        if obj_list[i+1]['state'] is False:
            fail_from_here = True
            color = "red"
        
        G.add_edge(obj_list[i]['name'], "dummy_start_%s" % obj_list[i+1]['name'], color="black", weight=4.5)
        G.add_edge(obj_list[i]['name'], obj_list[i+1]['name'], color="%s" % color, weight=5, style="bold")
        G.add_edge(obj_list[i]['name'], "dummy_end_%s" % obj_list[i+1]['name'], color="black", weight=4.5)
    
    G.layout()
    G.draw(target, format='png')
