#!/usr/bin/env python

import sys, os
import subprocess

class Test(object):
    def __init__(self, input="", output="", desc="", tool="python"):
        self.desc = desc
        self.input = input
        self.output = output
        self.tool = tool

    def trim(self):
        self.desc = self.desc.strip()
        self.input = self.input.strip()
        self.output = self.output.strip()
        self.tool = self.tool.strip()

    def run(self):
        if not self.input: return
        cmd = subprocess.Popen(self.tool.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = cmd.communicate(self.input)

        if out.strip() == self.output:
            print ".", self.desc
            return True
        else:
            print "F", self.desc
            print "===== Output: ====="
            print out.strip()
            print "===== Error: ======"
            print err.strip()
            print "==================="
            return False

def parsetests(strtests):
    tests = []
    curr = Test()
    
    for s in strtests.split("\n"):
        if len(s) == 0: continue

        if s[0] == "#" and s[1] != " ":
            s = s[1:]
            if s[:1] == "!":
                tests.append(curr)
                curr = Test(tool=s[1:].strip())
            elif s[:1] == "#":
                continue
        elif s[:2] == "# ":
            if curr.input:
                tests.append(curr)
                curr = Test(desc=s[2:].strip(), tool=curr.tool)
            else:
                curr.desc += "\n" + s[1:].strip()
        elif s[:4] == ">>> ":
            if curr.output:
                tests.append(curr)
                curr = Test(input=s[4:], tool=curr.tool)
            else:
                curr.input += "\n" + s[4:]
        else:
            curr.output += "\n" + s

    tests.append(curr)
    return tests

def run(l):
    tot = 0
    failed = 0
    
    for test in l:
        test.trim()
        
        tot += 1
        if not test.run(): failed += 1

    tot -= 1
    failed -= 1
    
    print "Failed %d out of %d" % (failed, tot)

    return failed

def run_file(f):
    if os.path.isdir(f):
        t = []
        for i in filter(os.path.isfile, map(lambda x: os.path.join(f, x), os.listdir(f))):
            r = run_file(i)
            if r > 0:
                t.append((i, r))

        sum = 0
        for i in t:
            sum += i[1]

        print
        print sum, "total failures"
        for i in t:
            print "Failed %d tests in %s" % (i[1], i[0])
        
        return t
    else:
        f = open(f)
        return run(parsetests(f.read()))

if __name__ == "__main__":
    if len(sys.argv) == 1:
        try:
            while 1:
                run_file(raw_input("Tests File? "))
        except (KeyboardInterrupt, EOFError):
            pass
    else:
        for i in sys.argv[1:]:
            run_file(i)
