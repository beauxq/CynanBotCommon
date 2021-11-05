from typing import Dict

try:
    import CynanBotCommon.utils as utils
except:
    import utils

# This class was taken from online:
# https://gist.github.com/jerryan999/6677a2619e8175e54ed05d3c6e1621cf
#
# I then slightly tweaked it for simplifcation... fingers crossed it works

class LinkedNode():

    def __init__(self, key: str):
        if not utils.isValidStr(key):
            raise ValueError(f'key argument is malformed: \"{key}\"')

        self.key: str = key
        self.next: LinkedNode = None
        self.prev: LinkedNode = None


class LruCache():

    def __init__(self, capacity: int):
        if not utils.isValidNum(capacity):
            raise ValueError(f'capacity argument is malformed: \"{capacity}\"')
        elif capacity < 8:
            raise ValueError(f'capacity argument is too small: {capacity}')

        self.__capacity: int = capacity
        self.__lookup: Dict[str, LinkedNode] = dict()
        self.__stub: LinkedNode = LinkedNode("stub")
        self.head: LinkedNode = self.__stub.next
        self.tail: LinkedNode = self.__stub.next

    def __append_new_node(self, new_node: LinkedNode):
        """  add the new node to the tail end
        """
        if not self.tail:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = self.tail.next

    def contains(self, key: str) -> bool:
        if not utils.isValidStr(key) or key not in self.__lookup:
            return False

        node = self.__lookup[key]

        if node is not self.tail:
            self.__unlink_cur_node(node)
            self.__append_new_node(node)

        return True

    def put(self, key: str):
        if not utils.isValidStr(key):
            raise ValueError(f'key argument is malformed: \"{key}\"')

        if key in self.__lookup:
            self.contains(key)
            return

        if len(self.__lookup) == self.__capacity:
            # remove head node and corresponding key
            self.__lookup.pop(self.head.key)
            self.__remove_head_node()

        # add new node and hash key
        newNode: LinkedNode = LinkedNode(key)
        self.__lookup[key] = newNode
        self.__append_new_node(newNode)

    def __remove_head_node(self):
        if not self.head:
            return

        prev = self.head
        self.head = self.head.next

        if self.head:
            self.head.prev = None

        del prev

    def __unlink_cur_node(self, node: LinkedNode):
        """ unlink current linked node
        """
        if self.head is node:
            self.head = node.next

            if node.next:
                node.next.prev = None

            return

        # removing the node from somewhere in the middle; update pointers
        prev, nex = node.prev, node.next
        prev.next = nex    
        nex.prev = prev
