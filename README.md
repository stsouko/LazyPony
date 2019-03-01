Lazy load of database


example:
========

**file1.py**

    from LazyPony import LazyEntityMeta

    class A(metaclass=LazyEntityMeta):
        id = PrimaryKey(int, auto=True)


**file2.py**

    from LazyPony import LazyEntityMeta

    db = Database()
    LazyEntityMeta.attach(db)
    db.bind()
    db.generate_mapping()

**file3.py**

    from file1 import A
    
    query = A.select()
