
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

    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as file:
            file_lines = file.readlines()
    else:
        print("file open failed")
        sys.exit(0)

    fdir = os.path.split(sys.argv[1])[0]
    with open(fdir + './out.txt', 'w') as file:
        txt = src2list(file_lines)
        file.write(txt)

    #print(txt)
    sys.exit(0)
