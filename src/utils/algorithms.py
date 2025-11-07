# utils/algorithms.py

#ORDENAMIENTO

def bubble_sort(lista, key=lambda x: x):
    
    n = len(lista)
    for i in range(n):
        for j in range(0, n - i - 1):
            if key(lista[j]) > key(lista[j + 1]):
                lista[j], lista[j + 1] = lista[j + 1], lista[j]
    return lista


def selection_sort(lista, key=lambda x: x):
    
    n = len(lista)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if key(lista[j]) < key(lista[min_idx]):
                min_idx = j
        lista[i], lista[min_idx] = lista[min_idx], lista[i]
    return lista


#BÚSQUEDA 

def busqueda_lineal(lista, key, valor):
    
    for item in lista:
        if key(item) == valor:
            return item
    return None


def busqueda_binaria(lista, key, valor):
    
    low, high = 0, len(lista) - 1
    while low <= high:
        mid = (low + high) // 2
        if key(lista[mid]) == valor:
            return lista[mid]
        elif key(lista[mid]) < valor:
            low = mid + 1
        else:
            high = mid - 1
    return None
