#
import sys
import os
from mylib import src2list, log2

help='''

usage : fsmlog [source]

'''

class FsmLog():
    name = 'fsm'
    clock  = [  'clk', 'posedge']
    reset  = ['rst_n', 'negedge']  # [] is None
    enable = ['en', "1'b1"]        # [] is None
    tab  = '  '

    def __init__(self, machine=[[]], export=[[]], inputs=[[]], outputs=[[]], regs=[[]] ):
        self.machine = machine
        self.export  = export
        self.inputs  = inputs
        self.outputs = outputs
        self.regs    = regs

    def dot(self):
        txt = 'digraph fsm {\n'    # rankdir=LR size="8,5"\n'
        #txt += '"@FsmLog"[shape = "plaintext"]\n\n'

        #######################
        # Edges
        #
        nodes={}
        for i in self.machine:     # machine1, machine2
            for j in i:  # node1, node2
                nodes[j[0]]= [j[0], '']
                n = len(j)
                if n%2==0:
                    print('Error: missing items at machine of ', j[0])
                for k in range(1,n,2):
                    next = j[k]
                    cond = j[k+1]
                    edge = j[0] + '->' + next + '[label="' + cond + '"]\n'
                    txt += edge

        txt += '\n'

        #######################
        # Nodes
        #
        for i in self.export:       # exp1, exp2
            for j in i:             # v1, v2
                if j[1]=='9': continue
                v = j[0]            # var name
                h = j[1]            # hold
                for k in range(2, len(j), 2):   # out1, out2
                    if h == '0':
                        nodes[j[k]][0] += '\\n' + v + '=' + j[k+1]
                    elif h == '1':
                        nodes[j[k]][0] += '\\n' + v + '(' + j[k+1] + ')'
                    elif h == '2':
                        nodes[j[k]][1] += j[0] + '=' + j[k+1] + '\\n'

        start_point = True
        for d,x in nodes.items():   # node1, node2
            txt += d + '[label="' + x[0] + '"'
            if start_point:
                txt += ' style=filled fillcolor=yellow'
                start_point = not start_point

            txt += ']\n'
            if x[1]!='':
                txt += d + '->' + d + '[color=white, label="' + x[1][:-2] + '"]\n'

        txt += '} # @FsmLog'
        return txt


    def hdl(self):
        always = 'always @(' + self.clock[1] + ' ' + self.clock[0]
        if self.reset != []:
            always += ' or ' + self.reset[1] + ' ' + self.reset[0] + ')\nif ('
            if self.reset[1] == 'negedge':
                always += '!'

            always += self.reset[0]

        always += ')'

        #######################
        # output definition
        #
        init = {}
        txt = '\nmodule ' + self.name + ' (\n'
        assign = ''
        for i in self.outputs:
            txt += self.tab + 'output '
            if len(i)>=4 and i[2]=='=':
                txt += '    '
                assign += '\nassign ' + i[0] + ' = ' + ''.join(i[3:]) + ';'
            else:
                txt += 'reg '

            w = int(i[1])   # width
            if w>1:
                txt += '[' + str(w-1) + ':0] '
            else:
                txt += '      '

            init[i[0]] = [i[1] + "'d"]*2    # {'out': ["1'd", "1'd0"], }
            if len(i)==3:
                init[i[0]][1] += i[2]
            elif len(i)==2:
                init[i[0]][1] += '0'

            txt += i[0]
            if len(i)>=4:
                txt += ',\n'
            else:
                txt += ' = ' + init[i[0]][1] + ',\n'

        #######################
        # input definition
        #
        for i in self.inputs:
            w = int(i[1])   # width
            txt += self.tab + 'input      '
            if w>1:
                txt += '[' + str(w-1) + ':0] ' + i[0] + ',\n'
            else:
                txt += '      ' + i[0] + ',\n'

        txt += '\n'
        if self.enable != []:
            txt += self.tab + 'input' + self.tab*2 + self.enable[0] + ',\n'

        if self.reset != []:
            txt += self.tab + 'input' + self.tab*2 + self.reset[0] + ',\n'

        txt += self.tab + 'input' + self.tab*2 + self.clock[0]
        txt += '\n);\n'

        #######################
        # inner vars definition
        #
        wire = ''
        for i in self.regs:
            w = int(i[1])   # width
            if w>1:
                w = '[' + str(w-1) + ':0] '
            else:
                w = self.tab

            if len(i)>=4 and i[2]=='=':
                wire += '\nwire' + w + i[0] + ' = ' + ''.join(i[3:]) + ';'
            else:
                txt += '\nreg ' + w

            init[i[0]] = [i[1] + "'d"]*2
            if len(i)==3:
                init[i[0]][1] += i[2]
            elif len(i)==2:
                init[i[0]][1] += '0'

            if len(i)<4:
                txt += i[0] + ' = ' + init[i[0]][1] + ';'

        if len(wire+assign)>0: txt += '\n'

        txt += wire + assign + '\n'

        #######################
        # state definition
        #
        m = 1
        for i in self.machine:      # machine1, machine2
            st = 'state' + str(m)
            nx =  'next' + str(m)
            width =  log2(len(i))

            txt += '\nlocalparam'
            n = 0
            for j in i:   # node1, node2
                txt += '\n' + j[0] + ' = ' + width + "'d" + str(n) + ','
                n += 1

            txt = txt[:-1]  # delete the last ','
            txt += ';\n\nreg [' + str(int(width) - 1) + ':0] ' + st + ', ' + nx + ';\n'

            txt += always + '\n'
            if self.reset != []:
                txt += self.tab + st + ' <= ' + i[0][0] + ';\nelse '

            if self.enable != []:
                txt += 'if (' + self.enable[0] + ' == ' + self.enable[1] + ')\n'
            elif self.reset != []:
                txt = txt[:-1] + '\n'

            txt += self.tab + st + ' <= ' + nx + ';\n\n'
            m += 1


        #######################
        # next-state block
        #
        m = 1
        for i in self.machine:       # fsm1, fsm2
            st = 'state' + str(m)
            nx =  'next' + str(m)
            txt += '\nalways @(*) begin\n'
            txt += self.tab + nx + ' = ' + st + ';\n\n'
            txt += self.tab + 'case(' + st + ')\n'

            for j in i:  # node1, node2
                txt += self.tab*2 + j[0] + ' :\n'
                n = len(j)
                if n%2==0:
                    print('Error: missing items at machine of ', j[0])
                    sys.exit(0)
                for k in range(1,n,2):
                    next = j[k]
                    cond = j[k+1]
                    if cond == '-':
                        if k > 1:
                            txt += self.tab*3 + 'else\n'
                    elif k > 1:
                        txt += self.tab*3 + 'else if (' + cond + ')\n'
                    else:
                        txt += self.tab*3 + 'if (' + cond + ')\n'

                    txt += self.tab*4 + nx + ' = ' + next + ';\n'

            txt += self.tab*2 + 'default :\n' + self.tab*4 + nx + ' = ' + i[0][0] + ';\n'
            txt += self.tab + 'endcase\nend\n'
            m += 1

        #sys.exit(0)
        #######################
        # export block
        #
        m = 1
        for i in self.export:
            st = 'state' + str(m)

            txt += '\n' + always + ' begin\n'
            if self.reset != []:
                for j in i:             # v1, v2
                    txt += self.tab + j[0] + ' <= ' + init[j[0]][1] + ';\n'

                txt += 'end\nelse begin\n'

            for j in i:                 # v1, v2
                if j[1] == '2':
                    txt += self.tab + j[0] + ' <= ' + init[j[0]][1] + ';\n'
                elif j[1]=='9':
                    txt += self.tab
                    if j[2][:3]=='if(':
                        txt += ' '.join(j[2:]) + ';\n'
                    else:
                        txt += j[0] + ' <= ' + ' '.join(j[2:]) + ';\n'

            txt += '//following 0,1\n'
            if self.enable != []:
                txt += '\n' + self.tab + 'if (' + self.enable[0] + ' == ' + self.enable[1] + ') begin\n'

            nodes = {}
            for j in i:                 # v1, v2
                if j[1]=='9': continue
                for k in range(2, len(j), 2):
                    nodes[j[k]] = ''

            for j in i:                 # v1, v2
                if j[1]=='9': continue

                if j[1]=='0' or j[1]=='1':
                    txt += self.tab*2
                    if j[1] == '1':         # hold
                        txt  = txt[:-2]
                        txt += '//'

                    txt += j[0] + ' <= ' + init[j[0]][1] + ';\n'

                for k in range(2, len(j), 2):
                    x = j[k+1]
                    nodes[j[k]] += self.tab*4
                    if x.isdecimal():   # ddd
                        nodes[j[k]] += j[0] + ' <= ' + init[j[0]][0] + x + ';\n'
                    elif len(x)>2 and x[:2]=='++':
                        x = x[2:].split(':')
                        nodes[j[k]] += j[0] + ' <= ' + j[0] + ' + ' + log2(int(x[0])) + "'d" + x[0] + ';\n'
                        if len(x)==2:
                            nodes[j[k]] += self.tab*4 + 'if('
                            if x[1].isdecimal():
                                nodes[j[k]] += j[0] + ' >= ' + init[j[0]][0] + x[1]
                            else:
                                nodes[j[k]] += x[1]

                            nodes[j[k]] += ') ' + j[0] + ' <= ' + init[j[0]][1] + ';\n'

                    elif x[:3]=='if(':
                        nodes[j[k]] += x + ';\n'
                    else:   # name = var
                        nodes[j[k]] += j[0] + ' <= ' + x + ';\n'

            txt += '\n' + self.tab*2 + 'case (' + st + ')\n'
            for k,x in nodes.items():
                txt += self.tab*3 + k + ' : begin\n' + x + self.tab*3 + 'end\n'

            txt += self.tab*2 + 'endcase\n'
            if self.enable != []:
                txt += self.tab + 'end\n'

            txt += 'end\n'
            m += 1

        #######################
        # misc
        #

        txt += '\nendmodule // @FsmLog\n'

        return txt


if __name__ == '__main__':

    GVBIN = 'dot.exe'
    GVFORMAT = 'pdf'
    INPUTS =[]
    OUTPUTS =[]
    REGS =[]
    EXPORT = []

    # read global.cfg
    fdir = os.path.split(sys.argv[0])[0]
    if fdir == '': fdir = '.'
    with open(fdir + '/global.cfg', 'r') as file:
        exec(file.read())

    # read source.fl
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as file:
            file_lines = file.readlines()
            exec(src2list(file_lines))
    else:
        print(help)
        sys.exit(0)

    fdir, full_fn = os.path.split(sys.argv[1])
    fn = os.path.splitext(full_fn)[0]  # module name
    if fdir == '': fdir = '.'
    #print(fdir, full_fn, fn)

    fg = FsmLog(MACHINE, EXPORT, INPUTS, OUTPUTS, REGS)
    fg.name = fn
    fg.reset = []
    fg.enable = []
    if  'CLOCK' in dir():
        fg.clock = CLOCK
    if  'RESET' in dir():
        fg.reset = RESET
    if 'ENABLE' in dir():
        fg.enable = ENABLE

    src = fg.dot()
    with open('./' + fn + '.dot', 'w') as file:
        file.write(src)
        print("Dot is OK.")

    src = fg.hdl()
    with open('./' + fn + '.v', 'w') as file:
        file.write(src)
        print("HDL is OK.")

    if os.path.exists(GVBIN) and os.path.isfile(GVBIN):
        os.system(GVBIN + ' -T' + GVFORMAT +
                     ' ./' + fn +'.dot -o' +
                     ' ./' + fn + '.' + GVFORMAT)
        print("Image is OK.")
    else:
        print('GVBIN is NOT found at ' + GVBIN)

    sys.exit(0)
