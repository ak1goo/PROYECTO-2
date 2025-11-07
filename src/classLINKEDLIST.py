from classNODE import Node

class LinkedList:
    def __init__(self):
        self.head = None

    def push(self, data):
        n = Node(data)
        n.next = self.head
        self.head = n

    def to_list(self):
        cur = self.head
        res = []
        while cur:
            res.append(cur.data)
            cur = cur.next
        return res[::-1]
