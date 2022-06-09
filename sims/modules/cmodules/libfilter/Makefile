CFLAGS=-fPIC
libfilter.so: obj/libfilter.o
	gcc ${CFLAGS} -shared  obj/*.o -o libfilter.so
obj/libfilter.o: libfilter.c libfilter.h
	gcc ${CFLAGS} -c libfilter.c -o obj/libfilter.o