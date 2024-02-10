class GlobalFunc():
    global pcall
    
    def pcall(func):
        try:
            args = func()

            if type(args) == tuple:
                return True, *args

            return True, args
        except Exception as e:
            return False, e
