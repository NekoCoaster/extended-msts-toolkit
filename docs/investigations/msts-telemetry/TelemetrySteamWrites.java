// @category MSTS
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.scalar.Scalar;
import java.io.*;
public class TelemetrySteamWrites extends GhidraScript {
 public void run() throws Exception {
  try(PrintWriter out=new PrintWriter(new File(getScriptArgs()[0],"steam-offset-writes.tsv"))){
   out.println("address\tfunction\tinstruction");
   InstructionIterator it=currentProgram.getListing().getInstructions(true);
   while(it.hasNext()&&!monitor.isCancelled()){
    Instruction ins=it.next();String m=ins.getMnemonicString();
    if(!(m.equals("FSTP")||m.equals("FST")||m.equals("MOV")))continue;
    boolean hit=false;
    for(Object o:ins.getOpObjects(0))if(o instanceof Scalar){long v=((Scalar)o).getSignedValue();if(v==0x316||v==0x312||v==0x2c2||v==0x32e)hit=true;}
    if(hit&&ins.getDefaultOperandRepresentation(0).contains("[")){
     Function f=getFunctionContaining(ins.getAddress());out.println(ins.getAddress()+"\t"+(f==null?"":f.getEntryPoint())+"\t"+ins);
    }
   }
  }
 }
}
