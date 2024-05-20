import heapq
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import ast
import math

def draw_polygon(ax, vertices, poly_color='#C9EAB3'):
    polygon = plt.Polygon(vertices, closed=True, edgecolor=poly_color, facecolor=poly_color)
    ax.add_patch(polygon)

def draw_route(routes, polygons=None, line_color='#D6DACD', bg_color='#FEFCF7', line_width=2, icons=None, shortest_path=None, extra_lines=None):
    plt.figure(facecolor=bg_color)
    ax = plt.gca()
    ax.set_facecolor(bg_color)

    for points in routes:
        x = [point[0] for point in points]
        y = [point[1] for point in points]
        plt.plot(x, y, color=line_color, linestyle='-', linewidth=line_width)

    if polygons:
        for vertices, color in polygons:
            draw_polygon(ax, vertices, color)
    
    if shortest_path:
        x = [point[0] for point in shortest_path]
        y = [point[1] for point in shortest_path]
        plt.plot(x, y, color='#6059FF', linestyle='-', linewidth=4)

    if extra_lines:
        for line in extra_lines:
            x = [line[0][0], line[1][0]]
            y = [line[0][1], line[1][1]]
            plt.plot(x, y, color='#6059FF', linestyle='--', linewidth=4)

    if icons:
        for (icon_coords, icon_path) in icons:
            img = plt.imread(icon_path)
            imagebox = OffsetImage(img, zoom=0.1)
            ab = AnnotationBbox(imagebox, icon_coords, frameon=False)
            ax.add_artist(ab)
    
    plt.title('Vẽ tuyến đường và đa giác', color=line_color)
    plt.xlabel('Longitude', color=line_color)
    plt.ylabel('Latitude', color=line_color)
    
    ax.tick_params(axis='x', colors=line_color)
    ax.tick_params(axis='y', colors=line_color)
    ax.spines['top'].set_color(line_color)
    ax.spines['bottom'].set_color(line_color)
    ax.spines['left'].set_color(line_color)
    ax.spines['right'].set_color(line_color)

    plt.grid(False)
    plt.show()

def read_routes_from_file(file_path):
    routes = []
    with open(file_path, 'r') as file:
        for line in file:
            route = ast.literal_eval(f'[{line.strip()}]')
            routes.append(route)
    return routes

def read_polygons_from_file(file_path):
    polygons = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(';')
            vertices = ast.literal_eval(f'[{parts[0]}]')
            color = parts[1].strip() if len(parts) > 1 else '#C9EAB3'
            polygons.append((vertices, color))
    return polygons

def read_icons_from_file(file_path):
    icons = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(';')
            coords = ast.literal_eval(f'({parts[0]})')
            icon_path = parts[1].strip()
            icons.append((coords, icon_path))
    return icons

def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def build_graph(routes):
    graph = {}
    for route in routes:
        for i in range(len(route) - 1):
            point1 = route[i]
            point2 = route[i + 1]
            distance = calculate_distance(point1, point2)
            if point1 not in graph:
                graph[point1] = []
            if point2 not in graph:
                graph[point2] = []
            graph[point1].append((point2, distance))
            graph[point2].append((point1, distance))
    return graph

def dijkstra(graph, start, goal):
    queue = [(0, start)]
    distances = {start: 0}
    previous_nodes = {start: None}
    
    while queue:
        current_distance, current_node = heapq.heappop(queue)
        
        if current_node == goal:
            break
        
        if current_node not in graph:
            raise KeyError(f"Node {current_node} is not in the graph.")
        
        for neighbor, weight in graph[current_node]:
            distance = current_distance + weight
            if neighbor not in distances or distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))
    
    path = []
    current_node = goal
    while current_node is not None:
        path.append(current_node)
        current_node = previous_nodes[current_node]
    path.reverse()
    
    return path

def find_closest_point(point, graph_points):
    closest_point = None
    min_distance = float('inf')
    for graph_point in graph_points:
        distance = calculate_distance(point, graph_point)
        if distance < min_distance:
            min_distance = distance
            closest_point = graph_point
    return closest_point

# Đọc dữ liệu từ tệp
file_path_routes = 'points.txt'
routes = read_routes_from_file(file_path_routes)
file_path_polygons = 'rectangle.txt'
polygons = read_polygons_from_file(file_path_polygons)
file_path_icons = 'icon.txt'
icons = read_icons_from_file(file_path_icons)

# Xây dựng đồ thị từ các tuyến đường
graph = build_graph(routes)
graph_points = list(graph.keys())

# Nhập tọa độ của hai điểm bất kỳ
start_point = (0, 0)
end_point = (25, 25)

# Kiểm tra xem điểm đầu và điểm cuối có nằm trong dữ liệu không
if start_point not in graph_points:
    closest_to_start = find_closest_point(start_point, graph_points)
else:
    closest_to_start = start_point

if end_point not in graph_points:
    closest_to_end = find_closest_point(end_point, graph_points)
else:
    closest_to_end = end_point

# Tìm đường đi ngắn nhất giữa hai điểm gần nhất trên đồ thị
shortest_path = dijkstra(graph, closest_to_start, closest_to_end)

# Tạo danh sách các đoạn thẳng bổ sung cần vẽ
extra_lines = []
if start_point != closest_to_start:
    extra_lines.append((start_point, closest_to_start))
if end_point != closest_to_end:
    extra_lines.append((end_point, closest_to_end))

# Add start and end icons to the icons list
start_icon_path = 'icon/starticon.png'
end_icon_path = 'icon/endicon.png'
icons.append((start_point, start_icon_path))
icons.append((end_point, end_icon_path))

# Vẽ các tuyến đường và đa giác với độ dày đường line là 5, chèn các icon và vẽ đoạn đường ngắn nhất
draw_route(routes, polygons, line_width=5, icons=icons, shortest_path=shortest_path, extra_lines=extra_lines)
