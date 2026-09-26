// @category MSTS
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.app.util.PseudoDisassembler;
import ghidra.app.util.PseudoInstruction;
import java.io.*;
public class TelemetryRange extends GhidraScript {
 public void run() throws Exception {
  String[] a=getScriptArgs();File out=new File(a[0]);out.mkdirs();
  Address begin=toAddr(a[1]),end=toAddr(a[2]);
  if(end.subtract(begin)>8192 || end.compareTo(begin)<0)throw new IllegalArgumentException("Bounded range required");
  try(PrintWriter w=new PrintWriter(new File(out,"range.asm"));PrintWriter b=new PrintWriter(new File(out,"range.bytes.tsv"))){
   PseudoDisassembler decoder=new PseudoDisassembler(currentProgram);
   for(Address at=begin;at.compareTo(end)<=0;){PseudoInstruction ins=decoder.disassemble(at);if(ins==null)throw new IllegalStateException("No decode at "+at);w.println(at+"  "+ins);StringBuilder h=new StringBuilder();for(byte x:ins.getBytes())h.append(String.format("%02x",x&255));b.println(at+"\t"+h);at=at.add(ins.getLength());}
  }
 }
}
