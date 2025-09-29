from typing import Literal

"""
Варианты загрузки связанных объектов для relationship()
Тип lazy        Когда грузится      Что возвращает
==================================================
select (def)	при обращении	    объекты
joined	        сразу (JOIN)	    объекты
subquery	    сразу (2 запроса)	объекты
selectin	    сразу (2 запроса)	объекты
dynamic	        при обращении	    Query
noload	        никогда	            пустой/None
raise	        при обращении	    ошибка
write_only	    только запись       ошибка при чтении

"""
LazyLoadArgumentType = Literal[
    "select",
    "joined",
    "selectin",
    "subquery",
    "raise",
    "raise_on_sql",
    "noload",
    "immediate",
    "write_only",
    "dynamic",
    True,
    False,
    None,
]
