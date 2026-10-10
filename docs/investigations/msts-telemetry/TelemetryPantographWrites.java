// @category MSTS
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.scalar.Scalar;
import java.io.*;
public class TelemetryPantographWrites extends GhidraScript {
 public void run() throws Exception {
  try(PrintWriter out=new PrintWriter(new File(getScriptArgs()[0],"pantograph-offset-writes.tsv"))){
   out.println("address\tfunction\tinstruction");
   InstructionIterator it=currentProgram.getListing().getInstructions(true);
   while(it.hasNext()&&!monitor.isCancelled()){
    Instruction ins=it.next();String m=ins.getMnemonicString();
    if(!(m.equals("FSTP")||m.equals("FST")||m.equals("MOV")||m.equals("AND")||m.equals("OR")||m.equals("XOR")||m.equals("INC")||m.equals("DEC")||m.equals("ADD")||m.equals("SUB")))continue;
    boolean hit=false;
    for(Object o:ins.getOpObjects(0))if(o instanceof Scalar){long v=((Scalar)o).getSignedValue();if(v==0x410||v==0x450)hit=true;}
    if(hit&&ins.getDefaultOperandRepresentation(0).contains("[")){
     Function f=getFunctionContaining(ins.getAddress());out.println(ins.getAddress()+"\t"+(f==null?"":f.getEntryPoint())+"\t"+ins);
    }
   }
  }
 }
}
