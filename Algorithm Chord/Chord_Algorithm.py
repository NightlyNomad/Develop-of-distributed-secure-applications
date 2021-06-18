import numpy as np

M = 10
id_M = [0, 1, 3, 4, 5, 6, 11, 12, 15, 18, 21, 125, 144]
CHORD_LIST = [0] * 2 ** M


class CHORD(object):

    def __init__(self, id_n):
        self.id = id_n
        self.M = M
        self.finger_start_f()
        self.finger_int_f()
        self.node_f()
        self.succes_f()
        self.pred_f()
        self.table = list(zip(self.finger_start, self.finger_int, self.node))
        CHORD_LIST[id_n] = self
        if id_n not in id_M:
            id_M.append(id_n)

    def finger_start_f(self):
        self.finger_start = [(self.id + 2 ** (i - 1)) % 2 ** M for i in range(1, M + 1)]
        # return finger_start

    def finger_int_f(self):
        finger_int = []

        for x in range(len(self.finger_start)):
            if (x + 1) != len(self.finger_start):
                finger_int.append((self.finger_start[x], self.finger_start[x + 1]))
            else:
                finger_int.append((self.finger_start[x], self.id))

        self.finger_int = finger_int

    def node_f(self):
        node_n = []
        a = np.array(sorted(id_M))

        for i in self.finger_start:
            if i <= max(a):
                node_n.append(a[a >= i][0])

            else:
                node_n.append(a[0])

        self.node = node_n

    def succes_f(self, ):
        self.succes = self.node[0]

    def pred_f(self):
        node_n = []
        a = np.array(sorted(id_M))

        for i in self.finger_start:
            if i == 0:
                minn = max(a)
                node_n.append(minn)
            else:
                minn = a[a < i][-1]
                node_n.append(minn)

        if node_n[0] == min(a):
            self.pred = max(a)
        else:
            self.pred = a[a < node_n[0]][-1]

    def after_add_del(self):
        """
            Метод вызываемый после удаления или добавление
        """
        self.finger_start_f()
        self.finger_int_f()
        self.node_f()
        self.succes_f()
        self.pred_f()
        self.table = list(zip(self.finger_start, self.finger_int, self.node))

    def add(self, id_m):
        """
            Добавление
        """
        if id_m not in id_M:
            id_M.append(id_m)
            CHORD_LIST[id_m] = CHORD(id_m)
            self.after_add_del()
            ne = self

            for v in range(len(id_M) - 1):
                ne = ne.find(ne.succes)
                ne.after_add_del()
                ne = ne.find(ne.succes)

    def find(self, id_m):
        """
            Поиск
        """
        if id_m == self.id:
            return self

        a = np.array(sorted(id_M))
        if (id_m < min(self.finger_start)) and (CHORD_LIST[self.succes].id == id_m):
            return CHORD_LIST[self.succes]
        else:
            return CHORD_LIST[self.succes].find(id_m)

        arg_n = np.argmax(np.array(self.finger_start)[np.array(self.finger_start) <= id_m])
        f = self.node[arg_n]

        if CHORD_LIST[f].id == id_m:
            return CHORD_LIST[f]
        else:
            return CHORD_LIST[f].find(id_m)

    def delete(self, id_m):
        """
            Удаление
        """
        if id_m in id_M:
            ne = self
            delete_nod = ne.find(id_m)
            d_suc = delete_nod.find(delete_nod.succes)
            d_pred = delete_nod.find(delete_nod.pred)
            CHORD_LIST[delete_nod.id] = 0
            id_M.remove(id_m)
            d_suc.after_add_del()
            d_pred.after_add_del()


if __name__ == '__main__':
    for n in id_M:
        CHORD(n)

    print('идентификаторы позиций')
    print(id_M)

    print('-----------------------')
    print('Список узлов')
    print(CHORD_LIST)

    print('-----------------------')
    print('Finger table')
    for n in id_M:
        print(CHORD_LIST[n].table)

    a = CHORD_LIST[1].find(3)

    print(a)

    print('-----------------------')
    print('Следующий узел в кольце')
    print(CHORD_LIST[3].succes)

    print('-----------------------')
    print(CHORD_LIST)
    print('Добавление')
    print(CHORD_LIST[0].add(6))
    print(CHORD_LIST)

    print(CHORD_LIST[0].delete(6))
    print(CHORD_LIST)
