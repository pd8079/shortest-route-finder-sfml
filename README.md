# Shortest Route Finder

A small SFML desktop app that visualizes Dijkstra's algorithm on a 20 × 20 grid.

## Requirements

This project was written for **SFML 2.5.1**, the version available in the Debian 12
environment used to build it.

On Debian or Ubuntu, install the compiler and SFML development files with:

```bash
sudo apt update
sudo apt install g++ make libsfml-dev
```

`libsfml-dev` provides SFML 2.5.x on Debian 12. If SFML is already installed,
check the version with:

```bash
pkg-config --modversion sfml-graphics
```

### Bazzite / Fedora

The executable must be built on Bazzite so it links to the SFML version installed
there. Install the Fedora packages, reboot when `rpm-ostree` asks, then rebuild:

```bash
sudo rpm-ostree install gcc-c++ make SFML-devel
reboot
cd /var/home/srodrigues/Desktop/DSA_project
rm -f shortest_route
make
./shortest_route
```

On regular Fedora, use `sudo dnf install gcc-c++ make SFML-devel`
instead. Rebuilding matters because a binary compiled on Debian may look for
`libsfml-graphics.so.2.5`, which may not be installed on a newer Fedora/Bazzite
system. The project includes its own font in `assets/DejaVuSans.ttf`, so no font
package is required.

## Build and run

```bash
make
./shortest_route
```

## Controls

- **Left-click + drag:** add walls; start on a wall to erase walls.
- **S**, then click a cell: set the start point.
- **E**, then click a cell: set the destination.
- **Space:** run Dijkstra's algorithm and animate the result.
- **R:** clear the walls and reset the points.

The grid uses four-way movement. If the destination cannot be reached, the status
panel reports that no route exists.
