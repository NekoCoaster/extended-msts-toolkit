// @category MSTS
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.scalar.Scalar;
import java.io.*;
public class TelemetryInfrastructureWrites extends GhidraScript {
 public void run() throws Exception {
  try(PrintWriter out=new PrintWriter(new File(getScriptArgs()[0],"writes.tsv"))){
   out.println("address\tfunction\tinstruction");
   InstructionIterator it=currentProgram.getListing().getInstructions(toAddr("00590000"),true);
   while(it.hasNext()&&!monitor.isCancelled()){
    Instruction ins=it.next();if(ins.getAddress().compareTo(toAddr("005d2000"))>=0)break;
    if(!ins.getMnemonicString().equals("MOV")||!ins.getDefaultOperandRepresentation(0).contains("["))continue;
    boolean hit=false;
    for(Object obj:ins.getOpObjects(0))if(obj instanceof Scalar){long v=((Scalar)obj).getSignedValue();if(v==0x58||v==0x38||v==0x35||v==0x24)hit=true;}
    if(hit){Function f=getFunctionContaining(ins.getAddress());out.println(ins.getAddress()+"\t"+(f==null?"":f.getEntryPoint())+"\t"+ins);}
   }
  }
 }
}
