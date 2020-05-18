

class Vector:
    def __init__(self, position, scale):
        self.position = position if position is not None else (0, 0)
        self.scale = scale if position is not None else 1
        self.visible = True
        self.children = []

    def render(self):
        """"""

    def render_children(self):
        for child in self.children:
            child.render()

class Behavior:
    def __init__(self):
        """"""

    def update(self):
        """"""
