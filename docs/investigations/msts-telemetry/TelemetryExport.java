// @category MSTS
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;
public class TelemetryExport extends GhidraScript {
 public void run() throws Exception {
  String[] args=getScriptArgs(); File out=new File(args[0]);out.mkdirs();
  LinkedHashSet<Function> fs=new LinkedHashSet<>();
  try(PrintWriter meta=new PrintWriter(new File(out,"program.txt"))){meta.println(currentProgram.getExecutablePath());meta.println(currentProgram.getExecutableSHA256());}
  try(PrintWriter refs=new PrintWriter(new File(out,"references.tsv"))){
   refs.println("target\tfrom\ttype\tfunction");
   for(int i=1;i<args.length;i++){
    Address a=toAddr(args[i]);if(a==null)throw new IllegalArgumentException("Invalid address: "+args[i]);Function f=getFunctionContaining(a);if(f!=null)fs.add(f);
    for(Reference r:getReferencesTo(a)){
     Function caller=getFunctionContaining(r.getFromAddress());
     refs.println(a+"\t"+r.getFromAddress()+"\t"+r.getReferenceType()+"\t"+(caller==null?"":caller.getEntryPoint()));
     if(caller!=null){fs.add(caller);
      if(caller.isThunk())for(Reference tr:getReferencesTo(caller.getEntryPoint())){
       Function tc=getFunctionContaining(tr.getFromAddress());
       refs.println(caller.getEntryPoint()+"\t"+tr.getFromAddress()+"\t"+tr.getReferenceType()+"\t"+(tc==null?"":tc.getEntryPoint()));
       if(tc!=null)fs.add(tc);
      }
     }
    }
   }
  }
  DecompInterface d=new DecompInterface();d.openProgram(currentProgram);
  try(PrintWriter index=new PrintWriter(new File(out,"functions.tsv"))){
   for(Function f:fs){if(monitor.isCancelled())break;
    DecompileResults r=d.decompileFunction(f,60,monitor);
    index.println(f.getEntryPoint()+"\t"+f.getName()+"\t"+r.decompileCompleted()+"\t"+r.getErrorMessage().replace('\n',' '));index.flush();
    if(r.decompileCompleted())try(PrintWriter w=new PrintWriter(new File(out,f.getEntryPoint()+".c"))){w.print(r.getDecompiledFunction().getC());}
    try(PrintWriter w=new PrintWriter(new File(out,f.getEntryPoint()+".asm"))){
     InstructionIterator it=currentProgram.getListing().getInstructions(f.getBody(),true);while(it.hasNext()){Instruction ins=it.next();w.println(ins.getAddress()+"  "+ins);}
    }
    try(PrintWriter w=new PrintWriter(new File(out,f.getEntryPoint()+".bytes.tsv"))){
     InstructionIterator it=currentProgram.getListing().getInstructions(f.getBody(),true);
     while(it.hasNext()){Instruction ins=it.next();StringBuilder h=new StringBuilder();for(byte b:ins.getBytes())h.append(String.format("%02x",b&255));w.println(ins.getAddress()+"\t"+h);}
    }
   }
  }finally{d.dispose();}
  println("Exported "+fs.size()+" targeted functions");
 }
}
