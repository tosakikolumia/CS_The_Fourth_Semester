`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2025/06/11 21:12:11
// Design Name: 
// Module Name: CP0_testbench
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


`timescale 1ns/1ps

module CP0_testbench;

  // Inputs
  reg clk;
  reg rst;
  reg mfc0;
  reg mtc0;
  reg [31:0] pc;
  reg [4:0] addr;
  reg [31:0] data;
  reg exception;
  reg eret;
  reg [4:0] cause;
  // Outputs
  wire [31:0] rdata;
  wire [31:0] status;
  wire [31:0] exc_addr;

  CP0 uut (
    .clk(clk),
    .rst(rst),
    .mfc0(mfc0),
    .mtc0(mtc0),
    .pc(pc),
    .addr(addr),
    .data(data),
    .exception(exception),
    .eret(eret),
    .cause(cause),
    .rdata(rdata),
    .status(status),
    .exc_addr(exc_addr)
  );

  // Clock generation
  initial begin
    clk = 0;
    forever #5 clk = ~clk;
  end

  initial begin
    
    // 初始化
    rst = 1; mfc0 = 0; mtc0 = 0; exception = 0; eret = 0;
    addr = 0; data = 0; pc = 0; cause = 0;
    #10 rst = 0;
    //测试写入和读出是否有效
    // Write to CP0 register 12 (status) using MTC0
    #10 addr = 5'd12;
        data = 32'hffff_0000;
        mtc0 = 1;
    #10 mtc0 = 0;
    //测试读出
    // Read from CP0 register 12 using MFC0
    #10 mfc0 = 1;
    #10 $display("Read CP0[12] = 0x%08h (Expect: ffff0000)", rdata);
        mfc0 = 0;
    // 进行中断
    // Trigger an exception at PC = 0x00400020 with cause = 5'b10101
    #10 pc = 32'h00400020;
        cause = 5'b10101;
        exception = 1;
    #10 exception = 0;
    //查看中断状态是否写入
    // Check EPC and cause
    //读取EPC
    #10 addr = 5'd14; mfc0 = 1; // EPC
    #10 $display("EPC = 0x%08h (Expect: 00400020)", rdata);
        mfc0 = 0;
    //读取Status
    #10 addr = 5'd13; mfc0 = 1; // cause
    #10 $display("Cause = 0x%08h (Expect: 00000054)", rdata);
        mfc0 = 0;

    // ERET instruction (return from exception)
    #10 eret = 1;
    #10 eret = 0;

    // Check updated status
    #10 addr = 5'd12; mfc0 = 1;
    #10 $display("Status after ERET = 0x%08h", rdata);
        mfc0 = 0;

    // Check exc_addr output

    #10 eret = 1;
    #10; // 等待一个时钟周期，让 CP0 有机会处理 eret
    $display("exc_addr = 0x%08h (Expect: 00400024)", exc_addr);
    eret = 0;
  end

endmodule
