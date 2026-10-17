// Reference probe for PTO golden f0a876e449a95d26841c5ee7affb4c905ebc5f5b.
// Assemble with the unmodified PTO model; this is not a second ISA definition.
func main() => integer
begin
    ResetProfileState();
    WriteTPC(Zeros{PTO_XLEN} + 0x1002);
    ClearFault();

    var pcr_instruction: bits(48) = Zeros{48} + 0x00004039;
    pcr_instruction[11:7] = Zeros{5} + 3;
    pcr_instruction[31:15] = Zeros{17} + 1;
    let pcr_status = ExecuteScalarInstruction(pcr_instruction, 32);
    assert pcr_status == ScalarExecution_Rejected;
    assert _LastFault == Fault_DataPage;
    assert _FaultAddress == Zeros{PTO_XLEN} + 0x1004;

    ResetProfileState();
    WriteTPC(Zeros{PTO_XLEN} + 0x1002);
    ClearFault();

    var addtpc_instruction: bits(48) = Zeros{48} + 0x00000007;
    addtpc_instruction[11:7] = Zeros{5} + 3;
    addtpc_instruction[31:12] = Zeros{20} + 1;
    let addtpc_status = ExecuteScalarInstruction(addtpc_instruction, 32);
    assert addtpc_status == ScalarExecution_Executed;
    assert _LastFault == Fault_None;
    assert ReadGPR(3) == Zeros{PTO_XLEN} + 0x2002;
    assert ReadTPC() == Zeros{PTO_XLEN} + 0x1006;
    return 0;
end;
