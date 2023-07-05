
.PHONY: clean run pdf png diff

run :
	python fsmlog.py ./example/test.yaml > test.v

png :
	dot -Tpng test.gv -o test.png

pdf :
	dot -Tpdf test.gv -o test.pdf

diff :
	@diff -Zsq test.v  ./example/test.v
	@diff -Zsq test.gv ./example/test.gv

clean :
	rm -f test.*

