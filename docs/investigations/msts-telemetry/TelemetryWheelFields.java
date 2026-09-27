// @category MSTS
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.scalar.Scalar;
import java.io.*;
public class TelemetryWheelFields extends GhidraScript {
 public void run() throws Exception {
  try(PrintWriter out=new PrintWriter(new File(getScriptArgs()[0],"fields.tsv"))){
   out.println("address\tfunction\tinstruction");
   InstructionIterator it=currentProgram.getListing().getInstructions(toAddr("00613000"),true);
   while(it.hasNext()&&!monitor.isCancelled()){
    Instruction ins=it.next();if(ins.getAddress().compareTo(toAddr("00640000"))>=0)break;
    boolean hit=false;
    for(int i=0;i<ins.getNumOperands();i++)for(Object obj:ins.getOpObjects(i))
     if(obj instanceof Scalar){long v=((Scalar)obj).getSignedValue();if(getScriptArgs().length>1){for(int j=1;j<getScriptArgs().length;j++)if(v==Long.parseLong(getScriptArgs()[j],16))hit=true;}else if(v==0x1dc||v==0x4e8||v==0x112||v==0x11a)hit=true;}
    if(hit){Function f=getFunctionContaining(ins.getAddress());out.println(ins.getAddress()+"\t"+(f==null?"":f.getEntryPoint())+"\t"+ins);}
   }
  }
 }
}
