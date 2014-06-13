# coding=utf-8
"""
This File is part of Pinyto
"""

import time
from multiprocessing import Process, Queue
from seccomp_process import SecureHost


def sandbox(code, user, queue):
    """
    This function gets executed in a separate subprocess which does not share the memory with the main
    Django process. This is done a) for security reasons to minimize the risk that code inside of the
    sandbox is able to do anything harmful and b) for cleanly measuring the execution time for the code
    because the user will have to pay for this.

    @param code: string
    @param user: User
    @param queue: Queue
    @return: nothing (the queue is used for returning the results)
    """
    start_time = time.clock()
    secure_host = SecureHost()
    secure_host.start_child()
    try:
        result = secure_host.execute(code)
    finally:
        secure_host.kill_child()
    end_time = time.clock()
    queue.put((result, end_time - start_time))


def safely_exec(code, user):
    """
    If you want to use this module call this method. It will setup a process and execute the code there
    with seccomp. Database connections will be opened for the users collection.

    @param code: string
    @param user: User
    @return: json
    """
    queue = Queue(1)
    sandbox_process = Process(target=sandbox, args=(code, user, queue))
    sandbox_process.start()
    result, execution_time = queue.get()
    sandbox_process.join()
    return result, execution_time
