// @category MSTS
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.scalar.Scalar;
import java.io.*;

/** Lexical scalar navigation only; does not prove ownership or execution. */
public class TelemetryScalarReferences extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        long target = Long.decode(args[1]);
        try (PrintWriter out = new PrintWriter(new File(args[0], "scalar-references.tsv"))) {
            out.println("address\tfunction\tinstruction");
            InstructionIterator iter = currentProgram.getListing().getInstructions(true);
            while (iter.hasNext() && !monitor.isCancelled()) {
                Instruction ins = iter.next();
                boolean hit = false;
                for (int operand = 0; operand < ins.getNumOperands(); operand++) {
                    for (Object object : ins.getOpObjects(operand)) {
                        if (object instanceof Scalar && ((Scalar)object).getUnsignedValue() == target) hit = true;
                    }
                }
                if (hit) {
                    Function function = getFunctionContaining(ins.getAddress());
                    out.println(ins.getAddress() + "\t" + (function == null ? "" : function.getEntryPoint()) + "\t" + ins);
                }
            }
            if (monitor.isCancelled()) throw new IOException("Scalar scan cancelled; output incomplete");
        }
    }
}
