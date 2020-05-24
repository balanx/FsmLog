
import sys
import os

help='''

usage : src2list [source]

'''


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
    txt = txt.replace('"', ' " ')
    its = txt.split()  # split by white space
    deep = 0           # deepth of '['
    quote = False      # "
    for i in range(len(its)):
        if its[i]=='"': quote = not quote
        if quote: continue

        p1 = (its[i]=='[')
        if p1: deep += 1

        p2 = (its[i]==']')
        if p2: deep -= 1

        if deep>0:
            p3 = (its[i+1]==']')

            if not p1 and not p2:
                its[i] = '"' + its[i] + '"'
                if not p3:
                    its[i] += ','
            elif p2:       # '],'
                if not p3:    # NOT '] ]'
                    its[i] += ','
        elif deep==0 and p2:  # ']\nMACHINE=[...'
            its[i] += '\n'


    txt = ''.join(its)
    return txt


if __name__ == '__main__':

    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as file:
            file_lines = file.readlines()
    else:
        print("file open failed")
        sys.exit(0)

    ffn = os.path.split(sys.argv[1])[1]  # name+ext
    fn = os.path.splitext(ffn)[0]        # name only
    with open('./' + fn + '.txt', 'w') as file:
        txt = src2list(file_lines)
        file.write(txt)

    #print(txt)
    sys.exit(0)
