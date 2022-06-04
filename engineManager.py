class rObject():
    def __init__(self):
        pass
    def draw(self):
        pass
    def render(self):
        self.draw()

class engineManager():
    def __init__(self, objs: list[rObject]):
        self.objs = objs

    def addObject(self, obj: rObject):
        self.objs.append(obj)    

    def update(self):
        for obj in self.objs:
            obj.render()
