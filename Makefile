CXX      = g++
CXXFLAGS = -std=c++17 -O2 -Wall -Wextra -pedantic
LDLIBS   = -lsfml-graphics -lsfml-window -lsfml-system

all: shortest_route

shortest_route: main.cpp
	$(CXX) $(CXXFLAGS) main.cpp -o $@ $(LDLIBS)

clean:
	rm -f shortest_route
