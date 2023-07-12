## https://github.com/balanx/FsmLog/

import sys
import os
import pathlib
import argparse
import yaml


parser = argparse.ArgumentParser(description='https://github.com/balanx/FsmLog/')
parser.add_argument('source', help='yaml format file')
parser.add_argument('-g', '--graph', action='store_true', help='output graph')
args = parser.parse_args()

def log2(n) :
    i = 1
    while (2**i < n) and (i <= 64):
        i += 1

    return i


def read_file() :
    with open(args.source, 'r') as f :
        return yaml.load(f, Loader=yaml.FullLoader)


def get_file_name() :
    fdir, full_fn = os.path.split(args.source)
    fn = os.path.splitext(full_fn)[0]  # module name
    #if fdir == '': fdir = '.'
    return fn


def initial() :
    f = {
         'clock' : 'clk',
         'reset_name' : 'rst',
         'reset_edge' :  True , # posedge or 1
         'reset_mode' :  True , # Sync.
         'enable' : '',
         'state_name' : 'state',
          'next_name' : 'next_st',
         ## local vars
         'module' : '',
      'state_1st' : '',
           'node' : {},
           'edge' : {},
            'tab' : '  '  }

    if 'config' in src :
        for k,v in src['config'].items() :
            f[k] = v

    if 'input'  not in src :
        src['input'] = {}

    if 'output' not in src :
        src['output'] = {}

    if 'var' not in src :
        src['var'] = {}

    return f

def vlog_head() :
    txt  = '\nmodule  ' + config['module'] + ' (\n'
    txt += '  input' + config['tab']*8 + config['clock'] + '\n'
    txt += ', input' + config['tab']*8 + config['reset_name'] + '\n'

    if config['enable'] != '' :
        txt += ', input' + config['tab']*8 + config['enable'] + '\n'

    return txt


def get_range_str(n) :
    txt  = config['tab']*3
    if isinstance(n, int) :
        if n > 1 :
            txt = '[' + str(n-1) + ':0]'
    else :
        txt = '[' + n + '-1 :0]'

    return txt


def vlog_inputs() :
    txt  = ''
    for k,v in src['input'].items() :
        txt += ', input     ' + get_range_str(v) + '  ' + k + '\n'

    return txt


def vlog_outputs() :
    txt  = ''
    for k,v in src['output'].items() :
        txt += ',output reg ' + get_range_str(v[0]) + '  ' + k + '\n'

    txt += ');\n'
    return txt


def vlog_vars() :
    txt  = '\n'
    for k,v in src['var'].items() :
        if v[1] == 'wire' :
            txt += 'wire ' + get_range_str(v[0]) + '  ' + k + ' ;\n'
            txt += 'assign  ' + k + ' = ' + v[2] + ' ;\n'
        else :
            txt += 'reg  ' + get_range_str(v[0]) + '  ' + k + ' ;\n'

    return txt


def vlog_param() :
    n = len(src['fsm'])
    txt  = '\nlocalparam ' + get_range_str(log2(n)) + '\n'
    i = 0
    for k,v in src['fsm'].items() :
        if i >= n-1 : break
        if i == 0 : config['state_1st'] = k
        txt += k + ' = ' + str(i) + ' ,\n'
        i += 1

    txt += k + ' = ' + str(i) + ' ;\n'
    return txt


def vlog_always_1st() :
    n = len(src['fsm'])
    txt  = '\nreg  ' + get_range_str(log2(n)) + '  state, next_st ;\n'
    txt += '\nalways @(posedge ' + config['clock']

    if not config['reset_mode'] :
        txt += ', ' + ('posedge ' if config['reset_edge'] else 'negedge ') + config['reset_name']

    txt += ')\n'
    txt += config['tab']*2 + 'if (' + ('' if config['reset_edge'] else '!') + config['reset_name'] + ')\n'
    txt += config['tab']*4 + config['state_name'] + ' <= ' + config['state_1st'] + ' ;\n'
    txt += config['tab']*2 + 'else'

    if config['enable'] :
        txt += ' if (' + config['enable'] + ')'

    txt += '\n'
    txt += config['tab']*4 + config['state_name'] + ' <= ' + config['next_name']  + ' ;\n\n'

    return txt


def vlog_always_2nd() :
    txt  = '\nalways @* begin\n'
    txt += config['tab']*2 + config['next_name'] + ' = ' + config['state_name'] + ' ;\n\n'
    txt += config['tab']*2 + 'case(' + config['state_name'] + ')\n'

    for k,v in src['fsm'].items() :
        txt += config['tab']*4 + k + ' :\n'
        config['node'][k] = ' [label="' + k

        if isinstance(v, str) :
            txt += config['tab']*8 + config['next_name'] + ' = ' + v + ' ;\n'
            config['edge'][k+'+'+v] = ' [label="'
        else :
            i = 0
            for x,y in v.items() :
                if x in src['fsm'] :
                    txt += config['tab']*6 + ('' if i == 0 else 'else ')

                    cond = '' if (y=='+') else y
                    config['edge'][k+'+'+x] = ' [label="' + cond

                    if cond :
                        txt += 'if (' + cond + ')'

                    txt += '\n'
                    txt += config['tab']*8 + config['next_name'] + ' = ' + x + ' ;\n'
                    i += 1

        txt += '\n'

    txt += config['tab']*4 + 'default :\n'
    txt += config['tab']*8 + config['next_name'] + ' = ' + config['state_1st'] + ' ;\n'
    txt += config['tab']*2 + 'endcase\nend\n'
    return txt


def vlog_export(x) :

    y = ''
    for k,v in x :
        if  'wire' in v : continue

        y += '\n'
        if ('trig' in v) or ('hold' not in v) :
            y += config['tab']*4 + k + ' <= ' + str(v[0]) + '\'d0 ;\n'

        i = 0
        for j in v :
            if not isinstance(j, dict) : continue

            y += config['tab']*4
            if i > 0 : y += 'else '

            s = list(j.keys())[0]
            d = list(j.values())[0]
            if '+' in s :
                config['edge'][s] += '//' + k + '=' + str(d)
                s = s.split('+')
                cond = config['state_name'] + '==' + s[0] + ' && ' + config['next_name'] + '==' + s[1]
            else :
                config['node'][s] += '\\n' + k + '=' + str(d)
                cond = config[ 'next_name'] + '==' + s

            y += 'if (' + cond + ')' + config['tab']*2 + k + ' <= ' + str(d) + ' ;\n'
            i += 1

    return y


def vlog_always_3rd() :
    txt  = '\nalways @(posedge ' + config['clock']

    if not config['reset_mode'] :
        txt += ', ' + ('posedge ' if config['reset_edge'] else 'negedge ') + config['reset_name']

    txt += ')\n' + config['tab']*2 + 'if (' + ('' if config['reset_edge'] else '!')
    txt += config['reset_name'] + ') begin\n'

    for k,v in src['var'].items() :
        if v[1] != 'wire' :
            txt += config['tab']*4 + k + ' <= ' + str(v[0]) + '\'d0 ;\n'

    for k,v in src['output'].items() :
        if v[1] != 'wire' :
            txt += config['tab']*4 + k + ' <= ' + str(v[0]) + '\'d0 ;\n'

    txt += config['tab']*2 + 'end\n'
    txt += config['tab']*2 + 'else begin'


    txt += vlog_export(src['var'].items() )
    txt += vlog_export(src['output'].items() )


    txt += config['tab']*2 + 'end\n'
    txt += '\nendmodule // fsmlog\n'

    return txt


def dot_build() :
    f  = 'digraph fsmlog {\n'
    f += 'rankdir=LR\n'  # LR, UD
    f += 'size="8,5"\n'  # 20,12 / 8,5

    i = 0
    for k,v in config['node'].items() :
        f += k + v + '"'
        if i==0 :
            f += ' style=filled fillcolor=yellow shape=doublecircle'

        f += ']\n'
        i += 1


    for k,v in config['edge'].items() :
        f += k.replace('+', '->') + v + '"]\n'

    f += '}\n'
    #out = pathlib.Path(config['module'] + '.gv')
    #out.write_text(f, encoding='utf-8')
    return f


if __name__ == '__main__' :

    src = read_file()
    # print(src)
    # sys.exit(0)

    config = initial()
    config['module'] = get_file_name()

    txt  = ''
    txt += vlog_head()
    txt += vlog_inputs()
    txt += vlog_outputs()
    txt += vlog_vars()
    txt += vlog_param()
    txt += vlog_always_1st()
    txt += vlog_always_2nd()
    txt += vlog_always_3rd()
    print(txt)

    txt = dot_build()
    #print(txt)
    if args.graph :
        import  graphviz
        dot=graphviz.Source(txt)
        #dot.view()  # pdf
        dot.render(config['module']+'.gv', format='png', view=True)

    # print(config['node'])
    # print(config['edge'])
    sys.exit(0)
