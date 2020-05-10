
import sys
import os

help='''

usage : fsmlog [source]

'''

class FsmLog():
    name = 'fsm'
    clock  = [  'clk', 'posedge']
    reset  = ['rst_n', 'negedge']  # [] is None
    enable = ['en', "1'b1"]        # [] is None
    tab  = '  '

    def __init__(self, machine=[[]], export=[[]], vars=[[],[],[]]):
        self.machine = machine
        self.export  = export
        self.vars    = vars

    def dot(self):
        txt = 'digraph fsm {\n'    # rankdir=LR size="8,5"\n'
        #txt += '"@FsmLog"[shape = "plaintext"]\n\n'

        #######################
        # Edges
        #
        nodes={}
        for i in self.machine:     # machine1, machine2
            for j in i:  # node1, node2
                nodes[j[0]]= j[0] #+ '\\n'
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
                v = j[0]            # var name
                h = j[1]            # hold
                for k in range(2, len(j), 2):   # out1, out2
                    if h == 0:
                        nodes[j[k]] += '\\n' + v + '=' + j[k+1]
                    else:
                        nodes[j[k]] += '\\n' + v + '(' + j[k+1] + ')'

        start_point = True
        for d,x in nodes.items():   # node1, node2
            txt += d + '[label="' + x + '"'
            if start_point:
                txt += ' style=filled fillcolor=yellow'
                start_point = not start_point

            txt += ']\n'

        txt += '} // @FsmLog'
        return txt

    def log2(self, n):
        i = 1
        while (2**i < n) and (i < 32):
            i += 1

        return i

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
        for i in self.vars[1]:
            txt += self.tab + 'output reg '
            init[i[0]] = str(i[1]) + "'d0"
            if len(i)>2:
                init[i[0]] = str(i[1]) + "'d" + str(i[2])

            if i[1]>1:
                txt += '[' + str(i[1]-1) + ':0] '
            else:
                txt += self.tab

            txt += i[0] + ' = ' + init[i[0]] + ',\n'

        #######################
        # input definition
        #
        for i in self.vars[0]:
            txt += self.tab + 'input      '
            if i[1]>1:
                txt += '[' + str(i[1]-1) + ':0] ' + i[0] + ',\n'
            else:
                txt += self.tab + i[0] + ',\n'

        txt += '\n'
        if self.enable != []:
            txt += self.tab + 'input' + self.tab*2 + self.enable[0] + ',\n'

        if self.reset != []:
            txt += self.tab + 'input' + self.tab*2 + self.reset[0] + ',\n'

        txt += self.tab + 'input' + self.tab*2 + self.clock[0]
        txt += '\n);\n\n'

        #######################
        # inner vars definition
        #
        for i in self.vars[2]:
            init[i[0]] = str(i[1]) + "'d0"
            if len(i)>2:
                init[i[0]] = str(i[1]) + "'d" + str(i[2])

            txt += 'reg '
            if i[1]>1:
                txt += '[' + str(i[1]-1) + ':0] '
            else:
                txt += self.tab

            txt += i[0] + ' = ' + init[i[0]] + ';\n'

        #print(init)

        #######################
        # state definition
        #
        m = 1
        for i in self.machine:      # machine1, machine2
            st = 'state' + str(m)
            nx =  'next' + str(m)
            width =  self.log2(len(i))

            txt += '\nlocalparam'
            n = 0
            for j in i:   # node1, node2
                txt += '\n' + j[0] + ' = ' + str(width) + "'d" + str(n) + ','
                n += 1

            txt = txt[:-1]  # delete the last ','
            txt += ';\n\nreg [' + str(width - 1) + ':0] ' + st + ', ' + nx + ';\n'

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
                    if cond == '':
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
                    txt += self.tab + j[0] + ' <= ' + init[j[0]] + ';\n'
                #
                txt += 'end\nelse begin\n'

            nodes = {}
            for j in i:                 # v1, v2
                for k in range(2, len(j), 2):
                    nodes[j[k]] = ''

            for j in i:                 # v1, v2
                txt += self.tab
                if j[1] == 1:           # hold
                    txt  = txt[:-2]
                    txt += '//'

                txt += j[0] + ' <= ' + init[j[0]] + ';\n'
                #
                for k in range(2, len(j), 2):
                    nodes[j[k]] += self.tab*4 + j[0] + ' <= ' + j[k+1] + ';\n'

            txt += '\n' + self.tab + 'case (' + st + ')\n'
            for k,x in nodes.items():
                txt += self.tab*2 + k + ' : begin\n' + x + self.tab*3 + 'end\n'


            txt += '\n' + self.tab + 'endcase\nend\n'
            m += 1

        #######################
        # misc
        #

        txt += '\nendmodule // @FsmLog\n'

        return txt


def src2list(file_lines):
    txt = ''
    for i in file_lines:
        p = i.find('#')
        if p<0:
            txt += i
        else:
            txt += i[:p] + '\n'

    txt = txt.replace('[', ' [ ') # split '[' from others, very important
    txt = txt.replace(']', ' ] ')
    its = txt.split()  # split by white space
    deep = 0           # deepth of '['
    for i in range(len(its)):
        p1 = -1
        p1 = its[i].find('[')
        if p1>=0: deep += 1

        p2 = -1
        p2 = its[i].find(']')
        if p2>=0: deep -= 1

        if deep>0:
            p3 = -1
            p3 = its[i+1].find(']')

            if p1== -1 and p2== -1:
                its[i] = '"' + its[i] + '"'
                if p3<0:
                    its[i] += ','
            elif p2==0:     # '],'
                if p3<0:    # NOT '] ]'
                    its[i] += ','
        elif deep==0 and p2>=0:  # ']\nMACHINE=[...'
            its[i] += '\n'


    txt = ''.join(its)
    return txt


if __name__ == '__main__':

    GVBIN = 'dot.exe'
    GVFORMAT = 'pdf'

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

    fg = FsmLog(MACHINE, EXPORT, VARS)
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
    with open(fdir + '/' + fn + '.dot', 'w') as file:
        file.write(src)
        print("Dot is OK.")

    src = fg.hdl()
    with open(fdir + '/' + fn + '.v', 'w') as file:
        file.write(src)
        print("HDL is OK.")

    if os.path.exists(GVBIN) and os.path.isfile(GVBIN):
        os.system(GVBIN + ' -T' + GVFORMAT + ' ' +
                    fdir + '/' + fn +'.dot -o ' +
                    fdir + '/' + fn + '.' + GVFORMAT)
        print("Image is OK.")
    else:
        print('GVBIN is NOT found at ' + GVBIN)

    sys.exit(0)
