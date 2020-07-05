from collections import defaultdict

def dfs(adj_list, visited, vertex, result, key):
    visited.add(vertex)
    result[key].append(vertex)
    for neighbor in adj_list[vertex]:
        if neighbor not in visited:
            dfs(adj_list, visited, neighbor, result, key)

edges = [('c', 'e'), ('c', 'd'), ('a', 'b'), ('d', 'e'), ('a', 'v')]

adj_list = defaultdict(list)
for x, y in edges:
    adj_list[x].append(y)
    adj_list[y].append(x)

result = defaultdict(list)
visited = set()
for vertex in adj_list:
    if vertex not in visited:
        dfs(adj_list, visited, vertex, result, vertex)

print(result.values())