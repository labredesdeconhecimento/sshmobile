import paramiko

class MySSHClient(SSHClient): 
    ## overload the exec_command method 
    def exec_command(self, command, bufsize=-1, timeout=None): 
        chan = self._transport.open_session() 
        chan.settimeout(timeout) 
        chan.exec_command(command) 
        stdin = chan.makefile('wb', bufsize) 
        stdout = chan.makefile('rb', bufsize) 
        stderr = chan.makefile_stderr('rb', bufsize) 
        return stdin, stdout, stderr 
