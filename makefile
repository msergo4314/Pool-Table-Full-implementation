CC = clang
# -O3 for optimization
CFLAGS = -Wall -std=c99 -pedantic -fpic -O3
.PHONY: all clean #phony targets


all: libphylib.so _phylib.so
	export LD_LIBRARY_PATH=.

libphylib.so: phylib.o
	$(CC) $(CFLAGS) phylib.o -shared -o libphylib.so -lm

_phylib.so: phylib_wrap.o libphylib.so
	$(CC) $(CFLAGS) -shared phylib_wrap.o -L. -L/usr/lib/python3.11 -lpython3.11 -lphylib -o _phylib.so

phylib.o: phylib.c phylib.h
	$(CC) $(CFLAGS) -c phylib.c -o phylib.o

phylib_wrap.c: phylib.i
	swig -python phylib.i

phylib_wrap.o: phylib_wrap.c
	$(CC) $(CFLAGS) -c phylib_wrap.c -I/usr/include/python3.11/ -fPIC -o phylib_wrap.o

clean:
	rm -f *.o *.so *.exe *.out *.svg phylib.py phylib_wrap.c