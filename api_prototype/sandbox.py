# coding=utf-8
"""
This File is part of Pinyto
"""

import time
from multiprocessing import Process, Queue
from multiprocessing.queues import Empty
from api_prototype.seccomp_process import SecureHost


def sandbox(code, request, real_db, queue):
    """
    This function gets executed in a separate subprocess which does not share the memory with the main
    Django process. This is done a) for security reasons to minimize the risk that code inside of the
    sandbox is able to do anything harmful and b) for cleanly measuring the execution time for the code
    because the user may have to pay for it.

    :param code: The python code which should be executed in the sandbox
    :type code: str
    :param request: Django's request object
    :type request: HttpRequest
    :param real_db: The database connection
    :type real_db: service.database.CollectionWrapper
    :param queue: Queue for communicating with the main process
    :type queue: multiprocessing.Queue
    :return: nothing (the queue is used for returning the results)
    """
    start_time = time.clock()
    secure_host = SecureHost()
    secure_host.start_child()
    try:
        result = secure_host.execute(code, request, real_db)
    finally:
        secure_host.kill_child()
    end_time = time.clock()
    queue.put((result, end_time - start_time))


def safely_exec(code, request, db):
    """
    If you want to execute something in the sandbox, call this method.
    It will setup a process and execute the code there with seccomp. The passed database connections
    will used to access the users collection.

    :param code: The python code which should be executed in the sandbox
    :type code: str
    :param request: Django's request object which is passed into the sandbox process
    :type request: HttpRequest
    :param db: The already opened database connection
    :type db: service.database.CollectionWrapper
    :return: A tuple containing the result and the time needed to calculate the result.
    :rtype: (dict, timedelta)
    """
    start_time = time.clock()
    queue = Queue(1)
    sandbox_process = Process(target=sandbox, args=(code, request, db, queue))
    sandbox_process.start()
    result = ""
    child_time = 0
    wait_for_data = True
    termination = False
    while wait_for_data and not termination:
        try:
            result, child_time = queue.get(True, 0.001)
            wait_for_data = False
        except Empty:
            wait_for_data = True
        if not sandbox_process.is_alive():
            termination = True
            result = {u'error': u"The code could not be executed because it tried to do something illegal."}
    sandbox_process.join()
    end_time = time.clock()
    return result, end_time - start_time + child_time
