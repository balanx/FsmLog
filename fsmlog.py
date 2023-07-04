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
    conf = {
         'clock' : 'clk',
         'reset_name' : 'rst',
         'reset_edge' :  True , # posedge or 1
         'reset_mode' :  True , # Sync.
         'enable' : '',
         'state_name' : 'state',
          'next_name' : 'next_st',
         ##
         'module' : '',
         'init_state' : '',
         'export' : {},
            'tab' : '  '  }

    if 'config' in src :
        for k,v in src['config'].items() :
            conf[k] = v

    if 'inputs' not in src :
        src['inputs'] = {}

    if 'outputs' in src :
        for k,v in src['outputs'].items() :
            conf['export'][k] = {}
    else :
        src['outputs'] = {}

    if 'vars' in src :
        for k,v in src['vars'].items() :
            conf['export'][k] = {}
    else :
        src['vars'] = {}

    return conf

def vlog_head() :
    txt  = '\nmodule  ' + config['module'] + ' (\n'
    txt += '  input' + config['tab']*8 + config['clock'] + '\n'
    txt += ', input' + config['tab']*8 + config['reset_name'] + '\n'

    if config['enable'] != '' :
        txt += ', input' + config['tab']*8 + config['enable'] + '\n'

    return txt


def get_range_str(n) :
    txt  = config['tab']*3
    if n > 1 :
        txt = '[' + str(n-1) + ':0]'

    return txt


def vlog_inputs() :
    txt  = ''
    for k,v in src['inputs'].items() :
        txt += ', input     ' + get_range_str(v) + '  ' + k + '\n'

    return txt


def vlog_outputs() :
    txt  = ''
    for k,v in src['outputs'].items() :
        txt += ',output reg ' + get_range_str(v[0]) + '  ' + k + '\n'

    txt += ');\n'
    return txt


def vlog_vars() :
    txt  = '\n'
    for k,v in src['vars'].items() :
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
        if i == 0 : config['init_state'] = k
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
    txt += config['tab']*4 + config['state_name'] + ' <= ' + config['init_state'] + ' ;\n'
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

        if isinstance(v, str) :
            txt += config['tab']*6 + config['next_name'] + ' = ' + v + ' ;\n'
        else :
            i = 0
            for x,y in v.items() :
                if x in src['fsm'] :
                    txt += config['tab']*6 + ('' if i == 0 else 'else ')

                    if isinstance(y, dict) :
                        cond = ''
                        if '+' in y :
                            cond = y['+']
                        for p,q in y.items() : # Mealy export
                            if p=='+' : continue
                            if len(config['export']) > 0 :
                                config['export'][p][config['state_name'] + ' == ' + k +
                                            ' && ' + config['next_name'] + ' == ' + x] = q

                    else :
                        cond = y

                    if cond :
                        txt += 'if (' + cond + ')'

                    txt += '\n'
                    txt += config['tab']*8 + config['next_name'] + ' = ' + x + ' ;\n'
                    i += 1
                else : # Moore export
                    if len(config['export']) > 0 :
                        config['export'][x][config['state_name'] + ' == ' + k] = y

        txt += '\n'

    txt += config['tab']*4 + 'default :\n'
    txt += config['tab']*8 + config['next_name'] + ' = ' + config['init_state'] + ' ;\n'
    txt += config['tab']*2 + 'endcase\nend\n'
    return txt


def vlog_always_3rd() :
    txt  = '\nalways @(posedge ' + config['clock']

    if not config['reset_mode'] :
        txt += ', ' + ('posedge ' if config['reset_edge'] else 'negedge ') + config['reset_name']

    txt += ')\n' + config['tab']*2 + 'if (' + ('' if config['reset_edge'] else '!')
    txt += config['reset_name'] + ') begin\n'

    for k,v in src['vars'].items() :
        if v[1] != 'wire' :
            txt += config['tab']*4 + k + ' <= ' + str(v[0]) + '\'d0 ;\n'

    for k,v in src['outputs'].items() :
        if v[1] != 'wire' :
            txt += config['tab']*4 + k + ' <= ' + str(v[0]) + '\'d0 ;\n'

    txt += config['tab']*2 + 'end\n'
    txt += config['tab']*2 + 'else begin\n'


    for k,v in src['vars'].items() :
        if v[1] == 'trig' :
            txt += config['tab']*4 + k + ' <= ' + str(v[0]) + '\'d0 ;\n'

    for k,v in src['outputs'].items() :
        if v[1] == 'trig' :
            txt += config['tab']*4 + k + ' <= ' + str(v[0]) + '\'d0 ;\n'

    for k,v in config['export'].items() :
        i = 0
        txt += '\n'
        for x,y in v.items() :
            txt += config['tab']*4
            txt += '' if i==0 else 'else '
            txt += 'if (' + x + ')\n'
            txt += config['tab']*6 + k + ' <= ' + str(y) + ' ;\n'
            i += 1

    txt += config['tab']*2 + 'end\n'


    txt += '\nendmodule // fsmlog\n'

    return txt


def dot_build() :
    f  = 'digraph fsmlog {\n'
    f += 'rankdir=LR\n'  # LR, UD
    f += 'size="8,5"\n'  # 20,12 / 8,5
    # f += 'node [shape=circle]'  # doublecircle

    i = 0
    for k,v in src['fsm'].items() :  # nodes
        f += k + ' ['
        if i==0 :
            f += 'style=filled fillcolor=yellow '

        f += 'label="' + k
        if not isinstance(v, str) :
            for x,y in v.items() :
                if not x in src['fsm'] :
                    f += '\\n' + x + '=' + str(y)

        f += '"]\n'
        i += 1


    for k,v in src['fsm'].items() :  # edges
        if isinstance(v, str) :
            f += k + '->' + v + '\n'
        else :
            for x,y in v.items() :
                if not x in src['fsm'] : continue

                f += k + '->' + x + '[label="'
                if isinstance(y, dict) :
                    f += ''
                    if '+' in y :
                        f += y['+']

                    for p,q in y.items() :
                        if p=='+' : continue
                        f += ' // '
                        f += p + '=' + str(q)
                else :
                    f += y

                f += '"]\n'

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

    sys.exit(0)
