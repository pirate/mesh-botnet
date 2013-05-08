import sys
from StringIO import StringIO

def evaluate(cmd):
   try:
      buffer = StringIO()
      sys.stdout = buffer
      exec(cmd)
      sys.stdout = sys.__stdout__
      out = buffer.getvalue()
   except Exception as error:
      out = error
   if len(str(out).strip()) < 1:
      try:
         out += "Eval: "+str(eval(cmd))
      except Exception as error:
         out += "Eval Failed: "+str(error)
   return str(out)

print(evaluate("print 1+1"))