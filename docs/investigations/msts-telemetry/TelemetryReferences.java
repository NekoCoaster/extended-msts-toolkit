// @category MSTS
import ghidra.app.script.GhidraScript;
import ghidra.program.model.symbol.*;
import ghidra.program.model.listing.*;
import java.io.*;
public class TelemetryReferences extends GhidraScript {
 public void run() throws Exception {
  String[] a=getScriptArgs();try(PrintWriter w=new PrintWriter(new File(a[0],"references.tsv"))){
   w.println("target\tfrom\ttype\tfunction");
   for(int i=1;i<a.length;i++)for(Reference r:getReferencesTo(toAddr(a[i]))){Function f=getFunctionContaining(r.getFromAddress());w.println(a[i]+"\t"+r.getFromAddress()+"\t"+r.getReferenceType()+"\t"+(f==null?"":f.getEntryPoint()));}
  }
 }
}
