from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.util.compat import make_admonition
from sphinx.locale import _

def setup(app):
    app.add_config_value('contributors_include_contributors', True, 'html')
    app.add_config_value('contributors_json', './contributors.json', 'html')

    app.add_node(contributorslist)
    app.add_node(contributors,
        html=(visit_contributors_node, depart_contributors_node),
        latex=(visit_contributors_node, depart_contributors_node),
        text=(visit_contributors_node, depart_contributors_node))

    app.add_directive('contributors', ContributorsDirective)
    app.add_directive('contributorslist', ContributorsListDirective)
    app.connect('doctree-resolved', process_contributors_nodes)
    app.connect('env-purge-doc', purge_contributors)

    return {'version' : '0.0.1'}

class contributors(nodes.Admonition, nodes.Element):
    pass

class contributorslist(nodes.General, nodes.Element):
    pass

def visit_contributors_node(self, node):
    self.visit_admonition(node)

def depart_contributors_node(self, node):
    self.depart_admonition(node)


class ContributorsDirective(Directive):

    has_content = True

    def run(self):

        env = self.state.document.settings.env

        targetid = "contributors-%d" % env.new_serialno('contributors')
        targetnode = nodes.target('', '', ids=[targetid])

        ad = make_admonition(contributors, self.name, [_('Contributors')], self.options,
                             self.content, self.lineno, self.content_offset,
                             self.block_text, self.state, self.state_machine)

        if not hasattr(env, 'contributors_all_contributors'):
            env.contributors_all_contributorss = []

        print env.docname, self.lineno, ad[0].deepcopy(), targetnode

        env.contributors_all_contributorss.append({
            'docname': env.docname,
            'lineno': self.lineno,
            'contributors': ad[0].deepcopy(),
            'target': targetnode,
        })

        return [targetnode] + ad

class ContributorsListDirective(Directive):
    pass

def purge_contributors(app, env, docname):
    if not hasattr(env, 'contributors_all_contributors'):
        return
    env.contributors_all_contributors = [contributor for contributor in env.contributors_all_contributors
                          if contributor['docname'] != docname]

def process_contributors_nodes(app, doctree, fromdocname):
    if not app.config.contributors_include_contributors:
        for node in doctree.traverse(contributor):
            node.parent.remove(node)

    # Replace all contributorslist nodes with a list of the collected contributors.
    # Augment each contributor with a backlink to the original location.
    env = app.builder.env

    for node in doctree.traverse(contributorslist):
        if not app.config.contributors_include_contributors:
            node.replace_self([])
            continue

        content = []

        for contributors_info in env.contributors_all_contributors:
            para = nodes.paragraph()
            filename = env.doc2path(contributors_info['docname'], base=None)
            description = (
                _('(The original entry is located in %s, line %d and can be found ') %
                (filename, contributors_info['lineno']))
            para += nodes.Text(description, description)

            # Create a reference
            newnode = nodes.reference('', '')
            innernode = nodes.emphasis(_('here'), _('here'))
            newnode['refdocname'] = contributors_info['docname']
            newnode['refuri'] = app.builder.get_relative_uri(
                fromdocname, contributors_info['docname'])
            newnode['refuri'] += '#' + contributors_info['target']['refid']
            newnode.append(innernode)
            para += newnode
            para += nodes.Text('.)', '.)')

            # Insert into the contributorslist
            content.append(contributors_info['contributor'])
            content.append(para)

        node.replace_self(content)
