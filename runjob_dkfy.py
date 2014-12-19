#!/usr/bin/python

# Installs a workflow if it isn't already on board
# Then schedules the job, and patches the crontab

import os
import re
import popen2
import shlex
import subprocess
import sys

WORKFLOW_SEARCH=r"Workflow_Bundle_SangerPancancerCgpCnIndelSnvStr_1.0.2_SeqWare_1.1.0-alpha.5"
WORKFLOW_SWID_SEARCH="SangerPancancerCgpCnIndelSnvStr\s+Version\s+.\s+1.0.2\s+Creation Date\s+.*\s+?SeqWare Accession\s+.\s(\d)"

SCHEDULE_WORKFLOW_COMMAND="seqware workflow schedule --accession"
INI_FILE_PATH="--ini /mnt/home/seqware/ini/20141218.pilot.1.0.2.dkfz/"
INI_FILE_NAME="config.ini"
HOST_CLAUSE="--host master"

CRON_ON="*/5 * * * *  ~/crons/status_1.1.0-alpha.5.cron >> /tmp/status_1.1.0-alpha.5.cron.log"
CRON_OFF="#*/5 * * * *  ~/crons/status_1.1.0-alpha.5.cron >> /tmp/status_1.1.0-alpha.5.cron.log"

SWID_SEARCH_REGEX1=r"SWID:\s*\((\d+)\)"
SWID_SEARCH_REGEX2=r"SWID:\s*(\d+)"

def RunCommand(string, needshell=False):
    """
        Simple function that executes a system call.
        Args:
            string  The command to run.
        Returns:
            out         Stdout contents.
            err         Stderr contents.
            code        Exit code returned by the call.
    """
    p = subprocess.Popen(shlex.split(string), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=needshell)
    out, err = p.communicate()
    p.wait()
    return out, err, p.returncode

def GetSwid(string):
    match = re.search(SWID_SEARCH_REGEX1,string)
    if match:
        return match.group(1)
    else:
        match = re.search(SWID_SEARCH_REGEX2,string)
        if match:
            return match.group(1)
        else:
            return None

def isWorkflowInstalled(search_string):
    out, err, code = RunCommand("seqware workflow list")
    if code is not 0:
        print err
        sys.exit()
    if search_string in out:
        # Get Accession of existing workflow
        match = re.search(WORKFLOW_SWID_SEARCH, out)
        print "Workflow is installed already with SWID %s." % (match.group(1))
        return match.group(1)
    else:
        print "Workflow is not installed."
        sys.exit()

def main():
    install = isWorkflowInstalled(WORKFLOW_SEARCH)
    installswid = install
    UUID = raw_input("Enter the UUID of the donor to process: ")
    # ASSEMBLE COMMAND
    CMD = "%s %s %s%s/%s %s " % ( SCHEDULE_WORKFLOW_COMMAND, installswid, INI_FILE_PATH, UUID, INI_FILE_NAME, HOST_CLAUSE )
    print "Executing %s" % ( CMD )
    out, err, code = RunCommand(CMD)
    if code is not 0:
        print err
        sys.exit()
    with open(".output","w") as f:
        f.write(out)
    print "%s" % (out)
    runswid = GetSwid(out)
    
    # TURN ON CRONTAB
    with open("newcron","w") as f:
        f.write(CRON_ON)
        f.write("\n")
    out, err, code = RunCommand("crontab newcron")
    print "Crontab Turned On."
    print "watch -n 5 'seqware workflow-run report --accession %s; qstat -f'" % (runswid)

if __name__ == '__main__':
    main()
        