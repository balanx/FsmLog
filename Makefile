
.PHONY: clean run pdf png diff

run :
	python fsmlog.py ./example/test.hson > test.sv

png :
	dot -Tpng test.gv -o test.png

pdf :
	dot -Tpdf test.gv -o test.pdf

diff :
	dos2unix test.sv
	dos2unix test.gv
	diff test.sv ./example/test.sv
	diff test.gv ./example/test.gv

clean :
	rm -f test.*

