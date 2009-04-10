from django.template import Library
from django.template import Node
from django.template import TemplateSyntaxError
from django.template import VariableDoesNotExist
from django.utils.encoding import force_unicode
from django.utils.functional import allow_lazy
import re

register = Library()

@register.tag(name="switch")
def do_switch(parser, token):
    """
    from http://www.djangosnippets.org/snippets/967/

    The ``{% switch %}`` tag compares a variable against one or more values in
    ``{% case %}`` tags, and outputs the contents of the matching block.  An
    optional ``{% else %}`` tag sets off the default output if no matches
    could be found::

        {% switch result_count %}
            {% case 0 %}
                There are no search results.
            {% case 1 %}
                There is one search result.
            {% else %}
                Jackpot! Your search found {{ result_count }} results.
        {% endswitch %}

    Each ``{% case %}`` tag can take multiple values to compare the variable
    against::

        {% switch username %}
            {% case "Jim" "Bob" "Joe" %}
                Me old mate {{ username }}! How ya doin?
            {% else %}
                Hello {{ username }}
        {% endswitch %}
    """
    bits = token.contents.split()
    tag_name = bits[0]
    if len(bits) != 2:
        raise TemplateSyntaxError("'%s' tag requires one argument" % tag_name)
    variable = parser.compile_filter(bits[1])

    class BlockTagList(object):
        # This is a bit of a hack, as it embeds knowledge of the behaviour
        # of Parser.parse() relating to the "parse_until" argument.
        def __init__(self, *names):
            self.names = set(names)
        def __contains__(self, token_contents):
            name = token_contents.split()[0]
            return name in self.names

    # Skip over everything before the first {% case %} tag
    parser.parse(BlockTagList('case', 'endswitch'))

    cases = []
    token = parser.next_token()
    got_case = False
    got_else = False
    while token.contents != 'endswitch':
        nodelist = parser.parse(BlockTagList('case', 'else', 'endswitch'))
        
        if got_else:
            raise TemplateSyntaxError("'else' must be last tag in '%s'." % tag_name)

        contents = token.contents.split()
        token_name, token_args = contents[0], contents[1:]
        
        if token_name == 'case':
            tests = map(parser.compile_filter, token_args)
            case = (tests, nodelist)
            got_case = True
        else:
            # The {% else %} tag
            case = (None, nodelist)
            got_else = True
        cases.append(case)
        token = parser.next_token()

    if not got_case:
        raise TemplateSyntaxError("'%s' must have at least one 'case'." % tag_name)

    return SwitchNode(variable, cases)

class SwitchNode(Node):
    def __init__(self, variable, cases):
        self.variable = variable
        self.cases = cases

    def __repr__(self):
        return "<Switch node>"

    def __iter__(self):
        for tests, nodelist in self.cases:
            for node in nodelist:
                yield node

    def get_nodes_by_type(self, nodetype):
        nodes = []
        if isinstance(self, nodetype):
            nodes.append(self)
        for tests, nodelist in self.cases:
            nodes.extend(nodelist.get_nodes_by_type(nodetype))
        return nodes

    def render(self, context):
        try:
            value_missing = False
            value = self.variable.resolve(context, True)
        except VariableDoesNotExist:
            no_value = True
            value_missing = None
        
        for tests, nodelist in self.cases:
            if tests is None:
                return nodelist.render(context)
            elif not value_missing:
                for test in tests:
                    test_value = test.resolve(context, True)
                    if value == test_value:
                        return nodelist.render(context)
        else:
            return ""
        
#http://www.djangosnippets.org/snippets/569/
def strip_empty_lines(value):
    """Return the given HTML with empty and all-whitespace lines removed."""
    return re.sub(r'\n[ \t\r]*(?=\n)', '', force_unicode(value))
strip_empty_lines = allow_lazy(strip_empty_lines, unicode)

class GaplessNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        return strip_empty_lines(self.nodelist.render(context).strip())

def gapless(parser, token):
    """
    Remove empty and whitespace-only lines.  Useful for getting rid of those
    empty lines caused by template lines with only template tags and possibly
    whitespace.

    Example usage::

        <p>{% gapless %}
          {% if yepp %}
            <a href="foo/">Foo</a>
          {% endif %}
        {% endgapless %}</p>

    This example would return this HTML::

        <p>
            <a href="foo/">Foo</a>
        </p>

    """
    nodelist = parser.parse(('endgapless',))
    parser.delete_first_token()
    return GaplessNode(nodelist)
gapless = register.tag(gapless)
