#include <SFML/Graphics.hpp>
#include <algorithm>
#include <array>
#include <functional>
#include <limits>
#include <queue>
#include <string>
#include <vector>

constexpr int ROWS = 20;
constexpr int COLS = 20;
constexpr int CELL = 28;
constexpr int STEP = 31;
constexpr int GRID_X = 56;
constexpr int GRID_Y = 168;
constexpr int INF = std::numeric_limits<int>::max();

struct Point {
    int row = -1;
    int col = -1;
};

bool operator==(Point a, Point b) { return a.row == b.row && a.col == b.col; }

struct SearchResult {
    std::vector<Point> visited;
    std::vector<Point> path;
};

// Dijkstra on a four-way grid. Every open cell has weight 1.
SearchResult findPath(const std::array<std::array<bool, COLS>, ROWS>& walls,
                      Point start, Point finish) {
    using QueueItem = std::pair<int, int>;
    std::priority_queue<QueueItem, std::vector<QueueItem>, std::greater<QueueItem>> queue;
    std::array<std::array<int, COLS>, ROWS> distance{};
    std::array<std::array<Point, COLS>, ROWS> previous{};

    for (int r = 0; r < ROWS; ++r) {
        distance[r].fill(INF);
        previous[r].fill(Point{});
    }

    const int startId = start.row * COLS + start.col;
    distance[start.row][start.col] = 0;
    queue.push({0, startId});
    SearchResult result;
    const int directions[4][2] = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};

    while (!queue.empty()) {
        auto [currentDistance, id] = queue.top();
        queue.pop();
        Point current{id / COLS, id % COLS};
        if (currentDistance != distance[current.row][current.col]) continue;

        result.visited.push_back(current);
        if (current == finish) break;

        for (const auto& direction : directions) {
            Point next{current.row + direction[0], current.col + direction[1]};
            if (next.row < 0 || next.row >= ROWS || next.col < 0 || next.col >= COLS ||
                walls[next.row][next.col]) continue;

            int newDistance = currentDistance + 1;
            if (newDistance < distance[next.row][next.col]) {
                distance[next.row][next.col] = newDistance;
                previous[next.row][next.col] = current;
                queue.push({newDistance, next.row * COLS + next.col});
            }
        }
    }

    if (distance[finish.row][finish.col] == INF) return result;
    for (Point current = finish;; current = previous[current.row][current.col]) {
        result.path.push_back(current);
        if (current == start) break;
    }
    std::reverse(result.path.begin(), result.path.end());
    return result;
}

enum class Mode { Walls, Start, Finish };
enum class AppState { Editing, Animating, Found, NoPath };

const sf::Color Background(14, 22, 38);
const sf::Color Panel(21, 33, 54);
const sf::Color PanelLight(27, 42, 67);
const sf::Color EmptyCell(25, 39, 61);
const sf::Color GridLine(41, 58, 83);
const sf::Color Wall(8, 15, 28);
const sf::Color Text(232, 238, 247);
const sf::Color Muted(143, 159, 181);
const sf::Color Teal(76, 205, 190);
const sf::Color Coral(255, 126, 143);
const sf::Color Visited(48, 103, 151);
const sf::Color Path(246, 198, 95);

void drawText(sf::RenderWindow& window, const sf::Font& font, const std::string& value,
              unsigned int size, sf::Color color, float x, float y) {
    sf::Text text(value, font, size);
    text.setFillColor(color);
    text.setPosition(x, y);
    window.draw(text);
}

void drawCenteredText(sf::RenderWindow& window, const sf::Font& font, const std::string& value,
                      unsigned int size, sf::Color color, sf::FloatRect box) {
    sf::Text text(value, font, size);
    text.setFillColor(color);
    sf::FloatRect bounds = text.getLocalBounds();
    text.setPosition(box.left + (box.width - bounds.width) / 2.f - bounds.left,
                     box.top + (box.height - bounds.height) / 2.f - bounds.top);
    window.draw(text);
}

void drawCard(sf::RenderWindow& window, sf::FloatRect box) {
    sf::RectangleShape card({box.width, box.height});
    card.setPosition(box.left, box.top);
    card.setFillColor(Panel);
    card.setOutlineThickness(1.f);
    card.setOutlineColor(GridLine);
    window.draw(card);
}

void drawKey(sf::RenderWindow& window, const sf::Font& font, const std::string& key,
             float x, float y, float width = 36.f) {
    sf::RectangleShape keycap({width, 30.f});
    keycap.setPosition(x, y);
    keycap.setFillColor(PanelLight);
    keycap.setOutlineThickness(1.f);
    keycap.setOutlineColor(GridLine);
    window.draw(keycap);
    drawCenteredText(window, font, key, 13, Text, {x, y, width, 30.f});
}

Point cellAt(sf::Vector2i mouse) {
    int x = mouse.x - GRID_X;
    int y = mouse.y - GRID_Y;
    if (x < 0 || y < 0) return {};
    int col = x / STEP;
    int row = y / STEP;
    if (row >= ROWS || col >= COLS || x % STEP >= CELL || y % STEP >= CELL) return {};
    return {row, col};
}

bool valid(Point point) { return point.row >= 0 && point.col >= 0; }

bool loadFont(sf::Font& font) {
    const std::vector<std::string> paths = {
        "assets/DejaVuSans.ttf",
        "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf"
    };
    for (const std::string& path : paths) {
        if (font.loadFromFile(path)) return true;
    }
    return false;
}

int main() {
    sf::RenderWindow window(sf::VideoMode(1180, 850), "Shortest Route Finder",
                            sf::Style::Titlebar | sf::Style::Close);
    window.setFramerateLimit(60);

    sf::Font font;
    if (!loadFont(font)) return 1;

    std::array<std::array<bool, COLS>, ROWS> walls{};
    std::array<std::array<bool, COLS>, ROWS> visited{};
    std::array<std::array<bool, COLS>, ROWS> pathCells{};
    Point start{9, 4};
    Point finish{10, 15};
    Mode mode = Mode::Walls;
    AppState state = AppState::Editing;
    SearchResult search;
    bool paintingWalls = true;
    float animationClock = 0.f;
    std::size_t visitedShown = 0;
    std::size_t pathShown = 0;
    std::string status = "Ready to explore";

    auto clearSearch = [&]() {
        visited = {};
        pathCells = {};
        search = {};
        visitedShown = pathShown = 0;
        animationClock = 0.f;
        state = AppState::Editing;
        status = "Ready to explore";
    };

    auto reset = [&]() {
        walls = {};
        start = {9, 4};
        finish = {10, 15};
        mode = Mode::Walls;
        clearSearch();
    };

    sf::Clock clock;
    while (window.isOpen()) {
        float delta = clock.restart().asSeconds();
        sf::Event event{};
        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed) window.close();

            if (event.type == sf::Event::KeyPressed) {
                if (event.key.code == sf::Keyboard::R) reset();
                if (event.key.code == sf::Keyboard::S && state != AppState::Animating) {
                    mode = Mode::Start;
                    status = "Click a cell to place the start";
                }
                if (event.key.code == sf::Keyboard::E && state != AppState::Animating) {
                    mode = Mode::Finish;
                    status = "Click a cell to place the destination";
                }
                if (event.key.code == sf::Keyboard::Space && state != AppState::Animating) {
                    clearSearch();
                    search = findPath(walls, start, finish);
                    state = AppState::Animating;
                    status = "Exploring the grid...";
                }
            }

            if (event.type == sf::Event::MouseButtonPressed &&
                event.mouseButton.button == sf::Mouse::Left && state != AppState::Animating) {
                Point point = cellAt({event.mouseButton.x, event.mouseButton.y});
                if (!valid(point)) continue;

                if (mode == Mode::Start) {
                    if (!(point == finish) && !walls[point.row][point.col]) start = point;
                    mode = Mode::Walls;
                    clearSearch();
                    status = "Start updated — press Space to search";
                } else if (mode == Mode::Finish) {
                    if (!(point == start) && !walls[point.row][point.col]) finish = point;
                    mode = Mode::Walls;
                    clearSearch();
                    status = "Destination updated — press Space to search";
                } else {
                    if (!(point == start) && !(point == finish)) {
                        paintingWalls = !walls[point.row][point.col];
                        walls[point.row][point.col] = paintingWalls;
                        clearSearch();
                    }
                }
            }

            if (event.type == sf::Event::MouseMoved && sf::Mouse::isButtonPressed(sf::Mouse::Left) &&
                mode == Mode::Walls && state != AppState::Animating) {
                Point point = cellAt({event.mouseMove.x, event.mouseMove.y});
                if (valid(point) && !(point == start) && !(point == finish)) {
                    walls[point.row][point.col] = paintingWalls;
                    clearSearch();
                }
            }
        }

        if (state == AppState::Animating) {
            animationClock += delta;
            const float interval = visitedShown < search.visited.size() ? 0.025f : 0.07f;
            while (animationClock >= interval) {
                animationClock -= interval;
                if (visitedShown < search.visited.size()) {
                    Point point = search.visited[visitedShown++];
                    visited[point.row][point.col] = true;
                } else if (pathShown < search.path.size()) {
                    Point point = search.path[pathShown++];
                    pathCells[point.row][point.col] = true;
                } else {
                    state = search.path.empty() ? AppState::NoPath : AppState::Found;
                    status = search.path.empty() ? "No route exists between these points"
                                                 : "Shortest route is ready";
                    break;
                }
            }
        }

        window.clear(Background);

        drawText(window, font, "ROUTE LAB", 13, Teal, 44.f, 30.f);
        drawText(window, font, "Shortest Route Finder", 30, Text, 44.f, 53.f);
        drawText(window, font, "A calm way to see Dijkstra's algorithm think.", 14, Muted, 48.f, 98.f);
        sf::RectangleShape headerLine({1092.f, 1.f});
        headerLine.setPosition(44.f, 132.f);
        headerLine.setFillColor(GridLine);
        window.draw(headerLine);

        drawCard(window, {40.f, 150.f, 650.f, 650.f});
        for (int row = 0; row < ROWS; ++row) {
            for (int col = 0; col < COLS; ++col) {
                sf::Color color = EmptyCell;
                if (walls[row][col]) color = Wall;
                else if (pathCells[row][col]) color = Path;
                else if (visited[row][col]) color = Visited;
                if (Point{row, col} == start) color = Teal;
                if (Point{row, col} == finish) color = Coral;

                sf::RectangleShape cell({static_cast<float>(CELL), static_cast<float>(CELL)});
                cell.setPosition(static_cast<float>(GRID_X + col * STEP),
                                 static_cast<float>(GRID_Y + row * STEP));
                cell.setFillColor(color);
                window.draw(cell);

                if (Point{row, col} == start || Point{row, col} == finish) {
                    drawCenteredText(window, font, Point{row, col} == start ? "S" : "E",
                                     13, Background, {static_cast<float>(GRID_X + col * STEP),
                                                      static_cast<float>(GRID_Y + row * STEP),
                                                      static_cast<float>(CELL), static_cast<float>(CELL)});
                }
            }
        }

        drawText(window, font, "20 × 20  ·  four-way movement", 12, Muted, 56.f, 772.f);

        drawCard(window, {720.f, 150.f, 420.f, 142.f});
        drawText(window, font, "STATUS", 11, Muted, 744.f, 171.f);
        sf::CircleShape statusDot(5.f);
        statusDot.setPosition(745.f, 205.f);
        statusDot.setFillColor(state == AppState::NoPath ? Coral : (state == AppState::Found ? Path : Teal));
        window.draw(statusDot);
        drawText(window, font, status, 17, Text, 764.f, 198.f);
        drawText(window, font, state == AppState::Animating ? "Watching the frontier expand"
                                                            : "Your map is in your hands",
                 13, Muted, 744.f, 237.f);

        drawCard(window, {720.f, 310.f, 420.f, 128.f});
        drawText(window, font, "BUILD YOUR MAP", 11, Muted, 744.f, 331.f);
        drawKey(window, font, "S", 744.f, 361.f);
        drawText(window, font, "place start", 14, Text, 790.f, 366.f);
        drawKey(window, font, "E", 924.f, 361.f);
        drawText(window, font, "place destination", 14, Text, 970.f, 366.f);
        drawText(window, font, "Left-click + drag to paint or erase walls", 13, Muted, 744.f, 406.f);

        drawCard(window, {720.f, 456.f, 420.f, 151.f});
        drawText(window, font, "RUN THE SEARCH", 11, Muted, 744.f, 477.f);
        drawKey(window, font, "SPACE", 744.f, 509.f, 76.f);
        drawText(window, font, "find shortest route", 16, Text, 836.f, 514.f);
        drawKey(window, font, "R", 744.f, 553.f);
        drawText(window, font, "reset the board", 14, Muted, 790.f, 558.f);

        drawCard(window, {720.f, 625.f, 420.f, 175.f});
        drawText(window, font, "LEGEND", 11, Muted, 744.f, 646.f);
        const std::array<std::pair<std::string, sf::Color>, 5> legend = {{{"Start", Teal},
            {"Destination", Coral}, {"Visited", Visited}, {"Shortest path", Path}, {"Wall", Wall}}};
        for (std::size_t i = 0; i < legend.size(); ++i) {
            float x = 744.f + (i % 2) * 190.f;
            float y = 676.f + (i / 2) * 34.f;
            sf::RectangleShape swatch({14.f, 14.f});
            swatch.setPosition(x, y + 3.f);
            swatch.setFillColor(legend[i].second);
            window.draw(swatch);
            drawText(window, font, legend[i].first, 13, Text, x + 24.f, y);
        }

        window.display();
    }
    return 0;
}
