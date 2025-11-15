`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2025/04/10 18:50:01
// Design Name: 
// Module Name: DIVU_tb
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


`timescale 1ns / 1ps

module DIVU_tb();

    // 定义模块输入输出信号
    reg [31:0] dividend;
    reg [31:0] divisor;
    reg start;
    reg clock;
    reg reset;
    wire [31:0] q;
    wire [31:0] r;
    wire busy;

    // 实例化除法器模块
    DIVU uut (
        .dividend(dividend),
        .divisor(divisor),
        .start(start),
        .clock(clock),
        .reset(reset),
        .q(q),
        .r(r),
        .busy(busy)
    );

    // 生成时钟信号
    initial begin
        clock = 0;
        forever #2 clock = ~clock; // 10ns周期的时钟信�?
    end

    // 测试过程
    initial begin
        clock = 0;
        reset = 1;
        start = 0;
        #10;
        reset = 0;
        dividend = 32'h0000000A; // 10  
        divisor = 32'h00000002;  // 2  
        start = 1;   // 结果应为5
        #10;
        start = 0;
        #150;
        
        reset = 1;
        #10;
        reset = 0;
        dividend = 32'h00000000; // 0  
        divisor = 32'hffffffff;  // 4294967295  
        start = 1;   // 结果应为0
        #10;
        start = 0;
        #150;
        
        reset = 1;
        #10;
        reset = 0;
        dividend = 32'h00000014; // 20  
        divisor = 32'h00000003;  // 3  
        start = 1;   // 结果应为1�?0.5
        #10;
        start = 0;
        #150;
        
        reset = 1;
        #10;
        reset = 0;
        dividend = 32'haaaaaaaa; // 2863311530  
        divisor = 32'h55555555;  // 1431655765
        start = 1;   // 结果应为2
        #10;
        start = 0;
        #150;
        
        reset = 1;
        #10;
        reset = 0;
        dividend = 32'h55555555; // 1431655765 
        divisor = 32'h7fffffff;  // 2147483647  
        start = 1;   // 结果应该�?0
        #10;
        start = 0;
        #150;
        
        reset = 1;
        #10;
        reset = 0;
    end

endmodule