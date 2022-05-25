from subprocess import Popen
import threading


def run(number, count):
    p = Popen(['python3', 'processor.py', '--id', str(number), '--shards-count', str(count)])
    print('Process: ', number, p.communicate())
    return p.communicate()


def __main__():
    process_count = 1
    threads = []
    for i in range(process_count):
        thread = threading.Thread(target=run, args=(i, process_count))
        thread.start()
        threads.append(thread)
    for t in threads:
        t.join()


__main__()