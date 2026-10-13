// @category MSTS
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import java.io.*;
public class TelemetryAnimationIndex extends GhidraScript {
 public void run() throws Exception {
  try(PrintWriter out=new PrintWriter(new File(getScriptArgs()[0],"functions.tsv"))){
   FunctionIterator it=currentProgram.getFunctionManager().getFunctions(toAddr("006d5000"),true);
   while(it.hasNext()&&!monitor.isCancelled()){
    Function f=it.next();if(f.getEntryPoint().compareTo(toAddr("006d5b50"))>=0)break;
    out.println(f.getEntryPoint()+"\t"+f.getName()+"\t"+f.getBody().getNumAddresses());
   }
  }
 }
}
