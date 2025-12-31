import threading

def first(event, callback, args):
    callback(*args)
    event.set()

def second(event, callback, args):
    event.wait()
    callback(*args)