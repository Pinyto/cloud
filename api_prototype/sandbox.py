# coding=utf-8
"""
This File is part of Pinyto
"""

import time
from multiprocessing import Process, Queue
from multiprocessing.queues import Empty
from seccomp_process import SecureHost


def sandbox(code, db, queue):
    """
    This function gets executed in a separate subprocess which does not share the memory with the main
    Django process. This is done a) for security reasons to minimize the risk that code inside of the
    sandbox is able to do anything harmful and b) for cleanly measuring the execution time for the code
    because the user will have to pay for this.

    @param code: string
    @param db: CollectionWrapper
    @param queue: Queue
    @return: nothing (the queue is used for returning the results)
    """
    start_time = time.clock()
    secure_host = SecureHost()
    secure_host.start_child()
    try:
        result = secure_host.execute(code, db)
    finally:
        secure_host.kill_child()
    end_time = time.clock()
    queue.put((result, end_time - start_time))


def safely_exec(code, db):
    """
    If you want to use this module call this method. It will setup a process and execute the code there
    with seccomp. Database connections will be opened for the users collection.

    @param code: string
    @param db: CollectionWrapper
    @return: json
    """
    start_time = time.clock()
    queue = Queue(1)
    sandbox_process = Process(target=sandbox, args=(code, db, queue))
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
            result = {'error': "The code could not be executed because it tried to do something illegal."}
    sandbox_process.join()
    end_time = time.clock()
    return result, end_time - start_time + child_time
