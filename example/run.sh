#
function testing {
    /usr/bin/python3  ../../fsmlog.py  ../source/$1.flg

    diff $1.v  ../result/$1.v && diff $1.dot  ../result/$1.dot

    if test $? -eq 0
    then
        printf "  %-30s OK\n" $1
    else
        printf "\nError in '%s'\n" $1
    fi
}

cd `dirname $0`
mkdir -p ./test
cd ./test


/usr/bin/python3  ../../mylib.py  ../source/src1.flg
diff src1.txt  ../result/src1.txt
printf "  %-30s Done\n" src1

testing filt1
testing filt2
testing filt3
testing filt4

exit 0
