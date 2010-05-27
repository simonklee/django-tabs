from django import template

register = template.Library()

ACTIVE_TAB_NAME = 'ACTIVETABS'
DEFAULT_NAMESPACE = 'default'

def get_tabs(context):    
    tabs = template.Variable(ACTIVE_TAB_NAME)
    try:
        return tabs.resolve(context)
    except template.VariableDoesNotExist:
        return {}

def set_tab(context, namespace, name):
    tabs = get_tabs(context)
    tabs[namespace] = name
    context[ACTIVE_TAB_NAME] = tabs
    
def is_tab(context, namespace, name):
    tabs = get_tabs(context)
    if namespace in tabs and tabs[namespace]==name:
        return True
    return False

    
class TabNode(template.Node):
    
    def __init__(self, name, namespace=None):
        if namespace is None:
            namespace = DEFAULT_NAMESPACE
        self.namespace = template.Variable(namespace)
        self.name = template.Variable(name)

        
    def render(self, context):
        try:
            namespace = self.namespace.resolve(context)
        except template.VariableDoesNotExist:
            namespace = None
        try:
            name = self.name.resolve(context)
        except template.VariableDoesNotExist(context):
            name = None

        set_tab(context, namespace, name)
        return ''

class IfTabNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false, name, namespace=None):
        if namespace is None:
            namespace = DEFAULT_NAMESPACE
            
        self.namespace = template.Variable(namespace)
        self.name = template.Variable(name)
        
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        
    def render(self, context):
        try:
            namespace = self.namespace.resolve(context)
        except template.VariableDoesNotExist:
            namespace = None
        try:
            name = self.name.resolve(context)
        except template.VariableDoesNotExist(context):
            name = None
            
        if is_tab(context, namespace, name):
            return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)

def tab(parser, token):
    bits = token.contents.split()[1:]
    if len(bits) not in (1, 2):
        raise template.TemplateSyntaxError, "Invalid number of arguments"
    if len(bits) == 1:
        namespace = None
        name = bits[0]
    else:
        namespace = bits[0]
        name = bits[1]
        
    return TabNode(name, namespace)
tab = register.tag('tab', tab)

def iftab(parser, token):
    bits = token.contents.split()[1:]
    nodelist_true = parser.parse(('else', 'endiftab'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endiftab',))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    if len(bits) not in (1, 2):
        raise template.TemplateSyntaxError, "Invalid number of arguments"
    if len(bits) == 1:
        namespace = None
        name = bits[0]
    else:
        namespace = bits[0]
        name = bits[1]
    return IfTabNode(nodelist_true, nodelist_false, name, namespace)

iftab = register.tag('iftab', iftab)
