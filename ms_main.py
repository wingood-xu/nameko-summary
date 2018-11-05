import signal

import eventlet

eventlet.monkey_patch()  # noqa (code before rest of imports)
from nameko.runners import ServiceRunner
import errno

from nameko.rpc import rpc

from dependency import JiebaDependency


class JiabaService(object):
    name = "jieba_service"
    model = JiebaDependency()

    @rpc
    def cut(self, text):
        return list(self.model.cut(text))


if __name__ == '__main__':
    service_runner = ServiceRunner(config={'AMQP_URI': "pyamqp://guest:guest@localhost"})
    service_runner.add_service(JiabaService)


    def shutdown(signum, frame):
        # signal handlers are run by the MAINLOOP and cannot use eventlet
        # primitives, so we have to call `stop` in a greenlet
        eventlet.spawn_n(service_runner.stop)


    service_runner.start()

    # if the signal handler fires while eventlet is waiting on a socket,
    # the __main__ greenlet gets an OSError(4) "Interrupted system call".
    # This is a side-effect of the eventlet hub mechanism. To protect nameko
    # from seeing the exception, we wrap the runner.wait call in a greenlet
    # spawned here, so that we can catch (and silence) the exception.
    runnlet = eventlet.spawn(service_runner.wait)

    while True:
        try:
            runnlet.wait()
        except OSError as exc:
            if exc.errno == errno.EINTR:
                # this is the OSError(4) caused by the signalhandler.
                # ignore and go back to waiting on the runner
                continue
            raise
        except KeyboardInterrupt:
            print()  # looks nicer with the ^C e.g. bash prints in the terminal
            try:
                service_runner.stop()
            except KeyboardInterrupt:
                print()  # as above
                service_runner.kill()
        else:
            # runner.wait completed
            break
