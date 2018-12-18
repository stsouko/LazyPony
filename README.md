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
    
    query = A[None].select()


if schema is set in LazyEntityMeta.attach

    query = A[schema].select()

possible to attach to models multiple schemas

    db1 = Database()
    LazyEntityMeta.attach(db1, 'schema1')
    
    db2 = Database()
    LazyEntityMeta.attach(db2, 'schema2')
    
    db3 = Database()
    LazyEntityMeta.attach(db3, 'schema3')
