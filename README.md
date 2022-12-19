# FsmLog
Source is a hjson file.
```
{

inputs : {
// width
    i : 1
}

outputs : {
// width,  t/h
    y : [1,  1]
}

vars : { // internal
// width,  t/h
    x : [8,  0]
}

fsm : {
    S0 : {S1 : "i==1'b1"}

    S1 : {S2 : {+ : "i==1'b1", x : 1}
          S3 : "i==1'b0"}

    S2 : {S0 : "i==1'b1"
          S4 : ""
          y  : 1}

    S3 :  S1

    S4 : {S5 : "i==1'b0"
          S3 : {+ : "i==1'b1", x : 2} }

    S5 : {S0 : "i==1'b0"
          S2 : "i==1'b1"
          y  : 0}
}

}
```
To generate Verilog-HDL & dot-Graph from a hjson file.
```
$ python fsmlog.py example/test.hson
```

To view [dot-Graph](http://www.graphviz.org/)
```
$ dot -Tpng test.gv -o test.png
```
![](./example/test.png)
