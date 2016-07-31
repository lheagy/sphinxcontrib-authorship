from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.util.compat import make_admonition
from sphinx.locale import _
from sphinx.roles import XRefRole
import ast


# class ContributorsRole(XRefRole):


def setup(app):
    app.add_config_value('contributors_include_contributors', True, 'html')
    # app.add_config_value('contributors_json', './contributors.json', 'html')

    app.add_node(contributorList)
    app.add_node(contributors,
        html=(visit_contributors_node, depart_contributors_node),
        latex=(visit_contributors_node, depart_contributors_node),
        text=(visit_contributors_node, depart_contributors_node))

    app.add_directive('contributors', ContributorsDirective)
    app.add_directive('contributorList', ContributorListDirective)
    app.connect('doctree-resolved', process_contributors_nodes)
    app.connect('env-purge-doc', purge_contributors)

    return {'version' : '0.0.1'}

class contributors(nodes.Admonition, nodes.Element):
    pass

class contributorList(nodes.General, nodes.Element):
    pass

def visit_contributors_node(self, node):
    print 'visiting contributors node'
    self.visit_admonition(node)

def depart_contributors_node(self, node):
    print 'leaving contributors node'
    self.depart_admonition(node)


class ContributorsDirective(Directive):

    has_content = True

    def run(self):

        env = self.state.document.settings.env

        targetid = "contributors-%d" % env.new_serialno('contributors')
        targetnode = nodes.target('', '', ids=[targetid])

        # print self.content

        # contribs = {}

        # contribs = [c.split(':') for c in self.content]
        # print len(contribs)
        # print contribs
        assert len(self.content) == 1, 'a single dictionary must be provided in the contributors list'

        contrib = self.content[0]
        contribdict = ast.literal_eval(contrib)
        print contribdict
        print contribdict.keys()
            # print key
            # print val
        #     keys += key
        #     vals += val

        # contribdict = dict(zip(keys,vals))

        # print contribdict

        # exec 'contribdict = self.content[0]'

        # print contribdict
        # # self.content[0]

        # for contrib in contribdict.iteritem():
        #     print contrib
            # contribs += make_admonition(contributors, self.name, contrib)

        content = []

        for key in reversed(contribdict.keys()):
            print key, contribdict[key]
            content.append('**{0}**: {1}'.format(key, contribdict[key]))

        content = ['| ' + '{0}'.format(c) for c in content]
        print ' \n'.join(content)

        content = ' \n'.join(content)
        self.content[0] = '{0}'.format(content)

        print 'name: ', self.name
        print 'options: ', self.options
        print 'content: ', self.content
        print 'lineno: ', self.lineno
        print 'content_offset,: ', self.content_offset
        print 'block_text: ', self.block_text
        print 'state: ', self.state
        print 'state_machine: ', self.state_machine

        ad = make_admonition(contributors, self.name, [_('Contributors')], self.options,
                             self.content, self.lineno, self.content_offset,
                             self.block_text, self.state, self.state_machine)

        # print ad

        if not hasattr(env, 'contributors_all_contributors'):
            env.contributors_all_contributorss = []

        # print env.docname, self.lineno, ad[0].deepcopy(), targetnode

        env.contributors_all_contributorss.append({
            'docname': env.docname,
            'lineno': self.lineno,
            'contributors': ad[0].deepcopy(),
            'target': targetnode,
        })

        return [targetnode] + ad

class ContributorListDirective(Directive):

    has_content = True

    def run(self):

        env = self.state.document.settings.env

        targetid = "contributorList-%d" % env.new_serialno('contributorList')
        targetnode = nodes.target('', '', ids=[targetid])

        contrib = open(self.content)
        contribs = json.load(contrib)

        return [targetnode]


def purge_contributors(app, env, docname):
    if not hasattr(env, 'contributors_all_contributors'):
        return
    env.contributors_all_contributors = [contributor for contributor in env.contributors_all_contributors
                          if contributor['docname'] != docname]

def process_contributors_nodes(app, doctree, fromdocname):
    if not app.config.contributors_include_contributors:
        for node in doctree.traverse(contributor):
            node.parent.remove(node)

    # Replace all contributorList nodes with a list of the collected contributors.
    # Augment each contributor with a backlink to the original location.
    env = app.builder.env

    for node in doctree.traverse(contributorList):
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

            # Insert into the contributorList
            content.append(contributors_info['contributor'])
            content.append(para)

        node.replace_self(content)
